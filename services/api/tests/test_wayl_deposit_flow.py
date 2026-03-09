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
from app.models import Project, User
from app.project_state import ProjectState
from app.routers.payments import create_deposit_session, wayl_webhook
from app.schemas import DepositSessionCreate


class _FakeRequest:
    def __init__(self, payload: bytes, headers: dict[str, str]):
        self._payload = payload
        self.headers = headers

    async def body(self) -> bytes:
        return self._payload


def _make_db_session(tmp_path: Path) -> Session:
    db_file = tmp_path / "test_wayl_deposit.db"
    engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}, future=True
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _make_user(db: Session, email: str = "client@example.com") -> User:
    user = User(
        email=email,
        password_hash=hash_password("password123"),
        role="client",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _make_project(db: Session, user_id: int, state: str = "submitted") -> Project:
    project = Project(
        client_user_id=user_id,
        title="Landing Page",
        package="starter",
        brief_en="Build a clean conversion-focused landing page for my startup.",
        brief_ar="أنشئ صفحة هبوط نظيفة تركز على التحويل لشركتي الناشئة.",
        state=state,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_create_deposit_session_sets_project_to_pending_and_returns_checkout(monkeypatch, tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        user = _make_user(db)
        project = _make_project(db, user.id, state=ProjectState.SUBMITTED.value)

        def _fake_create_deposit_session(self, *, project_id: int, title: str, package: str):
            assert project_id == project.id
            return {
                "session_id": "sess_123",
                "checkout_url": "https://pay.wayl.io/checkout/sess_123",
            }

        monkeypatch.setattr(
            "app.payments.wayl_client.WaylClient.create_deposit_session",
            _fake_create_deposit_session,
        )

        out = create_deposit_session(
            DepositSessionCreate(project_id=project.id),
            user=user,
            db=db,
        )

        db.refresh(project)
        assert project.state == ProjectState.DEPOSIT_PENDING.value
        assert out.project_id == project.id
        assert out.session_id == "sess_123"
        assert out.checkout_url.endswith("sess_123")
    finally:
        db.close()


def test_verified_success_webhook_transitions_pending_to_paid(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        user = _make_user(db)
        project = _make_project(db, user.id, state=ProjectState.DEPOSIT_PENDING.value)
        os.environ["WAYL_WEBHOOK_SECRET"] = "secret"

        payload = {
            "status": "success",
            "metadata": {"project_id": project.id},
        }
        body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(b"secret", body, hashlib.sha256).hexdigest()

        request = _FakeRequest(body, {"X-Wayl-Signature": signature})
        response = asyncio.run(wayl_webhook(request, db))

        assert response == {"ok": True}
        db.refresh(project)
        assert project.state == ProjectState.DEPOSIT_PAID.value
    finally:
        db.close()


def test_invalid_signature_webhook_does_not_transition(tmp_path: Path):
    db = _make_db_session(tmp_path)
    try:
        user = _make_user(db)
        project = _make_project(db, user.id, state=ProjectState.DEPOSIT_PENDING.value)
        os.environ["WAYL_WEBHOOK_SECRET"] = "secret"

        body = json.dumps({"status": "success", "metadata": {"project_id": project.id}}).encode("utf-8")
        request = _FakeRequest(body, {"X-Wayl-Signature": "bad-signature"})

        with pytest.raises(HTTPException) as exc:
            asyncio.run(wayl_webhook(request, db))

        assert exc.value.status_code == 401
        db.refresh(project)
        assert project.state == ProjectState.DEPOSIT_PENDING.value
    finally:
        db.close()
