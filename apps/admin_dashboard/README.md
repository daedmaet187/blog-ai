# Admin Dashboard

Simple static admin UI connected to `https://api.stuff187.com`.

## Features
- Login using `/auth/login`
- Create/edit draft post
- Publish or unpublish posts
- Review moderation queue (`/moderation/queue`)
- Override moderation decision (approve/reject) with optional note
- Reason codes are shown as `CODE + human label` chips for clarity

Token is stored in `localStorage` for quick testing.
