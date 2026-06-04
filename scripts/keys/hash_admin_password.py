from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.auth_service import hash_password


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a PBKDF2 ADMIN_PASSWORD value.")
    parser.add_argument("--password", help="Password to hash. Omit to use ADMIN_PASSWORD_INPUT or a hidden prompt.")
    args = parser.parse_args()

    password = args.password or os.getenv("ADMIN_PASSWORD_INPUT")
    if not password:
        password = getpass.getpass("Admin password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.", file=sys.stderr)
            return 1
    if len(password) < 12:
        print("Admin password should be at least 12 characters.", file=sys.stderr)
        return 1

    print("ADMIN_PASSWORD=" + hash_password(password))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
