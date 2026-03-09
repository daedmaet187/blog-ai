import asyncio
import hashlib
import hmac
import json
import os
from pathlib import Path

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.db import Base
from app.models import Project, ProjectDeployRequest, User
from app.project_state import ProjectState
from app.routers.admin import map_project_domain
from app.routers.payments import create_final_payment_session, wayl_webhook
from app.schemas import FinalPaymentSessionCreate


class _FakeRequest:
    def __init__(self, payload: bytes, headers: dict[str, str]):
        self._payload = payload
        self.headers = headers

    async def body(self) -> bytes:
        return self._payload


def _make_db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_final_payment_handoff.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}, future=True
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _make_user(db: Session, email: str, role: str) -> User:
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_project(db: Session, user_id: int, state: str) -> Project:
    project = Project(
        client_user_id=user_id,
        title="Final Payment Project",
        package="growth",
        brief_en="Deploy and hand off with custom domain once all payments are completed.",
        brief_ar="قم بالنشر والتسليم مع نطاق مخصص بعد اكتمال جميع الدفعات.",
        state=state,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def _make_deploy_request(db: Session, project_id: int) -> ProjectDeployRequest:
    record = ProjectDeployRequest(
        project_id=project_id,
        preview_url=f"https://preview.local/projects/{project_id}",
        status="deploy_approved",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def test_domain_mapping_is_blocked_until_final_payment_success(monkeypatch, tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        client = _make_user(db, "client+final@example.com", "client")
        admin = _make_user(db, "admin+final@example.com", "admin")
        project = _make_project(db, client.id, ProjectState.DEPLOY_APPROVED.value)
        _make_deploy_request(db, project.id)

        with pytest.raises(HTTPException) as blocked:
            map_project_domain(project_id=project.id, user=admin, db=db)
        assert blocked.value.status_code == 409
        assert blocked.value.detail == "Final payment is required before domain mapping"

        def _fake_create_final(self, *, project_id: int, title: str, package: str):
            assert project_id == project.id
            return {
                "session_id": "final_sess_123",
                "checkout_url": "https://pay.wayl.io/checkout/final_sess_123",
            }

        monkeypatch.setattr(
            "app.payments.wayl_client.WaylClient.create_final_payment_session",
            _fake_create_final,
        )

        final_session = create_final_payment_session(
            FinalPaymentSessionCreate(project_id=project.id),
            user=client,
            db=db,
        )
        assert final_session.project_id == project.id
        assert final_session.state == ProjectState.DEPLOY_APPROVED.value
        assert final_session.session_id == "final_sess_123"

        os.environ["WAYL_WEBHOOK_SECRET"] = "secret"
        payload = {
            "status": "success",
            "metadata": {"project_id": project.id, "payment_stage": "final"},
        }
        body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(b"secret", body, hashlib.sha256).hexdigest()
        request = _FakeRequest(body, {"X-Wayl-Signature": signature})

        response = asyncio.run(wayl_webhook(request, db))
        assert response == {"ok": True}

        db.refresh(project)
        assert project.state == ProjectState.DELIVERED.value

        mapped = map_project_domain(project_id=project.id, user=admin, db=db)
        assert mapped.project_id == project.id
        assert mapped.state == ProjectState.DELIVERED.value
        assert mapped.deploy_status == "domain_mapped"
        assert mapped.domain == f"project-{project.id}.launch.local"
    finally:
        db.close()
