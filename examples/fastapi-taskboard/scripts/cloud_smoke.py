"""Run only against an API you control; creates two throwaway accounts."""
import os

import httpx

from smoke import smoke

if __name__ == "__main__":
    base = os.environ["API_BASE_URL"].rstrip("/")
    if not base.startswith("https://"):
        raise SystemExit("API_BASE_URL must be your public HTTPS service URL")
    with httpx.Client(base_url=base, timeout=20) as client:
        smoke(client)
    print("Cloud smoke passed (two throwaway accounts remain).")
