# Daraja API Endpoints and Authentication

## Overview

Safaricom's Daraja API provides M-Pesa integration for Kenyan businesses. ADA uses two primary APIs: C2B (Customer to Business) for receiving payments and B2C (Business to Customer) for disbursements.

## Environments

| Environment | Base URL | Purpose |
|-------------|----------|---------|
| Sandbox | `https://sandbox.safaricom.co.ke` | Development and testing |
| Production | `https://api.safaricom.co.ke` | Live transactions |

## Authentication

### OAuth 2.0 Token Generation

All API calls require a Bearer token obtained via OAuth.

**Endpoint**: `GET /oauth/v1/generate?grant_type=client_credentials`

**Headers**:
```
Authorization: Basic {base64(consumer_key:consumer_secret)}
```

**Response**:
```json
{
  "access_token": "SGWcJPtNtYNPGm6uSYR9yPYrAI3Bm",
  "expires_in": "3599"
}
```

**Token management**:
- Cache the token in Redis with TTL = expires_in - 60 seconds (buffer)
- Refresh before expiry to avoid failed API calls
- Never log or expose the access token

### Credentials

| Credential | Source | Storage |
|-----------|--------|---------|
| Consumer Key | Daraja portal | Environment variable `MPESA_CONSUMER_KEY` |
| Consumer Secret | Daraja portal | Environment variable `MPESA_CONSUMER_SECRET` |
| Passkey (STK) | Safaricom | Environment variable `MPESA_PASSKEY` |
| Initiator Name | Business config | Environment variable `MPESA_INITIATOR_NAME` |
| Security Credential | Encrypted initiator password | Environment variable `MPESA_SECURITY_CREDENTIAL` |
| Short Code | Business till/paybill | Environment variable `MPESA_SHORTCODE` |

---

## C2B API (Customer to Business)

### 1. Register URLs

Register validation and confirmation callback URLs with Safaricom.

**Endpoint**: `POST /mpesa/c2b/v1/registerurl`

**Request**:
```json
{
  "ShortCode": "600000",
  "ResponseType": "Completed",
  "ConfirmationURL": "https://api.ada-finance.co.ke/mpesa/c2b/confirm",
  "ValidationURL": "https://api.ada-finance.co.ke/mpesa/c2b/validate"
}
```

**ResponseType options**:
- `Completed`: Accept all payments (validation URL still called but response ignored)
- `Cancelled`: Reject payments that fail validation

### 2. Validation Callback

Safaricom calls this URL to validate a payment before processing.

**Incoming request from Safaricom**:
```json
{
  "TransactionType": "Pay Bill",
  "TransID": "SHK7X2M4LP",
  "TransTime": "20260410143000",
  "TransAmount": "15000.00",
  "BusinessShortCode": "600000",
  "BillRefNumber": "INV-2026-0045",
  "InvoiceNumber": "",
  "OrgAccountBalance": "",
  "ThirdPartyTransID": "",
  "MSISDN": "254712345678",
  "FirstName": "JOHN",
  "MiddleName": "",
  "LastName": "DOE"
}
```

**Response to accept**:
```json
{
  "ResultCode": 0,
  "ResultDesc": "Accepted"
}
```

**Response to reject**:
```json
{
  "ResultCode": 1,
  "ResultDesc": "Rejected: Invalid account reference"
}
```

### 3. Confirmation Callback

Called after successful payment processing.

**Incoming request**: Same schema as validation callback.

**Response**: Always acknowledge with:
```json
{
  "ResultCode": 0,
  "ResultDesc": "Success"
}
```

**Processing**: Upon receiving confirmation, the system:
1. Deduplicates using TransID
2. Matches customer by BillRefNumber or MSISDN
3. Creates accounts receivable journal entry
4. Sends receipt confirmation to customer via WhatsApp (if phone is registered)

---

## B2C API (Business to Customer)

### 1. Initiate Payment

**Endpoint**: `POST /mpesa/b2c/v3/paymentrequest`

