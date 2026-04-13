# PAYE Progressive Tax Bands (Monthly)

## Current Bands

| Band | Monthly Income Range (KES) | Rate |
|------|---------------------------|------|
| 1 | First 24,000 | 10% |
| 2 | Next 8,333 (24,001 - 32,333) | 25% |
| 3 | Next 467,667 (32,334 - 500,000) | 30% |
| 4 | Next 300,000 (500,001 - 800,000) | 32.5% |
| 5 | Above 800,000 | 35% |

## Reliefs

| Relief | Monthly Amount (KES) |
|--------|---------------------|
| Personal Relief | 2,400 |
| Insurance Relief | 15% of premiums paid, maximum 5,000 |

## Computation Example

For a taxable income of KES 80,000/month:

```
Band 1: 24,000 x 10%     =  2,400
Band 2:  8,333 x 25%     =  2,083.25
Band 3: 47,667 x 30%     = 14,300.10
                    Total = 18,783.35
Less: Personal Relief     = -2,400.00
                     PAYE = 16,383.35
```

## Insurance Relief

Employees contributing to approved insurance policies (NHIF counts) may claim insurance relief:

- Rate: 15% of total premiums paid
- Maximum: KES 5,000 per month (KES 60,000 per year)
- NHIF contribution qualifies as an insurance premium for this relief

## Notes

- PAYE cannot be negative; minimum is zero
- Non-resident employees are taxed at a flat 30% with no personal relief
- Directors of private companies with >12.5% shareholding are subject to deemed interest benefit calculations
- All rates are stored in the database and can be updated without code changes when Finance Bill amendments take effect
