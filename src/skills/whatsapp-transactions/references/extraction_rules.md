# Extraction Rules for Kenyan Shorthand and M-Pesa References

## Amount Parsing

### Shorthand Multipliers

| Suffix | Multiplier | Examples |
|--------|-----------|----------|
| `k` or `K` | 1,000 | "5k" = 5,000; "12.5K" = 12,500; "250k" = 250,000 |
| `m` or `M` | 1,000,000 | "1m" = 1,000,000; "2.5M" = 2,500,000; "0.5m" = 500,000 |

### Amount Formats

| Format | Parsed Value | Notes |
|--------|-------------|-------|
| `5000` | 5,000.00 | Plain integer |
| `5,000` | 5,000.00 | Comma-separated |
| `5,000.50` | 5,000.50 | With decimals |
| `5k` | 5,000.00 | Shorthand |
| `5.5k` | 5,500.00 | Decimal shorthand |
| `1.2m` | 1,200,000.00 | Million shorthand |
| `KES 5000` | 5,000.00 | Currency prefix |
| `Ksh 5000` | 5,000.00 | Alternative currency prefix |
| `Kshs. 5,000` | 5,000.00 | Formal currency prefix |

### Multi-Amount Messages

When a message contains multiple amounts:
- If explicit line items (e.g., "bought A for 5k and B for 3k"), extract each as a separate line
- If one amount is clearly the total (e.g., "total 8k"), use it as the transaction amount
- If amounts are ambiguous, flag for clarification (confidence < 0.7)

## M-Pesa Transaction Codes

### Format

M-Pesa transaction codes follow the pattern: `[A-Z]{1}[A-Z0-9]{9}` (one letter followed by 9 alphanumeric characters, total 10 characters).

**Examples**: `SHK7X2M4LP`, `RAJ3B9K2NP`, `QCL8F5H1XR`

### Extraction Rules

1. Scan message for any 10-character alphanumeric string starting with a letter
2. Exclude common English words that match the pattern (unlikely at 10 chars)
3. Store as `reference` field in extracted data
4. If multiple codes found, use the first as primary reference, store others in `additional_references`

### Till Number / Paybill References

| Pattern | Type | Example |
|---------|------|---------|
| 6-digit number preceded by "till" | Till Number | "till 123456" |
| 5-7 digit number preceded by "paybill" | Paybill Number | "paybill 247247" |
| "account" followed by alphanumeric | Account Number | "account 001234" |

## Payment Method Detection

### Keywords to Payment Method Mapping

| Keywords | Payment Method |
|----------|---------------|
| `mpesa`, `m-pesa`, `pesa`, `safaricom`, `till`, `paybill`, `send money`, `lipa na` | `MPESA` |
| `cash`, `csh`, `notes`, `coins`, `petty cash` | `CASH` |
| `bank`, `bnk`, `transfer`, `eft`, `rtgs`, `swift`, `wire` | `BANK_TRANSFER` |
| `cheque`, `check`, `chq` | `CHEQUE` |
| `card`, `visa`, `mastercard`, `debit card`, `credit card`, `pos`, `swipe` | `CARD` |

### Priority

If multiple payment methods are mentioned, use the most specific one. "Paid supplier via bank then sent confirmation on mpesa" -> `BANK_TRANSFER` (bank is the actual payment method).

## Transaction Type Detection

| Keywords | Type |
|----------|------|
| `paid`, `bought`, `purchased`, `expense`, `spent`, `cost` | `EXPENSE` |
| `received`, `sold`, `revenue`, `income`, `collected`, `invoiced` | `REVENUE` |
| `transferred`, `moved`, `sent to account`, `deposit` | `TRANSFER` |
| `petty cash`, `imprest`, `float` | `PETTY_CASH` |

## Category Detection

### Common Kenyan SME Expense Categories

| Keywords | Category Code | Category Name |
|----------|--------------|---------------|
| `rent`, `office rent`, `shop rent` | `5200` | Rent & Lease |
| `salary`, `wages`, `pay`, `staff` | `5300` | Salaries & Wages |
| `fuel`, `petrol`, `diesel`, `gas` | `5410` | Fuel & Oil |
| `transport`, `fare`, `uber`, `bolt`, `matatu`, `boda` | `5420` | Transport |
| `food`, `lunch`, `tea`, `snacks`, `meals`, `catering` | `5430` | Meals & Entertainment |
| `stationery`, `office supplies`, `printing`, `toner` | `5100` | Office Supplies |
| `electricity`, `water`, `wifi`, `internet`, `airtime`, `data` | `5500` | Utilities |
| `repair`, `maintenance`, `fix`, `service` | `5600` | Repairs & Maintenance |
| `insurance` | `5700` | Insurance |
| `legal`, `lawyer`, `advocate` | `5810` | Legal Fees |
| `audit`, `accountant`, `accounting` | `5820` | Audit & Accounting |
| `marketing`, `ads`, `advertising`, `promo` | `5900` | Marketing & Advertising |

## Date Extraction

### Relative Dates

| Expression | Interpretation |
|------------|---------------|
| `today`, `leo` (Swahili) | Current date |
| `yesterday`, `jana` | Previous day |
| `last week` | Previous Monday |
| `last month` | 1st of previous month |
| No date mentioned | Default to current date |

### Explicit Date Formats

Supported formats: `DD/MM/YYYY`, `DD-MM-YYYY`, `DD.MM.YYYY`, `YYYY-MM-DD`, `D MMM YYYY` (e.g., "5 Apr 2026").

Note: Kenyan convention is DD/MM/YYYY (day first), not MM/DD/YYYY.

## Vendor/Customer Extraction

1. Look for proper nouns following payment verbs ("paid **Jumia**", "received from **Kamau**")
2. Match against known vendor/customer list from the company's database
3. If no match found, create a candidate name and flag for confirmation
4. Handle common formats: "Supplier X", company names, personal names, till/paybill business names
