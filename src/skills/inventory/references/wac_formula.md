# Weighted Average Cost (WAC) Formula

## Formula

```
New WAC = (existing_qty x existing_WAC + purchase_qty x purchase_unit_cost) / (existing_qty + purchase_qty)
```

WAC is recalculated on every purchase. It is NOT recalculated on sales or other issues.

## Example 1: Initial Purchase

Starting inventory: 0 units

```
Purchase: 100 units at KES 50 each

New WAC = (0 x 0 + 100 x 50) / (0 + 100)
        = 5,000 / 100
        = KES 50.00
```

Stock on hand: 100 units at WAC KES 50.00

## Example 2: Sale (No WAC Change)

Stock on hand: 100 units at WAC KES 50.00

```
Sale: 30 units

COGS = 30 x 50.00 = KES 1,500.00
WAC remains KES 50.00 (unchanged by sales)
```

Stock on hand: 70 units at WAC KES 50.00

## Example 3: Second Purchase at Different Price

Stock on hand: 70 units at WAC KES 50.00

```
Purchase: 50 units at KES 60 each

New WAC = (70 x 50 + 50 x 60) / (70 + 50)
        = (3,500 + 3,000) / 120
        = 6,500 / 120
        = KES 54.1667
```

Stock on hand: 120 units at WAC KES 54.1667

## Example 4: Another Sale

Stock on hand: 120 units at WAC KES 54.1667

```
Sale: 40 units

COGS = 40 x 54.1667 = KES 2,166.67
WAC remains KES 54.1667
```

Stock on hand: 80 units at WAC KES 54.1667

## Example 5: Purchase with Landed Costs

When purchase includes freight, insurance, or customs duty, these are added to the unit cost:

```
Purchase: 200 units at KES 45 each
Freight: KES 1,000
Insurance: KES 500
Total landed cost: (200 x 45) + 1,000 + 500 = KES 10,500
Effective unit cost: 10,500 / 200 = KES 52.50
```

Then apply the WAC formula using KES 52.50 as the purchase unit cost.

## Edge Cases

### Zero Existing Stock

When existing quantity is zero, the new WAC equals the purchase unit cost:

```
New WAC = (0 x 0 + qty x cost) / (0 + qty) = cost
```

### Purchase Returns

Purchase returns reduce both quantity and value. WAC is recalculated:

```
Adjusted WAC = (current_qty x current_WAC - return_qty x return_cost) / (current_qty - return_qty)
```

### Precision

WAC is stored to 4 decimal places (KES 54.1667, not KES 54.17) to prevent cumulative rounding errors over many transactions.
