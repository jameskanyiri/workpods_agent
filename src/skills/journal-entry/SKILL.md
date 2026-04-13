---
name: journal-entry
description: Journal entry proposal, recurring transaction detection, double-entry verification, and semantic verification pipeline. Maps to Agents 7 (Journal Proposal), 8 (Recurring Transaction), 13 (Double-Entry Verification), and 15 (Semantic Verification).
---

# Journal Entry Skill

This skill covers the full journal entry lifecycle: proposing journal entries from source documents using Claude Sonnet, detecting recurring patterns with XGBoost, verifying double-entry integrity with a rule engine, and semantically validating entries against source documents with Claude Haiku.

## Agents

| Agent | Name | Role |
|-------|------|------|
| 7 | Journal Proposal | Generate journal entries from source data using Claude Sonnet |
| 8 | Recurring Transaction | Detect recurring patterns and create templates using XGBoost |
| 13 | Double-Entry Verification | 8-point rule engine for journal integrity |
| 15 | Semantic Verification | Claude Haiku validates entry against source document |

## Journal Proposal (Agent 7)

### System Prompt Engineering

Agent 7 uses Claude Sonnet with a carefully engineered system prompt that includes dynamic context:

1. **Chart of Accounts**: Full chart with account codes, names, types, and normal balances (see `references/chart_of_accounts.md`)
2. **VAT rules**: Standard rate (16%), zero-rated items, exempt items, reverse charge rules
3. **WHT table**: Withholding tax rates by payment type (management fees 5%, professional fees 5%, contractual fees 3%, etc.)
4. **Statutory deductions**: NSSF (Tier I: 6% up to KES 7,000; Tier II: 6% on KES 7,001-36,000), NHIF (graduated scale), Housing Levy (1.5% of gross), PAYE (graduated bands)
5. **Last 20 similar transactions**: Retrieved by vendor/customer name and category for consistency

### Output Format

```json
{
  "effective_date": "2026-04-10",
  "description": "Office rent payment to Landlord Ltd for April 2026",
  "lines": [
    {
      "account_code": "5200",
      "account_name": "Rent & Lease Expense",
      "debit": 86207.00,
      "credit": 0.00
    },
    {
      "account_code": "2200",
      "account_name": "VAT Input (Claimable)",
      "debit": 13793.00,
      "credit": 0.00
    },
    {
      "account_code": "2310",
      "account_name": "WHT Payable - Rent",
      "debit": 0.00,
      "credit": 10000.00
    },
    {
      "account_code": "1000",
      "account_name": "Bank - Main",
      "debit": 0.00,
      "credit": 90000.00
    }
  ],
  "tax_implications": {
    "vat_input": 13793.00,
    "wht_deducted": 10000.00,
    "wht_rate": 0.10,
    "wht_type": "RENT"
  },
  "confidence": 0.93,
  "reasoning": "Rent payment of KES 100,000 inclusive of 16% VAT. WHT at 10% on gross rent deducted. Net payment = 100,000 - 10,000 WHT = 90,000.",
  "similar_entries_referenced": ["JE-2026-03-015", "JE-2026-02-018"]
}
```

### WHT Rate Table

| Payment Type | Rate | Tax Code |
|-------------|------|----------|
| Management / Professional fees | 5% | WHT-MGMT |
| Training fees | 5% | WHT-TRAIN |
| Contractual fees | 3% | WHT-CONT |
| Consultancy fees | 5% | WHT-CONS |
| Rent (immovable property) | 10% | WHT-RENT |
| Dividends (resident) | 5% | WHT-DIV |
| Interest (resident) | 15% | WHT-INT |
| Royalties | 5% | WHT-ROY |
| Insurance commission | 5% | WHT-INS |
| Appearance / performance fees | 5% | WHT-PERF |

## Recurring Transaction Detection (Agent 8)

### Detection Logic

An XGBoost classifier identifies recurring transactions based on three occurrence criteria:

1. **Same vendor/customer**: Fuzzy match on name (ratio > 0.9)
2. **Similar amount**: Within +/- 10% of previous occurrences
3. **Regular interval**: Consistent time gap (weekly, biweekly, monthly, quarterly)

### Trigger Threshold

A transaction is flagged as recurring after **3 occurrences** meeting all three criteria.

### Template Creation

Once flagged, a recurring template is created:

