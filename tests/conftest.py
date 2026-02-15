# tests/conftest.py
# Pytest fixtures + JSON reporting hooks (per-test + per-run + cumulative history)
#
# What this file does (high-level):
# 1) Ensures project root is on sys.path so imports work reliably (Option B).
# 2) Loads environment variables from .env (BASE_URL, TEST_USER, TEST_PASS, HEADLESS, ...).
# 3) Provides Playwright + Pytest fixtures:
#    - browser (session-scoped)
#    - context/page (function-scoped isolation)
#    - logged_in_page (reusable login entry point)
# 4) Adds a reporting system:
#    - reports/runs/<run_id>.json           -> one JSON per run (all tests)
#    - reports/tests/<test_nodeid>.json     -> one JSON per test (cumulative array)
#    - reports/history.jsonl               -> global append-only history (one line per test execution)
#
# Important:
# - This file also does a pre-flight check to avoid ugly crashes:
#   - If BASE_URL is unreachable: tests are skipped with a clear reason (professional behavior).
#   - If TEST_USER / TEST_PASS missing: tests are skipped with a clear reason.

import os
import sys
import json
import socket
import platform
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# --------------------------------------------------------------------------------------
# 1) Ensure project root is importable (Option B)
# --------------------------------------------------------------------------------------
# This allows imports like: `from pw_config import PW` even when tests are executed from within /tests.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# --------------------------------------------------------------------------------------
# 2) Load .env early (before reading PW or credentials)
# --------------------------------------------------------------------------------------
# If you have a `.env` file in the project root, load_dotenv() will pick it up.
# If you keep `.env` elsewhere, you can pass an explicit path: load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

from pw_config import PW  # noqa: E402 (import after sys.path + dotenv is intentional)
from pages.login_page import LoginPage  # noqa: E402

# --------------------------------------------------------------------------------------
# 3) Helpers for JSON reporting
# --------------------------------------------------------------------------------------

# We'll store pytest config globally so that we can access it in hooks safely.
_PYTEST_CONFIG = None


def _now_ist():
    """Return datetime in IST (Asia/Kolkata, +05:30)."""
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist)


def _now_iso_ist() -> str:
    """ISO timestamp for logs (allowed to contain ':' because it's inside JSON)."""
    return _now_ist().isoformat(timespec="seconds")


def _run_file_stamp() -> str:
    """
    Filename-safe timestamp for Windows file names.
    Example: 2026-02-16T004911+0530
    (No ':' characters because Windows forbids ':' in file names.)
    """
    dt = _now_ist()
    return dt.strftime("%Y-%m-%dT%H%M%S%z")


def _safe_filename(text: str) -> str:
    """Convert a pytest nodeid to a filesystem-safe filename."""
    safe = text.replace("/", "__").replace("\\", "__").replace("::", "__")
    safe = safe.replace("[", "_").replace("]", "_").replace(" ", "_")
    safe = safe.replace(":", "_")
    return safe


def _ensure_dir(path: Path) -> None:
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def _append_json_array(file_path: Path, record: dict) -> None:
    """
    Append `record` to a JSON file that stores a LIST of records.
    - If file doesn't exist: create it.
    - If file exists but is corrupted / not a list: start fresh.
    """
    if file_path.exists():
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                data = []
        except Exception:
            data = []
    else:
        data = []

    data.append(record)
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _append_jsonl(file_path: Path, record: dict) -> None:
    """
    Append one JSON record per line (JSONL).
    Great for cumulative logging without rewriting large arrays each run.
    """
    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------------------
# 4) Environment pre-flight checks (stability + professional behavior)
# --------------------------------------------------------------------------------------

def _is_reachable(url: str, timeout_seconds: float = 2.0) -> bool:
    """
    Basic reachability check to prevent net::ERR_CONNECTION_REFUSED surprises.
    - Parses hostname + port from BASE_URL
    - Attempts TCP connection
    """
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            return False

        port = parsed.port
        if port is None:
            port = 443 if parsed.scheme == "https" else 80

        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except Exception:
        return False


# --------------------------------------------------------------------------------------
# 5) Fixtures (Playwright lifecycle + test isolation)
# --------------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def base_url():
    """
    Base URL of the AUT (application under test).
    Comes from pw_config -> env var BASE_URL (with a fallback).
    """
    return PW["base_url"]


@pytest.fixture(scope="session")
def credentials():
    """
    Credentials come from .env (TEST_USER, TEST_PASS).
    If missing, tests will be skipped (see logged_in_page fixture).
    """
    return {
        "username": os.getenv("TEST_USER", "").strip(),
        "password": os.getenv("TEST_PASS", "").strip(),
    }


