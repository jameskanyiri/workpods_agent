# Posting Rules and ACID Requirements

## ACID Compliance

All ledger postings must satisfy ACID properties:

### Atomicity

The entire journal entry (header + all lines + balance updates + audit log) is a single PostgreSQL transaction. Either everything commits or everything rolls back. There is no intermediate state.

### Consistency

- Every journal entry must balance: `SUM(debits) = SUM(credits)`
- Running balances are updated within the same transaction
- Account types enforce sign conventions (assets/expenses = debit normal, liabilities/equity/revenue = credit normal)

### Isolation

- Transactions use `SERIALIZABLE` isolation level for balance-sensitive operations
- Concurrent postings to the same account are serialized to prevent running balance race conditions

### Durability

- All committed transactions are persisted to PostgreSQL WAL (Write-Ahead Log)
- Point-in-time recovery is available through WAL archiving

## Rollback Conditions

The transaction rolls back automatically if any of these conditions occur:

| Condition | Error Code | Description |
|-----------|-----------|-------------|
| Unbalanced entry | ERR-001 | SUM(debits) != SUM(credits) |
| Invalid account | ERR-002 | Account ID does not exist in chart of accounts |
| Closed period | ERR-003 | Target period is HARD_CLOSED or LOCKED |
| Inactive account | ERR-004 | Account is marked inactive |
| Negative balance | ERR-005 | Resulting balance would be negative on a non-negative account (e.g., bank) |
| Duplicate reference | ERR-006 | Same source_document_id already posted |
| Missing narration | ERR-007 | Narration field is empty |
| Future date | ERR-008 | Entry date is in the future |
| Zero amount | ERR-009 | All line amounts are zero |
| Currency mismatch | ERR-010 | Multi-currency entry has mismatched base amounts |

## Posting Validation Checklist

Before initiating the PostgreSQL transaction, the agent validates:

1. Entry date falls within an OPEN or SOFT_CLOSED period
2. All account IDs exist and are active
3. Debits equal credits (pre-check before trigger)
4. Source document has not already been posted (idempotency)
5. Narration is not empty
6. At least two ledger lines exist (minimum for double-entry)
7. No line has both debit and credit amounts > 0

## Correction Procedure

Since UPDATE and DELETE are blocked at the trigger level, corrections follow this process:

1. **Identify** the erroneous entry by journal_entry_id
2. **Create a reversing entry** that swaps all debits and credits from the original
3. **Post the correct entry** with the intended amounts
4. **Link** all three entries (original, reversal, correction) via a correction_group_id
5. **Document** the reason for correction in the narration

The original entry is never modified. The full correction chain is visible in the audit trail.

## Concurrent Posting Safety

- Row-level locks are acquired on affected account running_balance rows
- If two postings affect the same account simultaneously, one waits for the other to commit
- Deadlock detection is handled by PostgreSQL with automatic retry (up to 3 attempts)
