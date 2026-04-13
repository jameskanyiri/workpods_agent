# Maker/Checker Dual-Approval Workflow for B2C Disbursements

## Overview

All outbound M-Pesa payments (B2C) require dual authorization through a maker/checker workflow. This ensures no single person can initiate and approve a payment, providing fraud prevention and internal controls.

## Roles

### Maker

The person or system that creates a payment request.

**Permissions**:
- Create disbursement requests
- View own pending requests
- Cancel own pending requests (before checker action)
- Cannot approve own requests

**Who can be a Maker**:
- Any authorized user with `PAYMENT_CREATE` permission
- The ADA system itself (automated payments from recurring templates, salary runs)
- When system is the maker, a human checker is always required

### Checker

The person who reviews and approves or rejects a payment request.

**Permissions**:
- View all pending requests
- Approve or reject requests
- Cannot approve requests they created (separation of duties)
- Must provide rejection reason when rejecting

**Who can be a Checker**:
- Users with `PAYMENT_APPROVE` permission
- Typically: business owner, finance manager, or designated approver
- Minimum one checker required; can configure multiple checkers (any one can approve)

## Workflow States

```
DRAFT -> PENDING_APPROVAL -> APPROVED -> PROCESSING -> COMPLETED
                          -> REJECTED -> (end)
                                      -> FAILED -> RETRY -> PROCESSING
                                                -> MANUAL_REVIEW -> (end)
```

| State | Description | Next States |
|-------|-------------|-------------|
| `DRAFT` | Request created but not yet submitted | `PENDING_APPROVAL`, deleted |
| `PENDING_APPROVAL` | Submitted, waiting for checker | `APPROVED`, `REJECTED` |
| `APPROVED` | Checker approved, queued for execution | `PROCESSING` |
| `REJECTED` | Checker rejected with reason | Terminal (can create new request) |
| `PROCESSING` | B2C API call in progress | `COMPLETED`, `FAILED` |
| `COMPLETED` | Payment successful, journal entry posted | Terminal |
| `FAILED` | B2C API returned error | `RETRY`, `MANUAL_REVIEW` |
| `RETRY` | Automatic retry scheduled | `PROCESSING` |
| `MANUAL_REVIEW` | Max retries exceeded, needs human intervention | Terminal |

## Approval Process

### Step 1: Maker Creates Request

```json
{
  "disbursement_id": "DSB-2026-04-001",
  "type": "SUPPLIER_PAYMENT",
  "recipient_name": "Supplier ABC",
  "recipient_phone": "254712345678",
  "amount": 50000.00,
  "reference": "INV-SUP-2026-0089",
  "description": "Payment for raw materials - April batch",
  "supporting_documents": ["INV-SUP-2026-0089.pdf"],
  "maker": {
    "user_id": "USR-003",
    "user_name": "Jane Wanjiru",
    "role": "ACCOUNTANT",
    "timestamp": "2026-04-10T10:00:00+03:00",
    "ip_address": "192.168.1.100",
    "device": "WhatsApp/+254711222333"
  },
  "status": "PENDING_APPROVAL"
}
```

### Step 2: Notification to Checker(s)

A WhatsApp message is sent to all users with `PAYMENT_APPROVE` permission:

```
[ADA] Payment Approval Required

Type: Supplier Payment
To: Supplier ABC (0712345678)
Amount: KES 50,000.00
Reference: INV-SUP-2026-0089
Description: Payment for raw materials - April batch
Requested by: Jane Wanjiru at 10:00 AM

Reply APPROVE or REJECT (with reason)
```

### Step 3: Checker Reviews and Decides

**Approve**:
```
Approve
```

**Reject**:
```
Reject - amount should be 45,000 per the revised invoice
```

### Step 4: Execution or Rejection

**On approval**:
1. Log checker details (user_id, timestamp, IP)
2. Validate M-Pesa float balance is sufficient
3. Call B2C API
4. Wait for result callback
5. On success: create journal entry, notify maker
6. On failure: retry or escalate

**On rejection**:
1. Log rejection with reason
2. Notify maker via WhatsApp with rejection reason
3. Maker can create a new corrected request

## Audit Trail

Every action in the workflow is logged with:

