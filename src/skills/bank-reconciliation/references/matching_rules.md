# 5-Rule Cascade Matching Engine

## Overview

The bank reconciliation matching engine uses a cascade of five rules, applied in order from most strict to most permissive. The first rule that produces a match wins. This approach maximizes accuracy while ensuring most transactions can be automatically reconciled.

## Rule 1: Exact Match (Confidence: 99%)

### Criteria

All three conditions must be met:
- **Amount**: Bank amount exactly equals book amount (to the cent)
- **Date**: Bank transaction date exactly equals book entry date
- **Reference**: Bank reference string contains the book entry reference (or vice versa)

### Reference Matching

References are normalized before comparison:
- Strip whitespace and special characters
- Convert to uppercase
- M-Pesa codes: extract 10-character alphanumeric code
- Cheque numbers: extract numeric portion
- EFT references: extract bank reference number

### Example

```
Bank:  2026-04-05 | KES 5,000.00 | MPESA/SHK7X2M4LP/JOHN DOE
Book:  2026-04-05 | KES 5,000.00 | M-Pesa payment ref SHK7X2M4LP
Result: MATCH (Rule 1, 99% confidence)
```

## Rule 2: M-Pesa ID Match (Confidence: 97%)

### Criteria

All three conditions must be met:
- **Amount**: Bank amount exactly equals book amount
- **Date**: Bank date within +/- 3 calendar days of book date
- **M-Pesa ID**: Both contain the same M-Pesa transaction code

### Date Tolerance Rationale

M-Pesa transactions may be recorded in the books on a different day than the bank processes them (e.g., late evening transactions, weekend processing, or delayed data entry by the user).

### Example

```
Bank:  2026-04-07 | KES 12,500.00 | MPESA/RAJ3B9K2NP/SUPPLIER ABC
Book:  2026-04-05 | KES 12,500.00 | Paid Supplier ABC M-Pesa RAJ3B9K2NP
Result: MATCH (Rule 2, 97% confidence - date differs by 2 days)
```

## Rule 3: Description Similarity Match (Confidence: 90%)

### Criteria

All three conditions must be met:
- **Amount**: Bank amount exactly equals book amount
- **Date**: Bank date within +/- 7 calendar days of book date
- **Description similarity**: Cosine similarity > 0.85 using MiniLM-L6-v2 embeddings

### Similarity Computation

1. Preprocess descriptions: lowercase, remove common bank prefixes ("MPESA/", "EFT/", "CHQ/"), remove transaction codes
2. Generate sentence embeddings using `all-MiniLM-L6-v2`
3. Compute cosine similarity between the two embedding vectors
4. Threshold: 0.85

### Example

```
Bank:  2026-04-03 | KES 45,000.00 | EFT/RENT PAYMENT APRIL 2026
Book:  2026-04-01 | KES 45,000.00 | Office rent for April 2026
Cosine similarity: 0.89
Result: MATCH (Rule 3, 90% confidence)
```

## Rule 4: Fuzzy Approximate Match (Confidence: 80%)

### Criteria

All three conditions must be met:
- **Amount**: Bank amount within +/- 2% of book amount
- **Date**: Bank date within +/- 7 calendar days of book date
- **Description**: Fuzzy string ratio > 0.8 using rapidfuzz `token_sort_ratio`

### Amount Tolerance Rationale

The 2% tolerance accounts for:
- Bank charges added to transfers
- Currency conversion rounding
- Minor fee deductions
- Rounding differences between systems

### Fuzzy Matching Method

Uses `rapidfuzz.fuzz.token_sort_ratio` which:
1. Tokenizes both strings (split by whitespace)
2. Sorts tokens alphabetically
3. Computes Levenshtein-based similarity ratio
4. Returns score 0-100 (threshold: 80)

### Example

```
Bank:  2026-04-06 | KES 10,200.00 | MPESA/QCL8F5H1XR/OFFICE SUPPLIES
Book:  2026-04-05 | KES 10,000.00 | Office supplies purchase M-Pesa
Amount difference: 2.0% (within tolerance)
Fuzzy ratio: 0.83
Result: MATCH (Rule 4, 80% confidence - likely KES 200 bank charge)
```

## Rule 5: Unmatched (No Confidence)

### Criteria

Transaction did not match under any of Rules 1-4.

### Actions

1. Flag the transaction for human review
2. Generate suggested matches (top 3 candidates with scores below threshold)
3. Categorize the unmatched item:

| Category | Description | Common Causes |
|----------|-------------|---------------|
| `BANK_CHARGE` | Bank-side fees not recorded in books | Monthly maintenance, transfer fees, ATM charges |
| `TIMING_DIFFERENCE` | Transaction in transit | Cheques not yet cleared, pending transfers |
| `MISSING_ENTRY` | No corresponding book entry exists | Forgotten to record, auto-debits not captured |
| `DUPLICATE` | Possible duplicate in bank or books | System glitch, double-posting |
| `UNKNOWN` | Cannot determine cause | Requires investigation |

### Example

```
Bank:  2026-03-29 | KES 2,500.00 | CHG/MONTHLY MAINTENANCE FEE
Book:  No match found
Category: BANK_CHARGE
Action: Auto-suggest journal entry to record bank charge
```

## Performance Optimizations

### Indexing Strategy

- Primary index: amount (hash map for O(1) exact lookup)
- Secondary index: date range (sorted list for range queries)
- Pre-filter: only compare transactions within the same calendar month (+/- 7 days at boundaries)

### Batch Processing

- Process statements in monthly batches
- Cache embeddings for book entries (regenerate only when entries change)
- Parallel processing: Rules 1-2 are fast (no ML), run first; Rules 3-4 (require embeddings) run only on remaining unmatched items

### Expected Performance

| Statement Size | Processing Time | Match Rate |
|---------------|-----------------|------------|
| < 100 transactions | < 5 seconds | 90-95% |
| 100-500 transactions | < 15 seconds | 88-93% |
| 500-1000 transactions | < 45 seconds | 85-90% |
| > 1000 transactions | < 2 minutes | 82-88% |