```json
{
  "template_id": "TPL-001",
  "vendor": "Kenya Power",
  "description": "Monthly electricity bill",
  "frequency": "MONTHLY",
  "expected_day": 15,
  "expected_amount_range": {"min": 8500.00, "max": 12000.00},
  "lines_template": [
    {"account_code": "5500", "type": "debit", "amount_type": "variable"},
    {"account_code": "2200", "type": "debit", "amount_type": "calculated", "formula": "line_0 * 0.16"},
    {"account_code": "1000", "type": "credit", "amount_type": "total"}
  ],
  "auto_post": false,
  "notify_if_missing": true,
  "notify_days_overdue": 5
}
```

### XGBoost Features

| Feature | Description |
|---------|-------------|
| `vendor_hash` | Hashed vendor name |
| `amount_cv` | Coefficient of variation across occurrences |
| `interval_mean` | Mean days between occurrences |
| `interval_std` | Standard deviation of interval |
| `category_code` | Account category |
| `payment_method` | Encoded payment method |
| `day_of_month_std` | Std dev of day-of-month across occurrences |

## Double-Entry Verification (Agent 13)

### 8-Point Verification Checklist

Every journal entry must pass all 8 checks before posting. See `references/verification_checklist.md` for full details and `references/double_entry_rules.md` for debit/credit rules.

| # | Check | Rule | Failure Action |
|---|-------|------|---------------|
| 1 | Debits equal Credits | Sum of all debit amounts must equal sum of all credit amounts | Reject: "DR/CR imbalance of KES X" |
| 2 | No zero-amount lines | Every line must have either a non-zero debit or non-zero credit | Reject: "Line N has zero amount" |
| 3 | Valid account codes | Every account code must exist in the Chart of Accounts | Reject: "Unknown account code XXXX" |
| 4 | Open accounting period | Effective date must fall within an open (unlocked) accounting period | Reject: "Period MM/YYYY is closed" |
| 5 | No duplicate entries | No identical entry (same date, description, amounts, accounts) within 24 hours | Warn: "Possible duplicate of JE-XXXX" |
| 6 | Evidence attached | Source document (receipt, invoice, bank statement) must be linked | Warn: "No supporting document attached" |
| 7 | Correct account types | Debits go to correct account types (assets/expenses increase with debit) | Reject: "Revenue account XXXX should not be debited" |
| 8 | Consistent currency | All lines must use the same currency, or explicit forex conversion must be present | Reject: "Mixed currencies without conversion" |

### Verification Output

```json
{
  "verified": true,
  "checks_passed": 8,
  "checks_failed": 0,
  "warnings": [],
  "errors": [],
  "verification_timestamp": "2026-04-10T14:30:00Z"
}
```

## Semantic Verification (Agent 15)

### Purpose

After mechanical verification (Agent 13), Agent 15 uses Claude Haiku to semantically validate that the journal entry correctly represents the source document.

### Prompt Template

```
Given the following source document:
{source_document_text}

And the following proposed journal entry:
{journal_entry_json}

Does this journal entry correctly represent the financial transaction described in the source document?

Answer with:
- YES: The entry accurately captures the transaction
- NO: The entry contains errors (explain what is wrong)
- UNCERTAIN: Cannot determine correctness (explain what information is missing)
```

### Decision Matrix

| Response | Confidence | Action |
|----------|-----------|--------|
| YES | > 0.9 | Auto-post (if auto-posting enabled) |
| YES | 0.7 - 0.9 | Post with notification to accountant |
| UNCERTAIN | Any | Queue for human review |
| NO | Any | Reject, return to Agent 7 for re-proposal with error context |

### Common Semantic Errors Caught

- Wrong account category (e.g., recording a capital expense as operating expense)
- Missing VAT component when vendor is VAT-registered
- WHT not deducted when required
- Wrong vendor/customer assignment
- Amount mismatch between source and entry
- Date mismatch (e.g., entry dated differently from invoice date)

## LangGraph Node

- **Node name**: `journal_entry`
- **Subgraph nodes**: `propose` -> `recurring_check` -> `double_entry_verify` -> `semantic_verify`
- **State keys consumed**: `extracted_data`, `source_document`, `source_type`
- **State keys produced**: `journal_entry`, `verification_result`, `recurring_template`, `posting_decision`
- **Next nodes**: `ledger_posting` (if verified), `human_review` (if uncertain/failed), `propose` (if rejected for re-proposal, max 2 retries)
