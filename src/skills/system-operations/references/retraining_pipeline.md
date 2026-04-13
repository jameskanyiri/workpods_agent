# Weekly ML Retraining Pipeline

## Schedule

Runs every Sunday at 2:00 AM via the Scheduler Agent (Agent 21).

## Pipeline Steps

### Step 1: Data Extraction

Extract training data from three sources covering the past 7 days:

| Source | Table | Signal Type |
|--------|-------|-------------|
| Human corrections | `ai_corrections` | Negative (AI was wrong) |
| Rejected transactions | `transaction_reviews` where status = REJECTED | Negative (AI output rejected) |
| Approved transactions | `transaction_reviews` where status = APPROVED | Positive (AI output accepted) |

### Step 2: Feature Engineering

Transform raw records into training examples:

```
For each correction/rejection/approval:
  - Extract transaction features (amount, vendor, description, date, time)
  - Extract the AI's original prediction
  - Extract the correct label (human-provided or original if approved)
  - Create feature vector for the relevant model
```

### Step 3: Dataset Assembly

Combine new examples with the existing training dataset:

- Append new examples to the cumulative training set
- Apply class balancing (oversample minority classes if needed)
- Split: 80% training, 20% validation (stratified)

### Step 4: Model Retraining

Retrain each classification model:

| Model | Purpose | Algorithm |
|-------|---------|-----------|
| Expense Categorizer | Classify expenses into chart of accounts categories | Gradient Boosted Trees (XGBoost) |
| Vendor Matcher | Match transaction descriptions to known vendors | TF-IDF + cosine similarity |
| Account Mapper | Map transactions to correct GL accounts | Multi-class classifier (XGBoost) |
| Anomaly Detector | Identify unusual transactions | Isolation Forest (scikit-learn) |

### Step 5: Evaluation

Compare new model against current production model on the validation set:

| Metric | Threshold |
|--------|-----------|
| Accuracy | Must not decrease by more than 1% |
| F1 Score (macro) | Must not decrease by more than 2% |
| Per-class recall | No class recall drops below 70% |

### Step 6: Deployment Decision

```
IF new_model metrics >= current_model metrics:
    Deploy new model (swap in production)
    Archive current model as rollback candidate
ELSE IF degradation is within tolerance:
    Deploy new model but flag for monitoring
ELSE:
    Keep current model
    Alert administrator with degradation details
    Store new model for manual review
```

### Step 7: Logging and Metrics

Record retraining results:

| Metric | Description |
|--------|-------------|
| training_samples | Total training examples used |
| new_corrections | Number of new corrections this week |
| new_rejections | Number of new rejections this week |
| new_approvals | Number of new approvals this week |
| accuracy_before | Current model accuracy on validation set |
| accuracy_after | New model accuracy on validation set |
| f1_before | Current model F1 score |
| f1_after | New model F1 score |
| deployed | Whether the new model was deployed |
| duration_seconds | Total pipeline execution time |

## Correction Rate Tracking

The system tracks weekly correction rate as the primary self-improvement metric:

```
Correction Rate = corrections / total_ai_decisions x 100
```

A declining correction rate over consecutive weeks indicates successful learning. The target is to reduce correction rate below 5% within 3 months of deployment.

## Rollback

If a deployed model performs poorly in production (correction rate spikes):

1. Automatic rollback to the previous model if correction rate increases by >50% in 48 hours
2. Manual rollback available via administrator command
3. All model versions are retained for 90 days

## Data Retention

- Training data is retained indefinitely (cumulative learning)
- Model artifacts are retained for 90 days
- Retraining logs are retained for 1 year
- Correction records are never deleted (audit requirement)
