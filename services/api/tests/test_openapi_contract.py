from app.main import app


def test_openapi_includes_moderation_reason_code_schema():
    schema = app.openapi()

    reason_code = schema["components"]["schemas"].get("ModerationReasonCode")
    assert reason_code is not None
    assert reason_code["type"] == "string"
    assert set(reason_code["enum"]) == {
        "BLOCKED_WORD",
        "TOO_MANY_LINKS",
        "DUPLICATE_CONTENT",
        "TOO_MANY_MEDIA",
    }


def test_openapi_includes_role_based_publish_endpoints():
    schema = app.openapi()
    publish_op = schema["paths"].get("/posts/{post_id}/publish", {}).get("post")

    assert publish_op is not None
    assert "admin" in publish_op["description"].lower()
    assert "editor" in publish_op["description"].lower()
    assert "403" in publish_op["responses"]

    response_schema = (
        publish_op["responses"]["200"]["content"]["application/json"]["schema"]
    )
    assert response_schema["$ref"].endswith("/PublishPostResponse")
