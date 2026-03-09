import os
import sys

REQUIRED = [
    "DATABASE_URL",
    "JWT_SECRET",
    "WAYL_API_KEY",
    "WAYL_WEBHOOK_SECRET",
    "GITHUB_TOKEN",
    "GITHUB_OWNER",
]


def main() -> int:
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        print("Missing required env vars:")
        for k in missing:
            print(f"- {k}")
        return 1

    db = os.getenv("DATABASE_URL", "")
    if not (db.startswith("postgresql://") or db.startswith("postgresql+psycopg://")):
        print("DATABASE_URL must be postgres for production")
        return 1

    print("Preflight OK: required env present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
