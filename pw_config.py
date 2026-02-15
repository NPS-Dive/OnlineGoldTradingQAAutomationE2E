# playwright.config.py
# Lightweight config to make test runs consistent and debuggable.

import os
from dotenv import load_dotenv

load_dotenv()

# A place to keep shared settings for tests.
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

PW = {
    "base_url": BASE_URL,
    "headless": os.getenv("HEADLESS", "true").lower() == "true",
    "slow_mo_ms": int(os.getenv("SLOW_MO_MS", "0")),
    "timeout_ms": int(os.getenv("TIMEOUT_MS", "30000")),
}
