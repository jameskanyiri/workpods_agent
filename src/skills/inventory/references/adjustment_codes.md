# Stock Adjustment Reason Codes

Every stock adjustment requires a mandatory reason code. Adjustments without a reason code are rejected by the system.

## Reason Codes

| Code | Reason | Direction | Description |
|------|--------|-----------|-------------|
| ADJ-001 | Physical Count Variance | +/- | Difference found during physical stock count |
| ADJ-002 | Damaged Goods | - | Stock damaged in warehouse (write-off) |
| ADJ-003 | Expired Stock | - | Stock past expiry date (write-off) |
| ADJ-004 | Theft/Loss | - | Stock lost due to theft or unexplained shortage |
| ADJ-005 | Supplier Return | - | Goods returned to supplier (defective/wrong items) |
| ADJ-006 | Customer Return | + | Goods returned by customer |
| ADJ-007 | Production Consumption | - | Raw materials consumed in production |
| ADJ-008 | Production Output | + | Finished goods produced |
| ADJ-009 | Free Samples | - | Stock issued as promotional samples |
| ADJ-010 | Donation | - | Stock donated (charitable or promotional) |
| ADJ-011 | Opening Balance | + | Initial stock entry at system setup |
| ADJ-012 | Reclassification | +/- | Item reclassified to different category |
| ADJ-013 | Correction | +/- | Data entry error correction |
| ADJ-014 | Obsolescence | - | Stock declared obsolete (write-off) |
| ADJ-015 | Shrinkage | - | Natural loss due to evaporation, spillage, etc. |

## Required Fields Per Adjustment

| Field | Required | Description |
|-------|----------|-------------|
| reason_code | Yes | One of the codes above |
| quantity | Yes | Number of units (positive or negative) |
| notes | Yes | Free-text explanation |
| supporting_document | Conditional | Required for ADJ-004 (theft report), ADJ-005 (supplier credit note) |
| approved_by | Yes | User who authorized the adjustment |
| adjustment_date | Yes | Date of adjustment |

## Journal Entry Impact

| Adjustment Type | Debit | Credit |
|----------------|-------|--------|
| Stock increase (e.g., count surplus) | Inventory | Stock Adjustment Income |
| Stock decrease (e.g., damage, theft) | Stock Adjustment Expense | Inventory |
| Customer return | Inventory | Cost of Goods Sold |
| Supplier return | Accounts Payable | Inventory |

## Approval Requirements

- Adjustments below KES 10,000: single approval (warehouse manager)
- Adjustments KES 10,000 - 100,000: dual approval (warehouse manager + accountant)
- Adjustments above KES 100,000: triple approval (warehouse manager + accountant + director)
- All theft/loss adjustments (ADJ-004): require director approval regardless of amount

## Audit Trail

Every adjustment is logged with:
- User who initiated the adjustment
- User(s) who approved
- Timestamp of creation and approval
- Before and after quantities
- Before and after WAC values
- Reason code and notes
- Supporting document reference (if applicable)