| Field | Description |
|-------|-------------|
| `action` | CREATE, SUBMIT, APPROVE, REJECT, EXECUTE, COMPLETE, FAIL, RETRY |
| `user_id` | Who performed the action |
| `user_name` | Human-readable name |
| `timestamp` | ISO 8601 with timezone |
| `ip_address` | Source IP address |
| `device` | Device/channel (WhatsApp, Web, API) |
| `notes` | Optional notes (required for REJECT) |
| `previous_state` | State before action |
| `new_state` | State after action |

### Example Audit Log

```json
{
  "disbursement_id": "DSB-2026-04-001",
  "audit_trail": [
    {
      "action": "CREATE",
      "user_id": "USR-003",
      "user_name": "Jane Wanjiru",
      "timestamp": "2026-04-10T10:00:00+03:00",
      "ip_address": "192.168.1.100",
      "device": "WhatsApp/+254711222333",
      "previous_state": null,
      "new_state": "PENDING_APPROVAL"
    },
    {
      "action": "APPROVE",
      "user_id": "USR-001",
      "user_name": "James Kamau",
      "timestamp": "2026-04-10T10:15:00+03:00",
      "ip_address": "192.168.1.101",
      "device": "WhatsApp/+254700111222",
      "previous_state": "PENDING_APPROVAL",
      "new_state": "APPROVED"
    },
    {
      "action": "EXECUTE",
      "user_id": "SYSTEM",
      "user_name": "ADA System",
      "timestamp": "2026-04-10T10:15:05+03:00",
      "ip_address": "10.0.0.1",
      "device": "API",
      "previous_state": "APPROVED",
      "new_state": "PROCESSING"
    },
    {
      "action": "COMPLETE",
      "user_id": "SYSTEM",
      "user_name": "ADA System",
      "timestamp": "2026-04-10T10:15:30+03:00",
      "ip_address": "10.0.0.1",
      "device": "API",
      "notes": "M-Pesa TransID: QCL8F5H1XR",
      "previous_state": "PROCESSING",
      "new_state": "COMPLETED"
    }
  ]
}
```

## Thresholds and Escalation

| Amount Range | Approval Requirement |
|-------------|---------------------|
| KES 0 - 10,000 | Single checker approval |
| KES 10,001 - 100,000 | Single checker approval (must be MANAGER or above) |
| KES 100,001 - 500,000 | Two checker approvals required |
| KES 500,001+ | Business owner approval required |

These thresholds are configurable per business.

## Timeout Rules

| Scenario | Timeout | Action |
|----------|---------|--------|
| Pending approval with no response | 24 hours | Send reminder to checker(s) |
| Pending approval after reminder | 48 hours | Escalate to business owner |
| Pending approval after escalation | 72 hours | Auto-expire, notify maker |

## Bulk Salary Disbursement

For salary runs, the workflow is modified:

1. **Maker** submits a batch (list of employees, amounts, and M-Pesa numbers)
2. **System** validates: total matches approved payroll, all phones are valid, sufficient float
3. **Checker** receives a summary for approval (not individual payments)
4. **On approval**: execute B2C calls sequentially with 1-second delay between calls
5. **Result**: aggregate report showing successful/failed payments

### Bulk Request Schema

```json
{
  "batch_id": "SAL-2026-04",
  "type": "SALARY_DISBURSEMENT",
  "payroll_period": "April 2026",
  "total_amount": 850000.00,
  "recipient_count": 12,
  "recipients": [
    {"name": "John Odhiambo", "phone": "254712345678", "amount": 85000.00},
    {"name": "Mary Akinyi", "phone": "254723456789", "amount": 72000.00}
  ],
  "status": "PENDING_APPROVAL"
}
```

## Segregation of Duties Matrix

| Action | Accountant | Finance Manager | Business Owner |
|--------|-----------|----------------|---------------|
| Create payment request | Yes | Yes | Yes |
| Approve payments < 100K | No | Yes | Yes |
| Approve payments 100K-500K | No | Yes (1 of 2) | Yes (1 of 2) |
| Approve payments > 500K | No | No | Yes |
| View audit trail | Own requests | All | All |
| Configure thresholds | No | No | Yes |
| Override rejected payment | No | No | Yes |
