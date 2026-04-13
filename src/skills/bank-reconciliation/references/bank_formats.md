# Bank Statement Parser Specifications

## Overview

Rule-based parsers for the seven major Kenyan commercial banks. Each parser normalizes bank-specific formats into the standard transaction schema.

## Normalized Output Schema

```json
{
  "bank_tx_id": "string",
  "date": "YYYY-MM-DD",
  "value_date": "YYYY-MM-DD",
  "description": "string",
  "reference": "string",
  "debit": 0.00,
  "credit": 0.00,
  "balance": 0.00,
  "channel": "MPESA | EFT | CHEQUE | POS | ATM | RTGS | INTERNAL",
  "bank_name": "string"
}
```

---

## 1. Equity Bank

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Transaction Date | Format: DD/MM/YYYY |
| B | Value Date | Format: DD/MM/YYYY |
| C | Reference | Bank reference number |
| D | Description | Transaction narrative |
| E | Debit | Blank if credit |
| F | Credit | Blank if debit |
| G | Balance | Running balance |

- **Encoding**: UTF-8
- **Delimiter**: Comma
- **Header row**: Row 1
- **Footer**: Last 2 rows contain totals (skip)
- **Date format**: DD/MM/YYYY

### PDF Format

- **Tool**: tabula-py with `lattice=True`
- **Table detection**: Single table per page, header repeats on each page
- **Special handling**: Description may wrap to second line (merge rows where date column is empty)
- **Password protected**: Some statements are password-protected with account number

### Excel Format

- **Sheet**: "Statement" or first sheet
- **Header row**: Row 5 (rows 1-4 contain account info)
- **Account info extraction**: Account name (row 1), account number (row 2), period (row 3)

---

## 2. KCB (Kenya Commercial Bank)

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Date | Format: DD-MMM-YYYY (e.g., 05-Apr-2026) |
| B | Particulars | Transaction description |
| C | Cheque No | Cheque number if applicable |
| D | Withdrawals | Debit amount |
| E | Deposits | Credit amount |
| F | Balance | Running balance |

- **Encoding**: UTF-8 with BOM
- **Delimiter**: Comma
- **Header row**: Row 1
- **Date format**: DD-MMM-YYYY
- **Special**: Amount fields use parentheses for negatives

### PDF Format

- **Tool**: tabula-py with `stream=True` (KCB uses borderless tables)
- **Table detection**: May have multiple tables on summary page (skip summary, use detail pages)
- **Page header**: Account details repeated on every page

### Excel Format

- **Sheet**: "Transactions"
- **Header row**: Row 7
- **Special**: Merged cells in header area for account details

---

## 3. NCBA (formerly NIC and CBA)

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Txn Date | Format: YYYY-MM-DD |
| B | Value Date | Format: YYYY-MM-DD |
| C | Reference | Transaction reference |
| D | Narrative | Description |
| E | Debit | Negative amounts |
| F | Credit | Positive amounts |
| G | Closing Balance | Running balance |

- **Encoding**: UTF-8
- **Delimiter**: Comma
- **Header row**: Row 1
- **Date format**: YYYY-MM-DD (ISO format)
- **Special**: NCBA uses ISO dates (unlike other Kenyan banks)

### PDF Format

- **Tool**: tabula-py with `lattice=True`
- **Special handling**: Two-column layout on some statement types; use right column only
- **Currency**: May include USD statements for foreign currency accounts

---

## 4. Co-operative Bank

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Trans Date | Format: DD/MM/YYYY |
| B | Doc No | Document/reference number |
| C | Description | Transaction narrative |
| D | Amount | Signed amount (negative = debit) |
| E | Balance | Running balance |

- **Encoding**: Windows-1252 (convert to UTF-8)
- **Delimiter**: Comma
- **Header row**: Row 2 (row 1 is account number)
- **Date format**: DD/MM/YYYY
- **Special**: Uses single signed amount column instead of separate debit/credit
- **Conversion**: Negative amount -> debit, positive amount -> credit

### PDF Format

