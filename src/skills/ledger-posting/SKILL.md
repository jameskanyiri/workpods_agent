---
name: ledger-posting
description: ACID-compliant ledger posting engine with INSERT-only journal entries, PostgreSQL-enforced DR=CR balance validation, running balance maintenance, and period state machine. Maps to Agent 18 (Ledger Posting Agent) — the ONLY agent with write access to journal_entries and ledger_lines.
---

# Ledger Posting Skill

This skill implements the Ledger Posting Agent (Agent 18) — the sole agent in the 22-agent architecture with write access to `journal_entries` and `ledger_lines` tables. No other agent can create, modify, or delete accounting records.

## Agent Mapping

- **Agent 18**: Ledger Posting Agent (exclusive write access to journal_entries and ledger_lines)

## ACID Transaction Flow

Every journal entry is posted within a single PostgreSQL transaction:

```
1. BEGIN TRANSACTION
2. INSERT into journal_entries (status = 'POSTED')
3. INSERT into ledger_lines (one per account affected)
4. PostgreSQL trigger validates SUM(debit) = SUM(credit) for this entry
5. UPDATE running_balance on each affected account
6. INSERT into audit_trail (user, timestamp, action, details)
7. COMMIT
```

If any step fails, the entire transaction rolls back. No partial postings can exist.

### Validation Trigger

A PostgreSQL trigger on `ledger_lines` fires after insert and checks:

```sql
SELECT SUM(debit_amount) - SUM(credit_amount)
FROM ledger_lines
WHERE journal_entry_id = NEW.journal_entry_id;
```

If the result is not zero, the trigger raises an exception and the transaction rolls back.

## Security Model: INSERT-Only Permissions

The Ledger Posting Agent's database role has strictly limited permissions:

```sql
GRANT INSERT ON journal_entries TO ledger_posting_role;
GRANT INSERT ON ledger_lines TO ledger_posting_role;
GRANT INSERT ON audit_trail TO ledger_posting_role;
GRANT UPDATE (running_balance) ON accounts TO ledger_posting_role;
-- No UPDATE on journal_entries or ledger_lines
-- No DELETE on any table
```

Even if the agent is compromised, it cannot modify or delete existing records.

## Append-Only Enforcement

PostgreSQL triggers enforce the append-only model:

```sql
CREATE TRIGGER prevent_ledger_modification
BEFORE UPDATE OR DELETE ON ledger_lines
FOR EACH ROW EXECUTE FUNCTION raise_immutable_error();

CREATE TRIGGER prevent_journal_modification
BEFORE UPDATE OR DELETE ON journal_entries
FOR EACH ROW EXECUTE FUNCTION raise_immutable_error();
```

These triggers block any UPDATE or DELETE operation at the database level, regardless of which user or application attempts it.

### Corrections

Errors are corrected by posting a reversing journal entry, never by modifying the original:

1. Post a reversing entry (swap debits and credits of the original)
2. Post the correct entry
3. Both the original and correction remain in the ledger permanently

## Period State Machine

Accounting periods follow a strict state machine. See `references/period_states.md` for transition rules.

```
OPEN --> SOFT_CLOSED --> HARD_CLOSED --> LOCKED
```

| State | Posting Allowed | Who Can Transition |
|-------|----------------|-------------------|
| OPEN | Yes, all entries | Accountant |
| SOFT_CLOSED | Adjusting entries only (flagged) | Accountant |
| HARD_CLOSED | No new entries | Manager/Director |
| LOCKED | No changes whatsoever | System (after audit) |

## Journal Entry Structure

Each journal entry contains:

| Field | Description |
|-------|-------------|
| id | UUID primary key |
| entry_date | Date of the transaction |
| reference | Source document reference |
| narration | Description of the transaction |
| source_agent | Which agent requested the posting |
| source_document_type | Invoice, payment, receipt, adjustment, etc. |
| source_document_id | FK to the originating document |
| status | Always POSTED (no draft state at ledger level) |
| created_at | Timestamp of posting |
| created_by | User/agent that initiated the posting |

Each ledger line contains:

| Field | Description |
|-------|-------------|
| id | UUID primary key |
| journal_entry_id | FK to journal_entries |
| account_id | FK to chart of accounts |
| debit_amount | Debit amount (0 if credit line) |
| credit_amount | Credit amount (0 if debit line) |
| running_balance | Account balance after this line |

## Audit Trail

Every posting generates an audit trail entry:

| Field | Description |
|-------|-------------|
| action | JOURNAL_POSTED |
| journal_entry_id | FK to the posted entry |
| user_id | Who initiated the action |
| agent_id | Which agent requested posting |
| timestamp | When the action occurred |
| ip_address | Origin of the request |
| details | JSON with full entry details |

See `references/posting_rules.md` for ACID requirements and rollback conditions.
