---
name: mpesa-integration
description: M-Pesa payment integration covering Daraja C2B webhook reception and B2C payment disbursement with maker/checker dual-approval workflow. Maps to Agents 6 (M-Pesa Webhook) and 20 (Payment Disbursement).
---

# M-Pesa Integration Skill

This skill handles bidirectional M-Pesa integration: receiving customer payments (C2B) via Safaricom's Daraja API webhooks, and initiating outbound payments (B2C) for supplier payments and salary disbursements with a mandatory dual-approval workflow.

## Agents

| Agent | Name | Role |
|-------|------|------|
| 6 | M-Pesa Webhook | Receive and process C2B payment notifications via Daraja API |
| 20 | Payment Disbursement | Initiate B2C payments for supplier payments and salary disbursements |

## M-Pesa Webhook - C2B (Agent 6)

### Daraja C2B Flow

1. **Registration**: Register validation and confirmation URLs with Safaricom
2. **Validation**: Receive validation request, check business rules, respond with accept/reject
3. **Confirmation**: Receive confirmation after successful payment, create book entry

See `references/daraja_api.md` for API endpoint details and authentication.

### Validation Rules

When a C2B payment validation request arrives:

| Check | Rule | Reject If |
|-------|------|-----------|
| Amount | Must be positive and within expected range | Amount <= 0 or > KES 300,000 (configurable) |
| Account reference | Must match a known invoice, customer, or account | No matching record found (configurable: accept all or validate) |
| Business short code | Must match registered till/paybill | Short code mismatch |

### Signature Validation

All incoming webhooks are validated against Safaricom's certificate:

1. Extract the `X-Signature` header
2. Decode using Safaricom's public certificate
3. Verify signature against request body
4. Reject requests with invalid or missing signatures

### Deduplication

M-Pesa may send duplicate confirmation callbacks. Deduplication is handled by:

1. Extract `TransID` (M-Pesa transaction code) from the callback
2. Check against Redis set `mpesa:processed:{TransID}`
3. If exists: acknowledge callback but skip processing
4. If new: process and add to Redis with 90-day TTL

### Customer Matching

Match incoming payments to customers using a cascade:

| Priority | Match Field | Source |
|----------|-------------|--------|
| 1 | Account Reference | Customer account number in BillRefNumber |
| 2 | Phone Number | MSISDN mapped to customer record |
| 3 | Amount + Recent Invoice | Amount matches an outstanding invoice |
| 4 | No match | Create unallocated receipt, flag for manual allocation |

### Invoice Matching

When a customer payment arrives:

1. Look up customer by account reference or phone
2. Find outstanding invoices for that customer
3. Match by exact amount first, then oldest-first allocation
4. If overpayment: allocate to invoices, remainder to customer credit
5. If underpayment: partial allocation, flag remaining balance

### C2B Confirmation Output

```json
{
  "transaction_id": "SHK7X2M4LP",
  "transaction_type": "C2B",
  "amount": 15000.00,
  "phone": "254712345678",
  "account_reference": "INV-2026-0045",
  "timestamp": "2026-04-10T14:30:00+03:00",
  "customer_matched": true,
  "customer_id": "CUST-001",
  "invoice_matched": true,
  "invoice_id": "INV-2026-0045",
  "journal_entry": {
    "lines": [
      {"account_code": "1110", "account_name": "M-Pesa Float", "debit": 15000.00, "credit": 0.00},
      {"account_code": "1100", "account_name": "Accounts Receivable", "debit": 0.00, "credit": 15000.00}
    ]
  }
}
```

## Payment Disbursement - B2C (Agent 20)

### Supported Disbursement Types

| Type | Use Case | Daraja API |
|------|----------|-----------|
| Supplier Payment | Pay supplier via M-Pesa | B2C API |
| Salary Disbursement | Send employee salary to M-Pesa | B2C API (bulk) |
| Petty Cash Float | Send float to staff M-Pesa | B2C API |
| Refund | Customer refund via M-Pesa | B2C API |

### Maker/Checker Dual-Approval Workflow

