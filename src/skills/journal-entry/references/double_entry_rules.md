# Debit and Credit Rules by Transaction Type

## Fundamental Rules

| Account Type | Increase | Decrease | Normal Balance |
|-------------|----------|----------|---------------|
| Assets | Debit | Credit | Debit |
| Liabilities | Credit | Debit | Credit |
| Equity | Credit | Debit | Credit |
| Revenue | Credit | Debit | Credit |
| Expenses | Debit | Credit | Debit |

## Common Transaction Patterns

### 1. Cash Purchase (No VAT)

**Scenario**: Buy office supplies for KES 5,000 cash

| Account | Debit | Credit |
|---------|-------|--------|
| 5100 Office Supplies | 5,000 | |
| 1050 Petty Cash | | 5,000 |

### 2. Cash Purchase (With VAT)

**Scenario**: Buy office supplies for KES 5,000 inclusive of 16% VAT

| Account | Debit | Credit |
|---------|-------|--------|
| 5100 Office Supplies | 4,310.34 | |
| 2200 VAT Input | 689.66 | |
| 1050 Petty Cash | | 5,000 |

**VAT calculation**: Amount excl. VAT = 5,000 / 1.16 = 4,310.34; VAT = 5,000 - 4,310.34 = 689.66

### 3. Credit Purchase (Supplier Invoice)

**Scenario**: Receive invoice from supplier for KES 50,000 + VAT

| Account | Debit | Credit |
|---------|-------|--------|
| 5050 Raw Materials | 50,000 | |
| 2200 VAT Input | 8,000 | |
| 2000 Accounts Payable | | 58,000 |

### 4. Payment to Supplier (No WHT)

**Scenario**: Pay supplier invoice of KES 58,000 via bank

| Account | Debit | Credit |
|---------|-------|--------|
| 2000 Accounts Payable | 58,000 | |
| 1000 Bank - Main | | 58,000 |

### 5. Payment to Supplier (With WHT)

**Scenario**: Pay management consultant KES 100,000 + VAT, deduct 5% WHT

| Account | Debit | Credit |
|---------|-------|--------|
| 5830 Consultancy Fees | 100,000 | |
| 2200 VAT Input | 16,000 | |
| 2300 WHT Payable | | 5,000 |
| 1000 Bank - Main | | 111,000 |

**WHT**: 5% on gross amount (excl. VAT) = 100,000 * 0.05 = 5,000
**Net payment**: 100,000 + 16,000 - 5,000 = 111,000

### 6. Cash Sale (With VAT)

**Scenario**: Sell goods for KES 20,000 inclusive of VAT, received via M-Pesa

| Account | Debit | Credit |
|---------|-------|--------|
| 1110 M-Pesa Float | 20,000 | |
| 4000 Sales Revenue | | 17,241.38 |
| 2210 VAT Output | | 2,758.62 |

### 7. Credit Sale

**Scenario**: Issue invoice to customer for KES 100,000 + VAT

| Account | Debit | Credit |
|---------|-------|--------|
| 1100 Accounts Receivable | 116,000 | |
| 4000 Sales Revenue | | 100,000 |
| 2210 VAT Output | | 16,000 |

### 8. Receipt from Customer

**Scenario**: Customer pays outstanding invoice of KES 116,000

| Account | Debit | Credit |
|---------|-------|--------|
| 1000 Bank - Main | 116,000 | |
| 1100 Accounts Receivable | | 116,000 |

### 9. Salary Payment

**Scenario**: Monthly salary KES 100,000 gross

| Account | Debit | Credit |
|---------|-------|--------|
| 5300 Salaries & Wages | 100,000 | |
| 5310 Employer NSSF | 2,160 | |
| 5320 Employer NHIF/SHIF | (per table) | |
| 5330 Employer Housing Levy | 1,500 | |
| 2100 PAYE Payable | | (calculated per bands) |
| 2110 NSSF Payable | | 4,320 |
| 2120 NHIF/SHIF Payable | | (per table) |
| 2130 Housing Levy Payable | | 3,000 |
| 1000 Bank - Main | | (net pay + employer contributions) |

**NSSF**: Employee 6% (max Tier I KES 420 + Tier II), Employer matches
**Housing Levy**: Employee 1.5%, Employer 1.5%

### 10. Rent Payment (With WHT)

**Scenario**: Pay monthly rent KES 100,000 inclusive of VAT, deduct 10% WHT

| Account | Debit | Credit |
|---------|-------|--------|
| 5200 Rent & Lease | 86,207 | |
| 2200 VAT Input | 13,793 | |
| 2310 WHT Payable - Rent | | 10,000 |
| 1000 Bank - Main | | 90,000 |

**WHT on rent**: 10% on gross (excl. VAT) = 86,207 * 0.10 = 8,621 (or 10% on gross inclusive depending on lease terms)

### 11. Petty Cash Replenishment

**Scenario**: Withdraw KES 20,000 from bank to replenish petty cash

| Account | Debit | Credit |
|---------|-------|--------|
| 1050 Petty Cash | 20,000 | |
| 1000 Bank - Main | | 20,000 |

### 12. Bank Charge

**Scenario**: Bank deducts KES 500 monthly maintenance fee

| Account | Debit | Credit |
|---------|-------|--------|
| 5910 Bank Charges | 500 | |
| 1000 Bank - Main | | 500 |

### 13. Depreciation Entry

**Scenario**: Monthly depreciation on motor vehicle (cost KES 2,000,000, 5 years straight-line)

| Account | Debit | Credit |
|---------|-------|--------|
| 5920 Depreciation Expense | 33,333 | |
| 1321 Motor Vehicles - Accum. Depreciation | | 33,333 |

### 14. VAT Payment to KRA

**Scenario**: Monthly VAT remittance (output KES 50,000 - input KES 30,000 = net KES 20,000)

| Account | Debit | Credit |
|---------|-------|--------|
| 2210 VAT Output | 50,000 | |
| 2200 VAT Input | | 30,000 |
| 1000 Bank - Main | | 20,000 |

### 15. Foreign Currency Receipt

**Scenario**: Receive USD 1,000 from export client (rate: KES 129/USD)

| Account | Debit | Credit |
|---------|-------|--------|
| 1020 Bank - USD Account | 129,000 | |
| 4000 Sales Revenue | | 129,000 |

### 16. Bad Debt Write-Off

**Scenario**: Write off uncollectable receivable of KES 25,000

| Account | Debit | Credit |
|---------|-------|--------|
| 5930 Bad Debts Expense | 25,000 | |
| 1100 Accounts Receivable | | 25,000 |

## Anti-Patterns (Common Errors)

| Error | Example | Why It Is Wrong |
|-------|---------|----------------|
| Debiting revenue | DR 4000 Sales Revenue | Revenue increases with credit, not debit (unless recording a return) |
| Crediting expense | CR 5100 Office Supplies | Expenses increase with debit (unless reversing an entry) |
| Same account both sides | DR 1000 Bank, CR 1000 Bank | Self-referencing entry has no economic meaning |
| Missing VAT on taxable purchase | DR 5200 Rent 100,000; CR 1000 Bank 100,000 | VAT input not captured; underreports claimable VAT |
| Missing WHT on professional fees | DR 5800 Prof Fees 50,000; CR 1000 Bank 50,000 | WHT not deducted; company liable for unremitted WHT |
