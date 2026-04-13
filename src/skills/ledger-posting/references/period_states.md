# Period State Machine

## States

```
OPEN --> SOFT_CLOSED --> HARD_CLOSED --> LOCKED
```

### OPEN

- All journal entries can be posted
- Normal day-to-day operations
- Any authorized agent can request postings
- Default state for the current accounting period

### SOFT_CLOSED

- Only adjusting entries are allowed (must be flagged as `is_adjusting = true`)
- Used during month-end/year-end close process
- Allows accountant to post accruals, provisions, and corrections
- Regular transaction postings are rejected

### HARD_CLOSED

- No new entries of any kind are accepted
- Financial statements for this period are considered final
- Can only be set by a user with Manager or Director role
- Used after management review of period financials

### LOCKED

- Absolutely no changes are possible
- Set automatically after external audit sign-off
- Cannot be reversed or reopened by any user
- Represents the permanent, audited state of the period

## Transition Rules

| From | To | Who Can Trigger | Conditions |
|------|-----|----------------|------------|
| OPEN | SOFT_CLOSED | Accountant | All bank reconciliations complete, no unposted transactions in queue |
| SOFT_CLOSED | OPEN | Accountant | Reopening is logged in audit trail with reason |
| SOFT_CLOSED | HARD_CLOSED | Manager/Director | All adjusting entries posted, trial balance reviewed |
| HARD_CLOSED | SOFT_CLOSED | Director only | Exceptional circumstances, logged with mandatory reason |
| HARD_CLOSED | LOCKED | System | Triggered by audit sign-off confirmation |
| LOCKED | (none) | N/A | Terminal state, no transitions out |

## Backward Transitions

Moving a period backward in the state machine is restricted:

- **SOFT_CLOSED to OPEN**: Allowed for the accountant, but logged with a mandatory reason. Used when additional transactions are discovered.
- **HARD_CLOSED to SOFT_CLOSED**: Requires Director approval. Used only in exceptional circumstances such as material errors found after close. Triggers a notification to all stakeholders.
- **LOCKED**: Cannot be reopened under any circumstances. If corrections are needed for a locked period, they must be posted as prior-period adjustments in the current open period.

## Period Structure

| Field | Description |
|-------|-------------|
| id | UUID primary key |
| period_name | e.g., "2024-01" for January 2024 |
| start_date | First day of the period |
| end_date | Last day of the period |
| state | OPEN, SOFT_CLOSED, HARD_CLOSED, or LOCKED |
| closed_by | User who transitioned to SOFT_CLOSED |
| hard_closed_by | User who transitioned to HARD_CLOSED |
| locked_at | Timestamp of LOCKED transition |
| fiscal_year | FK to fiscal year |

## Business Rules

1. Only one period can be OPEN at a time per entity
2. Periods must be closed in sequential order (cannot close March before February)
3. Opening a new period automatically soft-closes the previous one if still open
4. Year-end close creates automated adjusting entries (depreciation, accruals) before transitioning
5. The system prevents posting to a period that has not yet been opened
