# Gold Buy Flow – QA Automation Sample  
## **Python · Playwright · Pytest**

### **By**: *Amir Mohammad Shahsavarni*

## Contents
- Part 1: Feature analysis & risk assessment (`Buy_Gold_Feature_Analysis.md`)
- Part 2: UI automation (Playwright + Pytest)


This repository contains a sample for an end-to-end (E2E) automated test suite for the **Buy Gold Flow** of an online gold trading platform that operates **24/7 with platform-defined prices**.

The project is designed to demonstrate:
- Clear test design
- Maintainable automation architecture
- Realistic business-flow coverage
- Deterministic and auditable test reporting (JSON, cumulative across runs)

---

## 1. High-Level Workflow

At a high level, the test execution flow is:

1. **Pytest starts a test session**
2. **Playwright launches a browser**
3. **Each test runs in an isolated browser context**
4. **Login is performed via a shared fixture**
5. **Tests interact with the Buy Gold flow using Page Objects**
6. **Assertions validate success or error states**
7. **Custom pytest hooks capture results**
8. **Test results are saved into cumulative JSON reports**
9. **A per-run summary JSON file is generated**

---

## 2. Project Structure & Responsibilities

gold-buy-e2e/
│
├── README.md
├── requirements.txt
├── playwright.config.py
├── .env.example
├── .gitignore
│
├── pages/
│ ├── base_page.py
│ ├── login_page.py
│ ├── buy_gold_page.py
│ └── order_success_page.py
│
├── tests/
│ ├── conftest.py
│ ├── test_buy_gold_happy_amount.py
│ ├── test_buy_gold_happy_grams.py
│ └── test_buy_gold_negative_insufficient_funds.py
│
├── utils/
│ ├── test_data.py
│ └── selectors.py
│
└── reports/ # Generated automatically (not committed)


---

## 3. Configuration & Environment

### `requirements.txt`
Defines all runtime dependencies:
- `playwright` → browser automation
- `pytest` → test runner
- `python-dotenv` → environment configuration

---

### `playwright.config.py`
Centralized configuration for:
- Base URL
- Headless vs headed execution
- Timeouts
- Slow-motion debugging

This keeps runtime behavior **consistent across all tests** and avoids hard-coding values in test files.

---

### `.env.example`
Template for runtime secrets and environment-specific values:
- Base URL
- Test user credentials
- Execution flags (headless, slow motion)

Each tester or CI system provides its own `.env` file.

---

## 4. Page Object Layer (`pages/`)

This layer encapsulates **UI structure and behavior**, isolating tests from UI changes.

### `base_page.py`
**Responsibility:**
- Shared helper functionality
- Common navigation or wait utilities

This avoids duplication across page classes.

---

### `login_page.py`
**Responsibility:**
- Login UI interactions
- Authentication flow

Used by a shared fixture so tests never duplicate login logic.

---

### `buy_gold_page.py`
**Responsibility:**
- Buy Gold screen interactions
- Input handling (amount / grams)
- Confirmation actions
- Error detection

This class models the **core business flow** of the platform.

---

### `order_success_page.py`
**Responsibility:**
- Success state verification
- Receipt and order ID extraction

Keeps success assertions consistent and reusable.

---

## 5. Test Layer (`tests/`)

Tests are **short, readable, and scenario-focused**.

### Test Philosophy
- Tests describe *what* is being verified
- Page Objects define *how* interactions happen
- No selectors or UI logic inside test files

---

### `conftest.py`
This is the **heart of the project**.

#### Responsibilities:
1. **Browser lifecycle management**
2. **Test isolation (fresh context per test)**
3. **Login fixture**
4. **Custom JSON reporting system**

##### Key Fixtures:
- `browser` → one browser per session
- `context` → isolated per test
- `page` → clean page per test
- `logged_in_page` → authenticated entry point

---

### Test Files

#### `test_buy_gold_happy_amount.py`
Validates:
- Buying gold by **currency amount**
- Successful order creation
- Receipt generation

---

#### `test_buy_gold_happy_grams.py`
Validates:
- Buying gold by **gram weight**
- Precision handling
- Successful confirmation

---

#### `test_buy_gold_negative_insufficient_funds.py`
Validates:
- Proper error handling when wallet balance is insufficient
- User-trust-preserving error messaging

---

## 6. Custom JSON Reporting System

This project implements a **custom reporting mechanism using pytest hooks**, without external plugins.

### Why this approach?
- Fully deterministic
- CI-friendly
- Auditable
- Easy to integrate with dashboards or analytics pipelines

---

### Report Output Structure

reports/
│
├── runs/
│ └── run_YYYY-MM-DDTHH-MM-SS+05-30.json
│
├── tests/
│ ├── tests__test_buy_gold_happy_amount__test_buy_gold_happy_path_by_amount.json
│ ├── tests__test_buy_gold_happy_grams__test_buy_gold_happy_path_by_grams.json
│ └── tests__test_buy_gold_negative_insufficient_funds__test_buy_gold_negative_insufficient_funds.json
│
└── history.jsonl

---

### What Each Report Contains

#### Per-Run Report (`reports/runs/`)
- One file per execution
- Summary statistics (pass/fail/skip)
- Full list of test results for that run

#### Per-Test Reports (`reports/tests/`)
- One file per test
- **Cumulative**: each execution appends a new record
- Enables trend analysis per test case

#### Global History (`history.jsonl`)
- Append-only log
- One JSON object per test execution
- Ideal for long-term analytics or ingestion into log systems

---

## 7. Execution Workflow (Step-by-Step)

1. `pytest` starts session
2. Playwright browser launches
3. Test context is created
4. Login is performed
5. Test scenario runs
6. Assertions validate behavior
7. Pytest hooks capture:
   - Outcome
   - Error details (if any)
   - Environment metadata
8. JSON files are written:
   - Per test
   - Per run
   - Global history
9. Browser context is destroyed
10. Session summary is saved

---

## 8. Running the Tests

### Run all tests
```bash
pytest -q

```

#### Run a single test
```bash
pytest tests/test_buy_gold_happy_amount.py
```

---
### 9. Design Principles Applied

- Separation of concerns
- Single responsibility per module
- Deterministic test outcomes
- Minimal flakiness
- Business-oriented validation
- Production-grade reporting


---

### 10. Extensibility
- This structure easily supports:
- API tests alongside UI tests
- CI/CD integration
- Performance or load checks
- Additional order types (sell, limit orders)
- Multi-environment execution

---

### 11. Notes

All selectors use data-testid placeholders and should be mapped to real attributes in the product.
Reporting output is excluded from version control by design.

---

**Author**: Amir Mohammad Shahsavraani
**Focus**: Quality, reliability, maintainability, and trust

