---
name: whatsapp-transactions
description: WhatsApp message intake pipeline covering intent classification and NLP-based transaction data extraction for Kenyan SMEs. Maps to Agents 1 (WhatsApp Listener) and 2 (WhatsApp Data Entry).
---

# WhatsApp Transactions Skill

This skill handles the full lifecycle of WhatsApp-based transaction recording: classifying incoming messages by intent, extracting structured financial data from natural language, and producing journal-ready output.

## Agents

| Agent | Name | Role |
|-------|------|------|
| 1 | WhatsApp Listener | Intent classification and message routing |
| 2 | WhatsApp Data Entry | NLP extraction of financial data from text |

## Intent Classification (Agent 1)

Every incoming WhatsApp message is classified into one of five intent categories:

| Intent | Description | Example |
|--------|-------------|---------|
| `TRANSACTION_RECORDING` | User wants to record a financial event | "Paid 5k for office supplies via M-Pesa" |
| `REPORT_REQUEST` | User wants to view financial data | "Show me last month's expenses" |
| `APPROVAL_RESPONSE` | User is responding to a pending approval | "Approve" / "Reject, amount is wrong" |
| `QUESTION` | User is asking about their books | "What's the balance on petty cash?" |
| `NOISE` | Non-financial chatter, greetings, spam | "Good morning" / sticker / media |

See `references/intent_categories.md` for the full taxonomy with examples.

## Data Extraction (Agent 2)

For messages classified as `TRANSACTION_RECORDING`, the extraction pipeline converts natural language into structured JSON:

### Extracted Fields

```json
{
  "type": "EXPENSE | REVENUE | TRANSFER | PETTY_CASH",
  "amount": 5000.00,
  "currency": "KES",
  "category": "office_supplies",
  "payment_method": "MPESA | CASH | BANK_TRANSFER | CHEQUE | CARD",
  "vendor_or_customer": "Jumia Office",
  "reference": "SHK7X2M4LP",
  "description": "Office supplies from Jumia"
}
```

### Kenyan Shorthand Parsing

The extraction engine handles common Kenyan financial shorthand:

- `k` or `K` suffix = multiply by 1,000 (e.g., "5k" = 5,000 KES)
- `m` or `M` suffix = multiply by 1,000,000 (e.g., "1.5m" = 1,500,000 KES)
- M-Pesa transaction codes (10 alphanumeric characters starting with a letter) are extracted as references
- Common abbreviations: "mpesa" / "pesa" = M-Pesa, "bnk" = bank transfer, "csh" = cash

See `references/extraction_rules.md` for the complete parsing ruleset.

## Model Routing

Messages are routed to different Claude models based on complexity:

| Complexity | Model | Criteria |
|------------|-------|----------|
| Simple | Claude Haiku | Single transaction, single currency, clear amount and category |
| Complex | Claude Sonnet | Multi-line entries, foreign currency, split transactions, ambiguous categories, corrections to previous entries |

### Complexity Detection Heuristics

- Message contains multiple amounts or line items -> Complex
- Message mentions USD, EUR, GBP, or other non-KES currency -> Complex
- Message uses "split", "divide", "half" or similar -> Complex
- Message references a previous entry for correction -> Complex
- All other `TRANSACTION_RECORDING` messages -> Simple

## Output Format

The final output is a journal-ready structure:

```json
{
  "effective_date": "2026-04-10",
  "description": "Office supplies purchased from Jumia via M-Pesa",
  "lines": [
    {
      "account_code": "5100",
      "account_name": "Office Supplies",
      "debit": 5000.00,
      "credit": 0.00
    },
    {
      "account_code": "1110",
      "account_name": "M-Pesa Float",
      "debit": 0.00,
      "credit": 5000.00
    }
  ],
  "source_type": "WHATSAPP",
  "source_message_id": "wamid.abc123",
  "confidence_score": 0.95,
  "requires_review": false,
  "tax_implications": {
    "vat_applicable": false
  }
}
```

### Confidence Scoring

| Score Range | Action |
|-------------|--------|
| 0.90 - 1.00 | Auto-post (if user has enabled auto-posting) |
| 0.70 - 0.89 | Post with confirmation prompt sent back to WhatsApp |
| 0.50 - 0.69 | Request clarification from user |
| Below 0.50 | Flag for manual review by accountant |

## LangGraph Node

- **Node name**: `whatsapp_intake`
- **State keys consumed**: `raw_message`, `sender_phone`, `message_timestamp`
- **State keys produced**: `intent`, `extracted_data`, `journal_proposal`, `confidence_score`
- **Next nodes**: `journal_proposal` (if TRANSACTION_RECORDING), `report_generator` (if REPORT_REQUEST), `approval_handler` (if APPROVAL_RESPONSE), `qa_agent` (if QUESTION), `END` (if NOISE)
