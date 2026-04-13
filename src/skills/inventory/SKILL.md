---
name: inventory
description: Inventory management using Weighted Average Cost (WAC) method with perpetual updates on purchases, COGS recognition on sales, reorder alerts, inter-branch transfers, and adjustment logging. Maps to Agent 12 (Inventory Agent).
---

# Inventory Skill

This skill implements the Inventory Agent (Agent 12) — a pure computation engine with no LLM involvement. It maintains accurate inventory valuations using the Weighted Average Cost method and handles all stock movement operations.

## Agent Mapping

- **Agent 12**: Inventory Agent (pure computation, no LLM)

## Weighted Average Cost (WAC) Formula

```
New WAC = (existing_qty x existing_WAC + purchase_qty x purchase_unit_cost) / (existing_qty + purchase_qty)
```

WAC is recalculated perpetually on every purchase transaction. See `references/wac_formula.md` for worked examples.

## Core Operations

### Purchase Receipt

When goods are received:

1. Validate purchase order exists and is approved
2. Record received quantity against PO line
3. Recalculate WAC using the formula above
4. Update stock quantity on hand
5. Generate journal entry: DR Inventory, CR Accounts Payable
6. Check if reorder alerts should be cleared

### Sales / COGS Recognition

When goods are sold:

1. Verify sufficient stock on hand
2. Calculate COGS at current WAC: `COGS = qty_sold x current_WAC`
3. Reduce stock quantity on hand
4. Generate journal entry: DR Cost of Goods Sold, CR Inventory
5. WAC is not recalculated on sales (only on purchases)

### Reorder Point Checking

Each inventory item has configurable reorder parameters:

| Parameter | Description |
|-----------|-------------|
| reorder_point | Quantity threshold that triggers an alert |
| reorder_qty | Suggested quantity to reorder |
| lead_time_days | Expected supplier delivery time |
| safety_stock | Minimum buffer stock |

When stock on hand falls to or below the reorder point, the system:
1. Generates a reorder alert notification
2. Creates a draft purchase order (if auto-PO is enabled)
3. Notifies the procurement contact

### Inter-Branch Transfers

For businesses with multiple locations:

1. Initiate transfer from source branch
2. Reduce source branch stock: DR In-Transit Inventory, CR Source Branch Inventory
3. Goods are tracked as "in transit"
4. Receive at destination branch: DR Destination Branch Inventory, CR In-Transit Inventory
5. Transfer uses the WAC of the source branch at time of dispatch
6. Both branches' stock records are updated

### Stock Adjustments

All adjustments require a mandatory reason code. See `references/adjustment_codes.md` for the complete list.

Adjustment flow:
1. Record adjustment quantity (positive or negative)
2. Attach mandatory reason code
3. Capture supporting notes/evidence
4. Generate journal entry: DR/CR Inventory, CR/DR Stock Adjustment Expense
5. Log in audit trail with user, timestamp, and reason

## Inventory Reports

| Report | Description |
|--------|-------------|
| Stock Valuation | Current quantity and WAC value per item |
| Stock Movement | All receipts, issues, transfers, and adjustments |
| Reorder Report | Items at or below reorder point |
| Aging Report | Stock age based on receipt dates |
| COGS Report | Cost of goods sold by period and item |

## Data Integrity

- All stock movements create audit trail entries
- Negative stock is blocked by default (configurable per item)
- WAC is stored to 4 decimal places to prevent rounding drift
- Physical count reconciliation is supported with variance reporting
