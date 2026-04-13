---
name: payroll
description: Payroll computation engine covering gross-to-net calculation, statutory deductions (PAYE, NSSF, NHIF, Housing Levy), payslip generation, and filing return outputs for Kenyan payroll compliance. Maps to Agent 10 (Payroll Computation Agent).
---

# Payroll Computation Skill

This skill implements the Payroll Computation Agent (Agent 10) — a pure computation engine with no LLM involvement. It executes a deterministic 7-step pipeline to calculate employee net pay and generate statutory filing outputs.

## Agent Mapping

- **Agent 10**: Payroll Computation Agent (pure computation, no LLM)

## 7-Step Computation Pipeline

### Step 1: Gross Pay

```
Gross = Basic Salary + House Allowance + Transport Allowance + Other Allowances
```

All allowance components are defined per employee in the payroll configuration.

### Step 2: NSSF Employee Contribution

```
NSSF Tier I  = 6% of first KES 7,000
NSSF Tier II = 6% of (Gross - 7,000), capped so total pensionable earnings do not exceed KES 36,000
```

Employer contribution mirrors employee contribution at matching rates.

### Step 3: Taxable Income

```
Taxable Income = Gross - NSSF Employee Contribution
```

NSSF is the only pre-tax deduction in the standard pipeline.

### Step 4: PAYE (Pay As You Earn)

Apply progressive tax bands to monthly taxable income, then subtract personal relief of KES 2,400/month. See `references/paye_brackets.md` for current bands.

```
PAYE = Tax from progressive bands - Personal Relief (2,400)
```

If PAYE computes to a negative value, it is set to zero.

### Step 5: NHIF Contribution

Lookup employee contribution from the graduated NHIF scale based on gross pay. See `references/statutory_rates.md` for the full scale.

### Step 6: Housing Levy

```
Housing Levy = 1.5% of Gross Pay
```

Employer also contributes 1.5% of gross pay.

### Step 7: Net Pay

```
Net Pay = Gross - PAYE - NSSF Employee - NHIF - Housing Levy - Other Deductions
```

Other deductions include loan repayments, SACCO contributions, salary advances, and any voluntary deductions configured per employee.

## Rate Configuration

All statutory rates, tax bands, and thresholds are stored as configuration records in the database — never hardcoded. This design allows same-day updates when Finance Bill changes are enacted, without requiring code deployment.

Rate configuration includes:
- PAYE progressive bands and personal relief amount
- NSSF tier thresholds and percentages
- NHIF graduated scale
- Housing Levy percentage
- NITA levy amount

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| Payslips | PDF/JSON | Per-employee breakdown of earnings and deductions |
| P10 CSV | CSV | PAYE return for KRA iTax upload |
| NSSF Schedule | CSV | NSSF contribution schedule for upload |
| NHIF Schedule | CSV | NHIF contribution schedule for upload |

## Filing Deadlines

| Return | Deadline | Penalty |
|--------|----------|---------|
| PAYE (P10) | 9th of following month | 25% of tax due or KES 10,000 (whichever is higher) |
| NSSF | 15th of following month | 5% penalty per month |
| NHIF | 9th of following month | 5x the contribution |

The system generates filing alerts based on these deadlines. See `references/filing_deadlines.md` for the complete schedule.
