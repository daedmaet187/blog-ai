# Beta API Contracts v1 (Task 1)

This document locks the beta API contract for moderation reason codes and publish flow RBAC.

## Moderation Reason Schema

Reason code enum (`ModerationReasonCode`):

- `BLOCKED_WORD`
- `TOO_MANY_LINKS`
- `DUPLICATE_CONTENT`
- `TOO_MANY_MEDIA`

Decision enum (`ModerationDecision`):

- `PASS`
- `FLAG`

Moderation object:

```json
{
  "decision": "PASS",
  "reasons": []
}
```

Example flagged moderation object:

```json
{
  "decision": "FLAG",
  "reasons": ["BLOCKED_WORD", "TOO_MANY_LINKS"]
}
```

## Publish Endpoint Contract

Endpoint: `POST /posts/{post_id}/publish`

Role access:

- Allowed: `admin`, `editor`
- Denied: all other roles (`403 Forbidden`)

Success response (`200`):

```json
{
  "post": {
    "id": 123,
    "title": "Beta launch prep",
    "slug": "beta-launch-prep",
    "content": "Final checklist",
    "status": "published",
    "author_id": 5,
    "created_at": "2026-03-09T19:00:00Z",
    "updated_at": "2026-03-09T19:10:00Z"
  },
  "moderation": {
    "decision": "PASS",
    "reasons": []
  }
}
```

Forbidden response (`403`):

```json
{
  "detail": "Forbidden"
}
```
