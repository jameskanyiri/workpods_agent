---
name: bank-reconciliation
description: Bank statement parsing, automated reconciliation with book entries, and verification pipeline for Kenyan commercial banks. Maps to Agents 5 (Bank Statement Parser), 9 (Bank Reconciliation), and 17 (Reconciliation Verification).
---

# Bank Reconciliation Skill

This skill handles the end-to-end bank reconciliation process: parsing bank statements from seven major Kenyan banks, matching bank transactions against book entries using a 5-rule cascade, and verifying matches with semantic similarity scoring.

## Agents

| Agent | Name | Role |
|-------|------|------|
| 5 | Bank Statement Parser | Parse CSV, PDF, and Excel bank statements into normalized transactions |
| 9 | Bank Reconciliation | Match bank transactions to book entries using 5-rule cascade |
| 17 | Reconciliation Verification | Verify match quality using MiniLM-L6-v2 description similarity |

## Bank Statement Parser (Agent 5)

### Supported Banks

| Bank | CSV | PDF | Excel | Parser Type |
|------|-----|-----|-------|-------------|
| Equity Bank | Yes | Yes | Yes | Rule-based |
| KCB | Yes | Yes | Yes | Rule-based |
| NCBA | Yes | Yes | No | Rule-based |
| Co-operative Bank | Yes | Yes | Yes | Rule-based |
| Stanbic Bank | Yes | Yes | No | Rule-based |
| ABSA Kenya | Yes | Yes | Yes | Rule-based |
| Standard Chartered | Yes | Yes | No | Rule-based |

See `references/bank_formats.md` for detailed parser specifications per bank.

### PDF Parsing

PDF bank statements are parsed using `tabula-py` (Java-based tabular PDF extraction):
1. Detect table regions in the PDF
2. Extract rows with column alignment
3. Handle multi-page statements with header repetition
4. Merge split rows (long descriptions that wrap to next line)

### Excel Parsing

Excel files are parsed using `openpyxl`:
1. Detect header row (may not be row 1)
2. Map columns to normalized schema
3. Handle merged cells and formatted numbers
4. Skip summary/footer rows

### Normalized Transaction Schema

All bank formats are normalized to:

```json
{
  "bank_tx_id": "unique-id-from-bank",
  "date": "2026-04-10",
  "value_date": "2026-04-10",
  "description": "MPESA/SHK7X2M4LP/JOHN DOE",
  "reference": "SHK7X2M4LP",
  "debit": 0.00,
  "credit": 5000.00,
  "balance": 125000.00,
  "channel": "MPESA",
  "bank_name": "EQUITY"
}
```

## Bank Reconciliation Engine (Agent 9)

### 5-Rule Cascade Matching

Transactions are matched using a cascade of increasingly permissive rules. The first rule that produces a match wins. Each rule assigns a confidence score.

| Rule | Criteria | Confidence | Description |
|------|----------|------------|-------------|
| 1 | Exact amount + exact date + exact reference | 99% | Perfect match on all three fields |
| 2 | Exact amount + date within 3 days + M-Pesa ID match | 97% | Near-match with M-Pesa reference confirmation |
| 3 | Exact amount + date within 7 days + cosine similarity > 0.85 | 90% | Amount and date match with similar descriptions |
| 4 | Amount within +/-2% + date within 7 days + fuzzy ratio > 0.8 | 80% | Approximate match allowing for fees/rounding |
| 5 | No match found | N/A | Flagged for human review |

See `references/matching_rules.md` for the complete matching engine specification.

### Matching Process

1. **Pre-filter**: Group bank transactions and book entries by month
2. **Index**: Build amount-based index for O(1) lookup
3. **Cascade**: For each unmatched bank transaction, run rules 1-4 in order
4. **Deduplicate**: Ensure no book entry is matched to multiple bank transactions
5. **Report**: Generate reconciliation report

### Output: Reconciliation Report

```json
{
  "reconciliation_id": "REC-2026-04-001",
  "bank_account": "Equity Bank - 1234567890",
  "period": {"from": "2026-03-01", "to": "2026-03-31"},
  "bank_balance": 1250000.00,
  "book_balance": 1247500.00,
  "difference": 2500.00,
  "summary": {
    "total_bank_transactions": 145,
    "matched": 138,
    "partially_matched": 4,
    "unmatched_bank": 2,
    "unmatched_book": 1
  },
  "matched_items": [
    {
      "bank_tx_id": "EQ-2026-03-001",
      "book_entry_id": "JE-2026-03-045",
      "rule_applied": 1,
      "confidence": 0.99,
      "bank_amount": 5000.00,
      "book_amount": 5000.00
    }
  ],
  "partially_matched_items": [
    {
      "bank_tx_id": "EQ-2026-03-089",
      "book_entry_id": "JE-2026-03-102",
      "rule_applied": 4,
      "confidence": 0.82,
      "bank_amount": 10200.00,
      "book_amount": 10000.00,
      "difference": 200.00,
      "note": "Possible bank charge included"
    }
  ],
  "unmatched_items": {
    "bank_only": [
      {
        "bank_tx_id": "EQ-2026-03-143",
        "date": "2026-03-29",
        "amount": 2500.00,
        "description": "CHG/MONTHLY MAINTENANCE FEE"
      }
    ],
    "book_only": [
      {
        "book_entry_id": "JE-2026-03-144",
        "date": "2026-03-31",
        "amount": 15000.00,
        "description": "Cheque #001234 to Supplier X"
      }
    ]
  }
}
```

## Reconciliation Verification (Agent 17)

### Semantic Similarity Scoring

Uses `sentence-transformers/all-MiniLM-L6-v2` to compute cosine similarity between bank transaction descriptions and book entry descriptions.

**Process**:
1. Encode bank description into embedding vector
2. Encode book description into embedding vector
3. Compute cosine similarity
4. Threshold: > 0.85 confirms match, 0.70-0.85 flags for review, < 0.70 rejects match

**Example**:
- Bank: "MPESA/SHK7X2M4LP/OFFICE SUPPLIES NAIVAS"
- Book: "Office supplies purchased from Naivas via M-Pesa"
- Cosine similarity: 0.91 (confirmed match)

### Verification Checks

1. All Rule 1 matches: auto-verified (skip similarity check)
2. Rule 2-3 matches: verify with similarity scoring
3. Rule 4 matches: verify with similarity scoring + flag amount difference
4. Unmatched items: attempt cross-matching against older periods (up to 90 days)

## LangGraph Node

- **Node name**: `bank_reconciliation`
- **State keys consumed**: `bank_statement_file`, `bank_name`, `account_id`, `period`
- **State keys produced**: `parsed_transactions`, `reconciliation_report`, `unmatched_items`
- **Next nodes**: `human_review` (if unmatched items exist), `ledger_update` (if fully reconciled)

## Model Dependencies

| Component | Library/Model |
|-----------|--------------|
| PDF parsing | tabula-py 2.9+ |
| Excel parsing | openpyxl 3.1+ |
| CSV parsing | pandas |
| Similarity scoring | sentence-transformers (all-MiniLM-L6-v2) |
| Fuzzy matching | rapidfuzz |