All B2C disbursements require dual approval before execution. See `references/maker_checker.md` for the full workflow.

**Roles**:
- **Maker**: Creates the payment request (can be automated by the system or manual by a user)
- **Checker**: Reviews and approves/rejects the payment (must be a different user from the maker)

**Flow**:
1. Maker creates disbursement request
2. System validates request (amount, recipient, account balance)
3. Notification sent to Checker(s) via WhatsApp
4. Checker approves or rejects (with reason)
5. If approved: execute B2C API call
6. If rejected: notify Maker with rejection reason

### Disbursement Request Schema

```json
{
  "disbursement_id": "DSB-2026-04-001",
  "type": "SUPPLIER_PAYMENT",
  "recipient_name": "Supplier ABC",
  "recipient_phone": "254712345678",
  "amount": 50000.00,
  "currency": "KES",
  "reference": "INV-SUP-2026-0089",
  "description": "Payment for raw materials - April batch",
  "maker": {
    "user_id": "USR-003",
    "timestamp": "2026-04-10T10:00:00+03:00",
    "ip_address": "192.168.1.100"
  },
  "checker": {
    "user_id": "USR-001",
    "timestamp": "2026-04-10T10:15:00+03:00",
    "ip_address": "192.168.1.101",
    "decision": "APPROVED",
    "notes": ""
  },
  "status": "APPROVED",
  "mpesa_result": {
    "conversation_id": "AG_20260410_0000abcdef12",
    "originator_conversation_id": "DSB-2026-04-001",
    "result_code": 0,
    "result_desc": "The service request is processed successfully.",
    "transaction_id": "QCL8F5H1XR"
  }
}
```

### Amount Limits

| Limit Type | Amount | Configurable |
|-----------|--------|-------------|
| Single transaction minimum | KES 10 | No (Safaricom minimum) |
| Single transaction maximum | KES 150,000 | Yes (default, can increase with Safaricom approval) |
| Daily limit per business | KES 1,000,000 | Yes |
| Monthly limit per business | KES 10,000,000 | Yes |
| Bulk salary max recipients | 500 per batch | Yes |

### B2C Result Handling

After initiating a B2C payment, handle the async result callback:

| Result Code | Meaning | Action |
|-------------|---------|--------|
| 0 | Success | Create journal entry, mark disbursement as completed |
| 1 | Insufficient balance | Alert finance team, retry after top-up |
| 2001 | Wrong credentials | Alert system admin, check API keys |
| 2006 | Transaction failed | Retry once after 5 minutes, then flag for manual review |
| 17 | System busy | Retry with exponential backoff (max 3 retries) |

### Journal Entry on Successful B2C

```json
{
  "effective_date": "2026-04-10",
  "description": "M-Pesa B2C payment to Supplier ABC - INV-SUP-2026-0089",
  "lines": [
    {"account_code": "2000", "account_name": "Accounts Payable", "debit": 50000.00, "credit": 0.00},
    {"account_code": "1110", "account_name": "M-Pesa Float", "debit": 0.00, "credit": 50000.00}
  ],
  "source_type": "MPESA_B2C",
  "mpesa_transaction_id": "QCL8F5H1XR"
}
```

## Security

| Measure | Implementation |
|---------|---------------|
| API credentials | Stored in environment variables / secrets manager, never in code |
| Webhook validation | Safaricom certificate-based signature verification |
| Audit trail | Every disbursement logged with user_id, timestamp, IP address |
| Rate limiting | Max 10 B2C requests per minute |
| IP whitelisting | Safaricom callback IPs whitelisted at firewall level |
| Encryption | All API calls over TLS 1.2+ |

## LangGraph Node

- **Node name**: `mpesa_integration`
- **Subgraph nodes**: `c2b_webhook` (event-driven), `b2c_disbursement` (request-driven)
- **State keys consumed**: `webhook_payload`, `disbursement_request`, `approval_decision`
- **State keys produced**: `payment_received`, `payment_sent`, `journal_entry`, `mpesa_result`
- **Next nodes**: `journal_entry` (for booking), `human_review` (for approval), `notification` (for alerts)
