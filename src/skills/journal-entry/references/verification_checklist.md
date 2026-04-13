# 8-Point Journal Entry Verification Checklist

## Overview

Agent 13 (Double-Entry Verification) applies this 8-point checklist to every proposed journal entry before it can be posted to the ledger. All checks must pass for auto-posting. Any failure results in rejection or a warning that requires human acknowledgment.

---

## Check 1: Debits Equal Credits

**Rule**: The sum of all debit amounts must exactly equal the sum of all credit amounts.

**Implementation**:
```
sum(line.debit for line in entry.lines) == sum(line.credit for line in entry.lines)
```

**Tolerance**: Zero. No rounding tolerance allowed. If amounts do not balance to the cent, the entry is rejected.

**Failure message**: `REJECT: DR/CR imbalance of KES {difference}. Total debits: KES {total_dr}, Total credits: KES {total_cr}.`

**Common causes of failure**:
- Rounding errors in VAT calculations
- Missing WHT line
- Incorrect split amounts

---

## Check 2: No Zero-Amount Lines

**Rule**: Every journal line must have either a non-zero debit OR a non-zero credit. A line cannot have both debit and credit as zero, nor can it have values in both debit and credit simultaneously.

**Implementation**:
```
for each line:
  assert (line.debit > 0 and line.credit == 0) or (line.debit == 0 and line.credit > 0)
```

**Failure message**: `REJECT: Line {n} (account {code}) has zero amount.` or `REJECT: Line {n} has both debit and credit values.`

**Common causes of failure**:
- Placeholder lines left in template
- Calculation resulting in zero (e.g., 0% WHT on exempt payment)

---

## Check 3: Valid Account Codes

**Rule**: Every account code referenced in the journal entry must exist in the active Chart of Accounts.

**Implementation**:
```
for each line:
  assert line.account_code in chart_of_accounts
  assert chart_of_accounts[line.account_code].is_active == True
```

**Failure message**: `REJECT: Unknown account code {code} on line {n}.` or `REJECT: Account {code} ({name}) is inactive/archived.`

**Common causes of failure**:
- Typo in account code
- Using old account codes after chart restructuring
- Account deactivated but still referenced in templates

---

## Check 4: Open Accounting Period

**Rule**: The effective date of the journal entry must fall within an accounting period that is currently open (not locked/closed).

**Implementation**:
```
period = get_period(entry.effective_date)
assert period.status == 'OPEN'
```

**Failure message**: `REJECT: Period {month}/{year} is closed. Entry date {date} cannot be posted. Last open period: {last_open}.`

**Period locking logic**:
- Monthly periods lock after month-end close is completed
- Year-end periods lock after annual audit
- Only users with ADMIN role can reopen a closed period
- Back-dating entries to closed periods requires explicit override

---

## Check 5: No Duplicate Entries

**Rule**: No identical journal entry (same date, same description, same account codes, same amounts) should exist within a 24-hour window.

**Implementation**:
```
existing = find_entries(
  date_range=(entry.effective_date - 24h, entry.effective_date + 24h),
  description_similarity > 0.95,
  lines_match=True
)
assert len(existing) == 0
```

**Failure message**: `WARN: Possible duplicate of {existing_entry_id} posted on {date}. Review before proceeding.`

**Note**: This is a WARNING, not a hard rejection. Legitimate duplicates exist (e.g., two identical purchases on the same day). The user must acknowledge the warning to proceed.

**Deduplication fields compared**:
1. Effective date (within 24 hours)
2. Description (cosine similarity > 0.95)
3. Line account codes (exact match)
4. Line amounts (exact match)

---

## Check 6: Evidence Attached

**Rule**: Every journal entry should have at least one supporting document (source evidence) linked to it.

**Implementation**:
```
assert len(entry.attachments) > 0 or entry.source_document_id is not None
```

**Failure message**: `WARN: No supporting document attached to this journal entry. Source evidence is required for audit trail.`

**Note**: This is a WARNING, not a hard rejection. Some entries (e.g., depreciation, accruals, adjusting entries) may not have external documents.

**Accepted evidence types**:
- Receipt image (from OCR pipeline)
- Invoice PDF (from email or upload)
- Bank statement line reference
- WhatsApp message reference
- M-Pesa confirmation
- Manual upload (any image/PDF)

---

## Check 7: Correct Account Types

**Rule**: Debit and credit entries must align with the normal balance convention for each account type.

**Implementation**:
```
for each line:
  account = chart_of_accounts[line.account_code]
  if line.debit > 0:
    assert account.type in ['ASSET', 'EXPENSE', 'CONTRA_LIABILITY', 'CONTRA_EQUITY', 'CONTRA_REVENUE']
    # OR the entry is a decrease (reversal/adjustment)
  if line.credit > 0:
    assert account.type in ['LIABILITY', 'EQUITY', 'REVENUE', 'CONTRA_ASSET']
    # OR the entry is a decrease (reversal/adjustment)
```

**Failure message**: `REJECT: Account {code} ({name}) is a {type} account and should not be {debited/credited} in normal operations. If this is a reversal, mark entry as type=REVERSAL.`

**Special handling**:
- Reversing entries: entries marked as `type=REVERSAL` or `type=ADJUSTMENT` bypass this check
- Contra accounts: contra-revenue (e.g., Sales Returns 4100) is debited; contra-asset (e.g., Accumulated Depreciation 1321) is credited
- VAT Input (2200) is a liability account with a normal debit balance (it is a contra-liability in effect)

---

## Check 8: Consistent Currency

**Rule**: All lines in a journal entry must use the same currency. If multiple currencies are involved, explicit foreign exchange conversion entries must be present.

**Implementation**:
```
currencies = set(line.currency for line in entry.lines)
if len(currencies) > 1:
  assert entry.has_forex_conversion == True
  assert forex_gain_loss_line_present == True
```

**Failure message**: `REJECT: Mixed currencies detected ({currencies}) without forex conversion. Add exchange rate and forex gain/loss line.`

**Multi-currency handling**:
- All lines should be in the functional currency (KES) for posting
- Foreign currency amounts should be converted at the transaction date rate
- A forex gain/loss line (4050/5960) must be present if the rate differs from the original booking rate
- The exchange rate used must be documented in the entry metadata

---

## Verification Output Schema

```json
{
  "entry_id": "JE-2026-04-001",
  "verified": true,
  "checks": [
    {"number": 1, "name": "dr_equals_cr", "status": "PASS", "message": null},
    {"number": 2, "name": "no_zero_lines", "status": "PASS", "message": null},
    {"number": 3, "name": "valid_accounts", "status": "PASS", "message": null},
    {"number": 4, "name": "open_period", "status": "PASS", "message": null},
    {"number": 5, "name": "no_duplicates", "status": "PASS", "message": null},
    {"number": 6, "name": "evidence_attached", "status": "WARN", "message": "No supporting document attached"},
    {"number": 7, "name": "correct_account_types", "status": "PASS", "message": null},
    {"number": 8, "name": "consistent_currency", "status": "PASS", "message": null}
  ],
  "overall_status": "PASS_WITH_WARNINGS",
  "warnings_count": 1,
  "errors_count": 0,
  "verification_timestamp": "2026-04-10T14:30:00Z",
  "verified_by": "agent_13"
}
```

## Status Definitions

| Status | Meaning | Action |
|--------|---------|--------|
| `PASS` | All 8 checks passed with no warnings | Proceed to semantic verification (Agent 15) |
| `PASS_WITH_WARNINGS` | All checks passed but warnings exist | Proceed with user notification |
| `FAIL` | One or more checks failed | Reject, return to Agent 7 for correction |
