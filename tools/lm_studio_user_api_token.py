#!/usr/bin/env python3
"""Resolve the persistent LM Studio API token without exposing it to logs."""

from __future__ import annotations

import os
import sys


TOKEN_ENVIRONMENT_NAME = "LM_API_TOKEN"


def resolve_token() -> str:
    """Return the process token or its persistent Windows user-environment value."""
    token = os.environ.get(TOKEN_ENVIRONMENT_NAME, "").strip()
    if token:
        return token
    if os.name != "nt":
        raise RuntimeError(f"{TOKEN_ENVIRONMENT_NAME} is not configured")

    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            stored, _ = winreg.QueryValueEx(key, TOKEN_ENVIRONMENT_NAME)
    except FileNotFoundError as exc:
        raise RuntimeError(f"{TOKEN_ENVIRONMENT_NAME} is not configured") from exc
    if not isinstance(stored, str) or not stored.strip():
        raise RuntimeError(f"{TOKEN_ENVIRONMENT_NAME} is not configured")
    return stored.strip()


def main() -> int:
    try:
        token = resolve_token()
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