**Request**:
```json
{
  "OriginatorConversationID": "DSB-2026-04-001",
  "InitiatorName": "ADA_INITIATOR",
  "SecurityCredential": "{encrypted_credential}",
  "CommandID": "BusinessPayment",
  "Amount": "50000",
  "PartyA": "600000",
  "PartyB": "254712345678",
  "Remarks": "Supplier payment INV-SUP-2026-0089",
  "QueueTimeOutURL": "https://api.ada-finance.co.ke/mpesa/b2c/timeout",
  "ResultURL": "https://api.ada-finance.co.ke/mpesa/b2c/result",
  "Occasion": "Supplier Payment"
}
```

**CommandID options**:
- `BusinessPayment`: Normal business payment (supplier, refund)
- `SalaryPayment`: Salary disbursement
- `PromotionPayment`: Promotional/bonus payment

### 2. Result Callback

Safaricom calls the ResultURL with the transaction outcome.

**Success response**:
```json
{
  "Result": {
    "ResultType": 0,
    "ResultCode": 0,
    "ResultDesc": "The service request is processed successfully.",
    "OriginatorConversationID": "DSB-2026-04-001",
    "ConversationID": "AG_20260410_0000abcdef12",
    "TransactionID": "QCL8F5H1XR",
    "ResultParameters": {
      "ResultParameter": [
        {"Key": "TransactionAmount", "Value": 50000},
        {"Key": "TransactionReceipt", "Value": "QCL8F5H1XR"},
        {"Key": "B2CRecipientIsRegisteredCustomer", "Value": "Y"},
        {"Key": "B2CChargesPaidAccountAvailableFunds", "Value": 950000.00},
        {"Key": "ReceiverPartyPublicName", "Value": "254712345678 - SUPPLIER ABC"},
        {"Key": "TransactionCompletedDateTime", "Value": "10.04.2026 14:30:00"},
        {"Key": "B2CUtilityAccountAvailableFunds", "Value": 0.00},
        {"Key": "B2CWorkingAccountAvailableFunds", "Value": 950000.00}
      ]
    }
  }
}
```

### 3. Timeout Callback

Called if Safaricom cannot process the request in time.

**Action**: Log timeout, retry after 5 minutes (max 3 retries), then flag for manual processing.

---

## Transaction Status Query

Check the status of a previously initiated transaction.

**Endpoint**: `POST /mpesa/transactionstatus/v1/query`

**Request**:
```json
{
  "Initiator": "ADA_INITIATOR",
  "SecurityCredential": "{encrypted_credential}",
  "CommandID": "TransactionStatusQuery",
  "TransactionID": "QCL8F5H1XR",
  "IdentifierType": "4",
  "PartyA": "600000",
  "Remarks": "Status check",
  "QueueTimeOutURL": "https://api.ada-finance.co.ke/mpesa/status/timeout",
  "ResultURL": "https://api.ada-finance.co.ke/mpesa/status/result"
}
```

---

## Account Balance Query

Check M-Pesa account balance.

**Endpoint**: `POST /mpesa/accountbalance/v1/query`

**Use case**: Verify sufficient balance before initiating B2C payments.

---

## Security Credential Generation

The SecurityCredential for B2C is generated by encrypting the initiator password with Safaricom's public certificate:

1. Download Safaricom's public certificate (sandbox or production)
2. Read the certificate and extract the public key
3. Encrypt the initiator password using RSA/OAEP
4. Base64-encode the result

**Certificate URLs**:
- Sandbox: Available in Daraja portal
- Production: Provided by Safaricom during go-live

---

## Rate Limits

| API | Rate Limit | Notes |
|-----|-----------|-------|
| OAuth token | 2 requests/second | Cache tokens to avoid hitting limit |
| C2B Register | 1 request/day | Only needed once (or on URL change) |
| B2C Payment | 40 TPS (transactions per second) | Shared across all API consumers |
| Transaction Status | 10 TPS | Use sparingly |
| Account Balance | 5 TPS | Cache result for 5 minutes |

## Error Codes Reference

| Code | Description | Recommended Action |
|------|-------------|-------------------|
| 0 | Success | Process normally |
| 1 | Insufficient funds | Alert finance, top up float |
| 2001 | Wrong credentials | Check API keys, regenerate security credential |
| 2006 | Transaction failed | Retry once, then manual review |
| 17 | System busy | Exponential backoff retry |
| 26 | System busy (timeout) | Retry after 5 minutes |
| 1032 | Request cancelled by user | Log, no retry |
| 1037 | Timeout waiting for response | Query transaction status |