- **Tool**: tabula-py with `lattice=True`
- **Special**: Table borders are thick, may need area specification for accurate extraction

### Excel Format

- **Sheet**: First sheet
- **Header row**: Row 3
- **Special**: Amount column contains formatted numbers with currency symbol

---

## 5. Stanbic Bank

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Transaction Date | Format: DD MMM YYYY (e.g., 05 Apr 2026) |
| B | Value Date | Same format |
| C | Transaction Reference | Reference number |
| D | Description | Narrative |
| E | Debit Amount | With comma separators |
| F | Credit Amount | With comma separators |
| G | Balance | Running balance |

- **Encoding**: UTF-8
- **Delimiter**: Comma (amounts may contain commas, use proper CSV parsing)
- **Header row**: Row 1
- **Date format**: DD MMM YYYY (space-separated)
- **Special**: Amounts are quoted strings with comma thousand separators

### PDF Format

- **Tool**: tabula-py with `stream=True`
- **Special**: Uses colored row backgrounds; tabula handles this correctly

---

## 6. ABSA Kenya (formerly Barclays)

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Posting Date | Format: DD/MM/YYYY |
| B | Value Date | Format: DD/MM/YYYY |
| C | Description | Transaction narrative |
| D | Reference Number | Bank reference |
| E | Debit | Debit amount |
| F | Credit | Credit amount |
| G | Running Balance | Balance after transaction |

- **Encoding**: UTF-8
- **Delimiter**: Comma
- **Header row**: Row 1
- **Date format**: DD/MM/YYYY
- **Special**: Description may contain "ABSA" prefix codes (strip for matching)

### PDF Format

- **Tool**: tabula-py with `lattice=True`
- **Special**: ABSA statements have a distinctive green header; skip first table (summary)

### Excel Format

- **Sheet**: "Statement"
- **Header row**: Row 4
- **Special**: Contains macros (use `data_only=True` in openpyxl)

---

## 7. Standard Chartered

### CSV Format

| Column | Header | Notes |
|--------|--------|-------|
| A | Date | Format: DD-MM-YYYY |
| B | Description | Transaction narrative |
| C | Withdrawals | Debit amount |
| D | Deposits | Credit amount |
| E | Balance | Running balance |

- **Encoding**: UTF-8
- **Delimiter**: Comma
- **Header row**: Row 1
- **Date format**: DD-MM-YYYY
- **Special**: No separate reference column; reference embedded in description
- **Reference extraction**: Parse description for patterns like "REF:XXXXX" or M-Pesa codes

### PDF Format

- **Tool**: tabula-py with `stream=True`
- **Special**: Multi-currency statements; each currency in a separate table section
- **Currency detection**: Look for "KES", "USD", "EUR", "GBP" section headers

---

## Channel Detection from Description

Bank descriptions often encode the transaction channel. Use these patterns to extract the `channel` field:

| Pattern in Description | Channel |
|----------------------|---------|
| `MPESA`, `M-PESA`, `MOBILE` | `MPESA` |
| `EFT`, `ELECTRONIC FUNDS` | `EFT` |
| `CHQ`, `CHEQUE`, `CHECK` | `CHEQUE` |
| `POS`, `POINT OF SALE`, `CARD` | `POS` |
| `ATM`, `CASH WITHDRAWAL` | `ATM` |
| `RTGS`, `REAL TIME` | `RTGS` |
| `INT`, `INTEREST`, `CHG`, `FEE`, `CHARGE` | `INTERNAL` |
| `SWIFT`, `TT`, `WIRE` | `SWIFT` |

## Common Parsing Issues

| Issue | Solution |
|-------|----------|
| Password-protected PDFs | Prompt user for password, try account number as default |
| Scanned (image) PDFs | Route to OCR pipeline instead of tabula |
| Multi-currency statements | Parse each currency section separately, tag with currency |
| Wrapped descriptions | Merge rows where date column is empty with previous row |
| Inconsistent date formats | Try multiple parsers, validate parsed dates are within expected range |
| Encoded characters | Detect encoding with chardet, convert to UTF-8 |
