---
name: tax-compliance
description: Tax computation, verification, and eTIMS submission covering VAT, WHT, corporate tax, and KRA filing. Maps to Agent 11 (Tax Computation), Agent 14 (Tax Logic Verification), and Agent 19 (eTIMS Submission).
---

# Tax Compliance Skill

This skill implements three agents that work together to compute, verify, and submit tax obligations to KRA:

## Agent Mapping

- **Agent 11**: Tax Computation Agent (pure computation, no LLM)
- **Agent 14**: Tax Logic Verification Agent (validation rules)
- **Agent 19**: eTIMS Submission Agent (KRA integration)

## VAT Computation (Agent 11)

```
Output VAT (from sales invoices)
- Input VAT (from purchase invoices)
= VAT-3 Liability (or refund if negative)
```

VAT categories determine how each line item is treated:
- **Standard rated (16%)**: Most goods and services
- **Zero-rated (0%)**: Exports, basic foodstuffs listed in First Schedule
- **Exempt**: Financial services, education, healthcare, unprocessed agricultural products

See `references/vat_rates.md` for full categorization.

## WHT Computation (Agent 11)

Withholding Tax is computed by summing all WHT withheld on vendor payments, grouped by WHT category:

| Category | Resident Rate | Non-Resident Rate |
|----------|--------------|-------------------|
| Professional/Management fees | 5% | 20% |
| Contractual fees | 3% | 20% |
| Dividends | 5% | 15% |
| Interest | 15% | 15% |
| Royalties | 5% | 20% |
| Rent (immovable property) | 10% | 30% |

See `references/wht_rates.md` for complete rates and examples.

## Corporate Tax Estimation (Agent 11)

```
Estimated Corporate Tax = Current Period Net Income x Applicable Rate (30% standard)
```

Computed as a running estimate for instalment tax purposes. Actual corporate tax is finalized at year-end with full adjustments.

## Tax Logic Verification (Agent 14)

Every tax computation passes through verification before posting:

1. **VAT rate check**: VAT charged equals 16% of the pre-VAT amount for standard-rated items
2. **WHT rate check**: WHT rate matches the vendor's payment category and residency status
3. **KRA PIN validation**: Vendor's KRA PIN format is valid (P/A prefix + 9 digits + letter suffix)
4. **PIN existence check**: Vendor PIN exists in KRA's iTax system (cached lookup)
5. **Cross-period check**: Invoice date falls within the return period being filed
6. **Duplicate check**: No duplicate invoice numbers for the same vendor in the same period

Verification failures block posting and route to human review.

## eTIMS Submission (Agent 19)

The eTIMS submission pipeline handles all interactions with KRA's electronic Tax Invoice Management System:

### Submission Flow

```
1. Validate payload (all required fields present, formats correct)
2. Submit to VSCU (Virtual Sales Control Unit)
3. Receive control number and QR code from VSCU
4. Stamp invoice with control number and QR
5. Store stamped invoice and VSCU response
```

### Retry Logic (Exponential Backoff)

If submission fails, retry with exponential backoff:

| Attempt | Wait Time |
|---------|-----------|
| 1 | 1 minute |
| 2 | 5 minutes |
| 3 | 15 minutes |
| 4 | 1 hour |
| 5 | 6 hours |

### Offline Mode

If KRA systems are down for more than 6 hours:
- Switch to offline mode
- Queue invoices locally with sequential offline numbers
- Auto-submit queued invoices when connectivity is restored
- Reconcile offline numbers with VSCU control numbers

See `references/etims_api.md` for API details.

## Filing Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| VAT-3 Return | CSV | KRA iTax |
| P10 PAYE Return | CSV | KRA iTax |
| WHT Return | CSV/XML | KRA iTax |
| eTIMS Invoices | JSON | KRA VSCU |

See `references/filing_calendar.md` for all KRA filing deadlines and penalties.