@pytest.fixture(scope="session")
def playwright():
    """Create one Playwright instance per test session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright):
    """
    Launch one browser for the whole test session (faster).
    Tests are still isolated because we create a NEW context per test.
    """
    browser = playwright.chromium.launch(
        headless=PW["headless"],
        slow_mo=PW["slow_mo_ms"],
    )
    yield browser
    browser.close()


@pytest.fixture()
def context(browser):
    """
    Create a fresh browser context per test.
    This isolates cookies/storage/session to prevent test-to-test leakage.
    """
    ctx = browser.new_context()
    yield ctx
    ctx.close()


@pytest.fixture()
def page(context):
    """Create a new page per test."""
    p = context.new_page()
    p.set_default_timeout(PW["timeout_ms"])
    yield p
    p.close()


@pytest.fixture()
def logged_in_page(page, base_url, credentials):
    """
    Shared entry point for tests:
    1) Pre-check BASE_URL reachability
    2) Pre-check credentials exist
    3) Navigate to BASE_URL
    4) Login
    """
    # Pre-flight: is the environment up?
    if not _is_reachable(base_url):
        pytest.skip(
            f"BASE_URL not reachable: {base_url}. "
            f"Start your local app (if using localhost) or set BASE_URL to a reachable staging/demo URL."
        )

    # Pre-flight: do we have credentials?
    if not credentials["username"] or not credentials["password"]:
        pytest.skip("Missing TEST_USER/TEST_PASS in .env. Please set them before running UI tests.")

    page.goto(base_url)

    login = LoginPage(page)
    login.login(credentials["username"], credentials["password"])

    return page


# --------------------------------------------------------------------------------------
# 6) Pytest hooks for reporting (per-test + per-run + cumulative)
# --------------------------------------------------------------------------------------

def pytest_configure(config):
    """
    Called once at start of session.
    - Create run metadata
    - Create report folders
    """
    global _PYTEST_CONFIG
    _PYTEST_CONFIG = config

    config._run_started_at = _now_iso_ist()
    config._run_stamp = _run_file_stamp()
    config._run_id = f"run_{config._run_stamp}"
    config._results = []

    root = Path.cwd()
    config._reports_dir = root / "reports"
    config._reports_runs_dir = config._reports_dir / "runs"
    config._reports_tests_dir = config._reports_dir / "tests"
    config._reports_history_jsonl = config._reports_dir / "history.jsonl"

    _ensure_dir(config._reports_runs_dir)
    _ensure_dir(config._reports_tests_dir)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture setup/call/teardown reports and attach to test item.
    We'll create a single final record after teardown.
    """
    outcome = yield
    rep = outcome.get_result()

    if not hasattr(item, "_rep_by_phase"):
        item._rep_by_phase = {}

    item._rep_by_phase[rep.when] = rep


def pytest_runtest_teardown(item, nextitem):
    """
    Called after each test teardown.
    At this point we can safely produce ONE final record per test.
    """
    global _PYTEST_CONFIG
    config = _PYTEST_CONFIG
    if config is None:
        return  # avoid crashing test run

    reps = getattr(item, "_rep_by_phase", {})
    rep_setup = reps.get("setup")
    rep_call = reps.get("call")
    rep_teardown = reps.get("teardown")

    def _phase_outcome(rep):
        return getattr(rep, "outcome", None) if rep else None

    # Final outcome priority:
    # setup failed > call failed > teardown failed > skipped > passed
    final_outcome = "passed"
    if _phase_outcome(rep_setup) == "failed":
        final_outcome = "failed"
    elif _phase_outcome(rep_call) == "failed":
        final_outcome = "failed"
    elif _phase_outcome(rep_teardown) == "failed":
        final_outcome = "failed"
    elif _phase_outcome(rep_setup) == "skipped" or _phase_outcome(rep_call) == "skipped":
        final_outcome = "skipped"

    # Total duration = sum of all phases we have
    total_duration = 0.0
    for r in (rep_setup, rep_call, rep_teardown):
        if r and getattr(r, "duration", None) is not None:
            total_duration += float(r.duration)

    # Error details: prefer call error, then setup, then teardown
    error_text = None
    if final_outcome == "failed":
        for r in (rep_call, rep_setup, rep_teardown):
            if r and getattr(r, "outcome", None) == "failed":
                try:
                    error_text = str(r.longrepr)
                except Exception:
                    error_text = "Test failed (unable to stringify longrepr)."
                break

    record = {
        "run_id": getattr(config, "_run_id", "unknown_run"),
        "run_started_at": getattr(config, "_run_started_at", None),
        "recorded_at": _now_iso_ist(),
        "nodeid": item.nodeid,
        "outcome": final_outcome,
        "duration_seconds": round(total_duration, 6),
        "error": error_text,
        "environment": {
            "base_url": os.getenv("BASE_URL", ""),
            "headless": os.getenv("HEADLESS", "true"),
            "python": platform.python_version(),
            "os": platform.platform(),
        },
    }

    # 1) Save into in-memory list for the run summary
    config._results.append(record)

    # 2) Per-test cumulative JSON array file
    per_test_file = config._reports_tests_dir / f"{_safe_filename(item.nodeid)}.json"
    _append_json_array(per_test_file, record)

    # 3) Global cumulative history JSONL
    _append_jsonl(config._reports_history_jsonl, record)


def pytest_sessionfinish(session, exitstatus):
    """
    End of session: write a single JSON summary file for the whole run.
    """
    config = session.config

    run_id = getattr(config, "_run_id", f"run_{_run_file_stamp()}")
    run_started_at = getattr(config, "_run_started_at", None)
    run_finished_at = _now_iso_ist()

    results = getattr(config, "_results", [])

    summary = {
        "run_id": run_id,
        "run_started_at": run_started_at,
        "run_finished_at": run_finished_at,
        "exitstatus": exitstatus,
        "totals": {
            "total": len(results),
            "passed": sum(1 for r in results if r["outcome"] == "passed"),
            "failed": sum(1 for r in results if r["outcome"] == "failed"),
            "skipped": sum(1 for r in results if r["outcome"] == "skipped"),
        },
        "results": results,
    }

    run_file = config._reports_runs_dir / f"{run_id}.json"
    run_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
