# Anomaly Detection Rules

## Rule 1: Duplicate Transaction Detection

**Logic:** Flag transactions where the same vendor and same amount appear within a 7-day window.

**Threshold:**
- Exact amount match (to the cent)
- Same vendor_id
- Within 7 calendar days

**Example:**
```
Jan 10: Payment to Vendor A - KES 45,000.00
Jan 14: Payment to Vendor A - KES 45,000.00  <-- FLAGGED
```

**Exceptions:**
- Recurring payments (rent, subscriptions) marked as recurring in the system are excluded
- Payroll batch payments are excluded

**Severity:** High

---

## Rule 2: Statistical Outlier

**Logic:** Flag transactions where the amount exceeds 3 standard deviations from the vendor's historical mean.

**Calculation:**
```
mean = average of all transactions with this vendor (last 12 months)
std_dev = standard deviation of those transactions
threshold = mean + (3 x std_dev)
```

**Example:**
```
Vendor B historical: KES 10,000, 12,000, 11,500, 9,800, 10,200
Mean: KES 10,700    Std Dev: KES 890
Threshold: 10,700 + (3 x 890) = KES 13,370

New transaction: KES 25,000  <-- FLAGGED (exceeds 13,370)
```

**Minimum data:** Requires at least 5 historical transactions. If fewer, this rule is skipped for that vendor.

**Severity:** Medium

---

## Rule 3: Round Number Bias

**Logic:** Flag users whose transactions in a 30-day rolling window are predominantly round numbers.

**Definition of round number:** Amount ending in 000 (e.g., KES 5,000, KES 50,000, KES 100,000).

**Threshold:** More than 80% of a user's transactions in the window are round numbers.

**Example:**
```
User C's last 30 days: 10 transactions
  KES 5,000, 10,000, 3,000, 7,000, 15,000, 8,000, 20,000, 12,000, 4,500, 6,000
Round numbers: 9 out of 10 = 90%  <-- FLAGGED (exceeds 80%)
```

**Rationale:** Legitimate transactions typically have varied amounts. A high proportion of round numbers may indicate fabricated expenses.

**Severity:** Low (informational)

---

## Rule 4: Weekend/Holiday Transactions

**Logic:** Flag transactions created on weekends (Saturday/Sunday) or Kenyan public holidays.

**Public holidays include:**
- New Year's Day (1 Jan)
- Labour Day (1 May)
- Madaraka Day (1 Jun)
- Mashujaa Day (20 Oct)
- Jamhuri Day (12 Dec)
- Christmas Day (25 Dec)
- Boxing Day (26 Dec)
- Good Friday, Easter Monday (variable)
- Eid al-Fitr, Eid al-Adha (variable)
- Utamaduni Day (10 Oct)

**Severity:** Low

**Note:** Some businesses operate on weekends. This rule can be disabled per business in settings.

---

## Rule 5: New Vendor High-Value First Transaction

**Logic:** Flag the first-ever transaction with a vendor if it exceeds KES 100,000.

**Threshold:** KES 100,000 (configurable per business)

**Example:**
```
New vendor "XYZ Supplies" - no prior transactions
First payment: KES 250,000  <-- FLAGGED
```

**Action:** Requires manager approval before the transaction is posted. The vendor's KRA PIN and registration details should be verified.

**Severity:** High

---

## Rule 6: Category Expense Spike

**Logic:** Flag an expense category if the current month's total exceeds the 3-month rolling average by more than 50%.

**Calculation:**
```
rolling_avg = (month_1 + month_2 + month_3) / 3
threshold = rolling_avg x 1.5
```

**Example:**
```
"Office Supplies" category:
  October:  KES 30,000
  November: KES 25,000
  December: KES 35,000
  Rolling avg: KES 30,000
  Threshold: KES 45,000

  January:  KES 52,000  <-- FLAGGED (exceeds 45,000)
```

**Minimum data:** Requires at least 3 months of history. New categories are exempt until sufficient data exists.

**Severity:** Medium

---

## Severity Levels and Actions

| Severity | Action |
|----------|--------|
| High | Block posting, require manager approval |
| Medium | Allow posting but flag for review within 48 hours |
| Low | Log alert, include in weekly anomaly report |

## Combined Scoring

When multiple rules fire on the same transaction, severity is escalated:
- 2+ Low flags = Medium
- 1 Medium + 1 Low = High
- 2+ Medium flags = High (block posting)
