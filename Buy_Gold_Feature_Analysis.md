# Feature Analysis: Buy Gold Flow (24/7, Platform-Defined Pricing)

**(This is a sample template for fueature analysis including Risk analysis, Test Scenarios, Test cases covering critical paths, & Release decision for a one-time, non-financial bug that pushes the release by 2 days)**

### By: Amir Mohammad Shahsavarani

## 0) Scope and Assumptions

**Scope:**  
End-to-end “Buy Gold” user journey:
- Viewing buy price
- Entering amount or grams
- Receiving a quote (if applicable)
- Confirming purchase
- Wallet/payment deduction
- Gold credit
- Receipt and transaction history

**Key assumptions (these could be adjusted in fueature if product differs):**
- Platform provides its **own buy price** (not a third-party market feed).
- User must be **authenticated** to complete a purchase.
- Purchase can be entered by **amount (currency)** or **grams**.
- A **time-bound quote** may exist to lock the price.
- Funds come from **wallet balance** or an integrated **payment gateway**.
- Orders and ledger updates must be **auditable**.

---

## 1) Risk Analysis

### 1.1 Financial Risks

1. **Wrong price charged vs displayed**
   - UI shows price A, backend executes at price B.
   - Impact: direct monetary loss and legal exposure.
2. **Quote expiry not enforced**
   - User confirms after expiration but order executes anyway.
3. **Duplicate orders (double submit / retry)**
   - Network latency or double click creates multiple orders.
4. **Precision & rounding errors**
   - Gold grams and currency decimals must follow strict rules.
5. **Fee / spread miscalculation**
   - Inconsistent fee calculation between quote and final receipt.
6. **Insufficient funds execution**
   - Client-side validation only; backend allows execution.

**Expected controls**
- Server-side price validation and quote locking.
- Idempotency key on order creation.
- Centralized calculation logic and rounding rules.
- Backend as the final authority.

---

### 1.2 Data Integrity Risks

1. **Ledger inconsistency**
   - Cash debited but gold not credited (or vice versa).
2. **Eventual consistency confusion**
   - Success shown but history/balance not updated.
3. **Missing or duplicated transaction history**
4. **Incorrect order state transitions**
   - PENDING / SUCCESS / FAILED mis-handled.
5. **Account/session mix-up**
   - Wrong user wallet affected.

**Expected controls**
- Atomic ledger operations or compensating transactions.
- Durable audit trail.
- Clear order state model.

---

### 1.3 System & Availability Risks

1. **Pricing service downtime**
2. **Traffic spikes during volatility**
3. **Retries causing duplicate orders**
4. **Partial outages**
5. **Poor mobile / unstable network behavior**

**Expected controls**
- Graceful degradation and clear messaging.
- Idempotency and retry safety.
- Monitoring and alerting on critical services.

---

### 1.4 User Trust Risks

1. **Unexpected price change at confirmation**
2. **Generic or unclear error messages**
3. **Missing receipt or transaction trace**
4. **Perceived price manipulation**
5. **No progress indication during processing**

**Expected controls**
- Clear price timestamp and quote validity.
- Actionable error messages.
- Immediate receipt and history visibility.

---

## 2) Detailed Test Scenarios

### 2.1 Price Display & Refresh
1. Price loads correctly with timestamp.
2. Price refresh updates calculated totals.
3. Pricing service unavailable → buy disabled with message.

### 2.2 Input Validation
4. Valid amount purchase.
5. Valid grams purchase with precision.
6. Minimum boundary value.
7. Below minimum rejected.
8. Maximum boundary enforced.
9. Invalid formats rejected.
10. Rounding edge cases handled consistently.

### 2.3 Quote / Price Lock
11. Valid quote execution.
12. Quote expires before confirmation.
13. Quote refresh requires re-confirmation.

### 2.4 Order Submission & Idempotency
14. Single confirm → one order.
15. Double confirm → still one order.
16. Timeout + retry → no duplicate order.

### 2.5 Wallet / Payment
17. Sufficient funds → correct debit/credit.
18. Insufficient funds → clear error, no execution.
19. Payment gateway decline.
20. Payment succeeds but receipt delayed.

### 2.6 Ledger & History
21. Receipt shows full breakdown.
22. History updated correctly.
23. Wallet balances match receipt/history.

### 2.7 Security & Session
24. Unauthenticated user blocked.
25. Session expires mid-flow.

### 2.8 Trust & UX
26. Error messages are understandable.
27. Processing state prevents re-submit.

---

## 3) Critical-Path Test Cases

### TC-01 — Happy Path Buy by Amount
- **Preconditions:** Logged in, sufficient wallet balance.
- **Steps:** Enter amount → confirm → view receipt → check history.
- **Expected:** One order, correct balances, receipt visible.
- **Priority:** P0

### TC-02 — Happy Path Buy by Grams
- **Expected:** Correct precision, rounding, and balances.
- **Priority:** P0

### TC-03 — Quote Expiry Enforcement
- **Expected:** No execution after expiry.
- **Priority:** P0

### TC-04 — Insufficient Funds (Negative)
- **Expected:** Clear error, no debit/credit.
- **Priority:** P0

### TC-05 — Duplicate Submit Protection
- **Expected:** One order only.
- **Priority:** P0

### TC-06 — Pricing Service Failure
- **Expected:** Buy disabled, no execution.
- **Priority:** P0

### TC-07 — Ledger Consistency on Partial Failure
- **Expected:** Safe final state or compensating transaction.
- **Priority:** P0 / P1

---

## 4) Release Decision — Non-Financial Bug Delaying Release by 2 Days

### 4.1 Decision Framework

Evaluate the bug based on:
1. User impact
2. Trust impact
3. Operational/support impact
4. Mitigation availability
5. Regression risk

---

### 4.2 Release vs Delay Example

**Release immediately if:**
- Bug is cosmetic only.
- No effect on price, balances, receipt, or history.
- No user confusion or trust impact.
- Workaround exists (hide label, feature flag).

**Delay release (2 days) if:**
- Bug affects confirmation, receipt, or history.
- Bug can be misinterpreted as wrong execution.
- Bug blocks completion or causes retries.
- Bug increases compliance or support risk.

---

### 4.3 Final QA Recommendation

- **Treat any bug affecting purchase confirmation, receipt, or audit trail as a release blocker**, even if labeled “non-financial”.
- Cosmetic issues with no trust or data impact should not block release but must be tracked and patched quickly.

---

## Release Gating Summary

**Must be green to ship:**
- Price correctness
- Quote enforcement
- Idempotency
- Insufficient funds handling
- Ledger consistency
- Receipt and history accuracy

**Can follow in next patch:**
- Minor UI inconsistencies outside transactional screens

---

**Document Type:** Manual QA Feature Analysis  
**Audience:** Product, Engineering, QA, Release Management  
