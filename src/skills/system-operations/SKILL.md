---
name: system-operations
description: Anomaly and fraud detection, scheduled task execution, and self-improvement through ML retraining. Maps to Agent 16 (Anomaly/Fraud Detection), Agent 21 (Scheduler), and Agent 22 (Self-Improvement).
---

# System Operations Skill

This skill implements three infrastructure agents that maintain system integrity, automate recurring tasks, and continuously improve classification accuracy.

## Agent Mapping

- **Agent 16**: Anomaly/Fraud Detection Agent
- **Agent 21**: Scheduler Agent
- **Agent 22**: Self-Improvement Agent

## Anomaly and Fraud Detection (Agent 16)

### 6 Detection Rules

#### Rule 1: Duplicate Transaction Detection

```
Flag if: same amount + same vendor within 7 days
Threshold: exact amount match (KES)
Action: flag for human review before posting
```

#### Rule 2: Statistical Outlier

```
Flag if: transaction amount > 3 standard deviations from vendor's historical mean
Calculation: mean and std dev computed from last 12 months of transactions with that vendor
Action: flag for review, present historical context
```

#### Rule 3: Round Number Bias

```
Flag if: >80% of a user's transactions in a period are round numbers (ending in 000)
Window: rolling 30-day period per user
Action: flag user's transactions for audit review
```

#### Rule 4: Weekend/Holiday Transactions

```
Flag if: transaction created on a weekend or Kenyan public holiday
Reference: Kenya public holiday calendar (configurable)
Action: flag with "off-hours" marker, lower severity than other rules
```

#### Rule 5: New Vendor High-Value First Transaction

```
Flag if: first-ever transaction with a vendor exceeds KES 100,000
Threshold: KES 100,000 (configurable)
Action: require manager approval before posting
```

#### Rule 6: Category Expense Spike

```
Flag if: expense category total > 50% increase vs 3-month rolling average
Calculation: current month total vs average of prior 3 months
Action: flag for review, present trend data
```

See `references/anomaly_rules.md` for detailed thresholds and examples.

### ML Model: Isolation Forest

In addition to rule-based detection, an Isolation Forest model (scikit-learn) runs nightly to identify statistical anomalies that rule-based checks may miss:

- Trained on transaction features: amount, time of day, day of week, vendor frequency, category distribution
- Contamination parameter: 0.01 (expects ~1% anomaly rate)
- Retrained weekly from the `ai_corrections` table to incorporate human feedback

## Scheduled Tasks (Agent 21)

The Scheduler Agent manages 12 recurring tasks. See `references/schedule_calendar.md` for the complete schedule.

| # | Task | Frequency | Time |
|---|------|-----------|------|
| 1 | Email polling | Every 60 seconds | Continuous |
| 2 | M-Pesa reconciliation | Every 6 hours | 00:00, 06:00, 12:00, 18:00 |
| 3 | Bank statement import | Daily | 6:00 AM |
| 4 | PAYE filing alert | Monthly | 5th of month |
| 5 | VAT filing alert | Monthly | 15th of month |
| 6 | NSSF filing alert | Monthly | 10th of month |
| 7 | Month-end reminder | Monthly | 28th of month |
| 8 | Recurring transactions | Daily | 8:00 AM |
| 9 | Anomaly scan | Daily | Midnight |
| 10 | ML model retraining | Weekly | Sunday 2:00 AM |
| 11 | Quarterly instalment tax reminder | Quarterly | 1st of Apr/Jun/Sep/Dec |
| 12 | Annual P9 generation | Annually | 15th January |

### Task Execution

Each scheduled task:
1. Acquires a distributed lock to prevent duplicate execution
2. Logs start time and status
3. Executes the task logic
4. Records completion status (success/failure) and duration
5. Releases the lock
6. On failure: retries up to 3 times with 5-minute intervals, then alerts the administrator

## Self-Improvement (Agent 22)

### Weekly Retraining Cycle

Every Sunday at 2:00 AM, the Self-Improvement Agent runs a retraining pipeline. See `references/retraining_pipeline.md` for the full cycle.

**Data sources for retraining:**

1. **ai_corrections table**: Records where a human corrected the AI's classification (e.g., changed expense category, corrected vendor match, fixed account mapping)
2. **Rejection logs**: Transactions that were rejected by the accountant with reasons
3. **Approval patterns**: Transactions that were approved without modification (positive signal)

**Retraining process:**

1. Extract corrections, rejections, and approvals from the past week
2. Transform into training examples with correct labels
3. Retrain classification models (expense categorization, vendor matching, account mapping)
4. Evaluate new model against a held-out validation set
5. If accuracy improves or maintains: deploy new model
6. If accuracy degrades: keep existing model and alert administrator
7. Log retraining metrics (accuracy, F1, sample count) for trend monitoring

### Feedback Loop

```
User corrects AI decision
  --> Correction stored in ai_corrections table
    --> Weekly retraining incorporates correction
      --> Model improves for similar future transactions
        --> Fewer corrections needed over time
```

The system tracks correction rate as a key metric. A declining correction rate over weeks indicates successful self-improvement.
