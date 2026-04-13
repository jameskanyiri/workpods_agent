# Scheduled Tasks Calendar

## All 12 Scheduled Tasks

### Task 1: Email Polling

| Property | Value |
|----------|-------|
| Frequency | Every 60 seconds |
| Schedule | Continuous |
| Description | Poll configured email inboxes for incoming invoices, receipts, and bank notifications |
| On failure | Log error, retry on next cycle |
| Lock timeout | 30 seconds |

### Task 2: M-Pesa Reconciliation

| Property | Value |
|----------|-------|
| Frequency | Every 6 hours |
| Schedule | 00:00, 06:00, 12:00, 18:00 |
| Description | Pull M-Pesa transaction statements via Daraja API and reconcile against recorded payments |
| On failure | Retry 3x at 5-minute intervals, then alert administrator |
| Lock timeout | 15 minutes |

### Task 3: Bank Statement Import

| Property | Value |
|----------|-------|
| Frequency | Daily |
| Schedule | 6:00 AM |
| Description | Import bank statements (via API or file drop) and match against recorded transactions |
| On failure | Retry 3x at 5-minute intervals, then alert administrator |
| Lock timeout | 30 minutes |

### Task 4: PAYE Filing Alert

| Property | Value |
|----------|-------|
| Frequency | Monthly |
| Schedule | 5th of each month |
| Description | Send reminder that PAYE P10 return is due by the 9th |
| Recipients | Accountant, business owner |
| On failure | Retry next day |

### Task 5: VAT Filing Alert

| Property | Value |
|----------|-------|
| Frequency | Monthly |
| Schedule | 15th of each month |
| Description | Send reminder that VAT-3 return is due by the 20th |
| Recipients | Accountant, business owner |
| On failure | Retry next day |

### Task 6: NSSF Filing Alert

| Property | Value |
|----------|-------|
| Frequency | Monthly |
| Schedule | 10th of each month |
| Description | Send reminder that NSSF return is due by the 15th |
| Recipients | Accountant, business owner |
| On failure | Retry next day |

### Task 7: Month-End Reminder

| Property | Value |
|----------|-------|
| Frequency | Monthly |
| Schedule | 28th of each month |
| Description | Remind accountant to begin month-end close process: reconciliations, accruals, provisions |
| Recipients | Accountant |
| On failure | Retry next day |

### Task 8: Recurring Transactions

| Property | Value |
|----------|-------|
| Frequency | Daily |
| Schedule | 8:00 AM |
| Description | Process all recurring transactions due today (rent, subscriptions, loan repayments) |
| On failure | Retry 3x at 5-minute intervals, then flag for manual processing |
| Lock timeout | 10 minutes |

### Task 9: Anomaly Scan

| Property | Value |
|----------|-------|
| Frequency | Daily |
| Schedule | Midnight (00:00) |
| Description | Run all 6 anomaly detection rules and Isolation Forest model against the day's transactions |
| On failure | Retry 3x at 5-minute intervals, then alert administrator |
| Lock timeout | 30 minutes |

### Task 10: ML Model Retraining

| Property | Value |
|----------|-------|
| Frequency | Weekly |
| Schedule | Sunday 2:00 AM |
| Description | Retrain classification models using corrections, rejections, and approvals from past week |
| On failure | Keep existing model, alert administrator |
| Lock timeout | 2 hours |

### Task 11: Quarterly Instalment Tax Reminder

| Property | Value |
|----------|-------|
| Frequency | Quarterly |
| Schedule | 1st of April, June, September, December |
| Description | Remind that quarterly instalment tax is due by the 20th of the month |
| Recipients | Accountant, business owner, tax advisor |
| On failure | Retry next day |

### Task 12: Annual P9 Generation

| Property | Value |
|----------|-------|
| Frequency | Annually |
| Schedule | 15th January |
| Description | Auto-generate P9A tax deduction cards for all employees for the prior year |
| On failure | Retry 3x, then alert administrator for manual generation |
| Lock timeout | 1 hour |

## Distributed Lock Protocol

Each task acquires a distributed lock before execution to prevent duplicate runs in multi-instance deployments:

```
1. Attempt to acquire lock (task_name + scheduled_time)
2. If lock acquired: execute task
3. If lock not acquired: skip (another instance is handling it)
4. On completion: release lock and log result
5. Lock auto-expires after lock_timeout if not released (crash protection)
```

## Monitoring

All task executions are logged with:
- Task name
- Scheduled time vs actual start time
- Duration
- Status (success/failure/skipped)
- Error details (if failed)
- Instance ID (which server ran it)
