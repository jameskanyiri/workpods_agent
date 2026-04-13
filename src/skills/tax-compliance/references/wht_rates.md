# Withholding Tax (WHT) Rates

## Rates by Payment Category

| Payment Category | Resident Rate | Non-Resident Rate |
|-----------------|--------------|-------------------|
| Professional / Management / Training fees | 5% | 20% |
| Contractual fees | 3% | 20% |
| Consultancy fees | 5% | 20% |
| Dividends | 5% | 15% |
| Interest (financial institutions) | 15% | 15% |
| Interest (bearer instruments) | 25% | 25% |
| Royalties | 5% | 20% |
| Rent (immovable property) | 10% | 30% |
| Insurance commission | 5% | 20% |
| Appearance/performance fees | 5% | 20% |
| Telecommunication services | - | 5% |
| Natural resource income | - | 20% |

## Computation Examples

### Example 1: Professional Fee (Resident)

```
Invoice amount: KES 100,000 (inclusive of professional fee)
WHT: 100,000 x 5% = KES 5,000
Amount paid to vendor: KES 95,000
WHT remitted to KRA: KES 5,000
```

### Example 2: Rent Payment (Resident)

```
Monthly rent: KES 200,000
WHT: 200,000 x 10% = KES 20,000
Amount paid to landlord: KES 180,000
WHT remitted to KRA: KES 20,000
```

### Example 3: Consultancy Fee (Non-Resident)

```
Invoice amount: KES 500,000
WHT: 500,000 x 20% = KES 100,000
Amount paid to consultant: KES 400,000
WHT remitted to KRA: KES 100,000
```

## WHT on VAT-Inclusive Amounts

When the payment is VAT-inclusive, WHT is computed on the pre-VAT amount:

```
VAT-inclusive invoice: KES 116,000
Pre-VAT amount: 116,000 / 1.16 = KES 100,000
WHT (5% professional): 100,000 x 5% = KES 5,000
VAT: KES 16,000
Amount paid: 116,000 - 5,000 = KES 111,000
```

## Filing Requirements

- WHT is remitted to KRA by the 20th of the following month
- WHT certificates must be issued to vendors upon deduction
- Annual WHT returns are filed as part of the corporate tax return
- Non-remittance attracts 5% penalty plus 1% monthly interest

## System Behavior

- WHT category is assigned per vendor in the vendor master
- The system automatically computes WHT on qualifying payments
- WHT certificates are generated and available for vendor download
- Monthly WHT summaries are prepared for iTax upload
