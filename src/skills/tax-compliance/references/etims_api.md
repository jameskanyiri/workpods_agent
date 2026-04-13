# eTIMS VSCU REST API Reference

## Overview

The electronic Tax Invoice Management System (eTIMS) requires all VAT-registered businesses to submit invoices through a Virtual Sales Control Unit (VSCU). The VSCU stamps each invoice with a control number and QR code for KRA verification.

## Base URL

```
Production: https://etims.kra.go.ke/api/v1
Sandbox:    https://etims-sandbox.kra.go.ke/api/v1
```

## Authentication

All requests require HMAC-SHA256 signed headers:

```
Headers:
  X-API-Key: {assigned_api_key}
  X-Timestamp: {ISO-8601 timestamp}
  X-Signature: HMAC-SHA256(api_secret, timestamp + request_body)
  Content-Type: application/json
```

API keys are issued per device/terminal during VSCU registration.

## Endpoints

### POST /invoice/submit

Submit a new tax invoice for stamping.

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| traderSystemInvoiceNumber | string | Yes | Internal invoice number |
| invoiceType | string | Yes | "S" (sale), "CR" (credit note), "DR" (debit note) |
| invoiceDate | string | Yes | ISO-8601 date |
| buyerPin | string | No | Buyer KRA PIN (required if B2B > KES 10,000) |
| buyerName | string | Yes | Buyer name |
| totalAmount | decimal | Yes | Total invoice amount (VAT inclusive) |
| vatAmount | decimal | Yes | Total VAT amount |
| items | array | Yes | Line items (see below) |

**Line Item Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| itemCode | string | Yes | HS code or internal code |
| itemDescription | string | Yes | Description of goods/services |
| quantity | decimal | Yes | Quantity |
| unitPrice | decimal | Yes | Unit price (VAT exclusive) |
| taxCategory | string | Yes | "A" (16%), "B" (0%), "C" (exempt), "D" (non-VAT) |
| vatAmount | decimal | Yes | VAT on this line |
| totalAmount | decimal | Yes | Line total (VAT inclusive) |

**Response (Success):**

```json
{
  "status": "OK",
  "controlNumber": "INV-2024-00001234",
  "qrCode": "base64_encoded_qr_image",
  "receiptNumber": "RCT-0000567890",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /invoice/{controlNumber}

Retrieve a previously submitted invoice by control number.

### POST /invoice/cancel

Cancel a previously submitted invoice. Requires the original control number and a reason code.

### GET /status

Health check endpoint. Returns VSCU connectivity status.

## Error Codes

| Code | Description | Action |
|------|-------------|--------|
| E001 | Invalid API key | Re-register VSCU device |
| E002 | Signature mismatch | Check HMAC computation |
| E003 | Invalid invoice format | Validate required fields |
| E004 | Duplicate invoice number | Check for duplicate submission |
| E005 | Invalid buyer PIN | Validate KRA PIN format |
| E006 | Item code not found | Register item in eTIMS item master |
| E007 | VSCU offline | Enter offline mode |
| E008 | Rate limit exceeded | Back off and retry |
| E009 | Invalid tax category | Use valid category code (A/B/C/D) |
| E010 | Session expired | Re-authenticate |

## Retry Logic

On transient failures (E007, E008, network timeouts), apply exponential backoff:

| Attempt | Wait Time | Cumulative |
|---------|-----------|------------|
| 1 | 1 minute | 1 minute |
| 2 | 5 minutes | 6 minutes |
| 3 | 15 minutes | 21 minutes |
| 4 | 1 hour | 1 hour 21 minutes |
| 5 | 6 hours | 7 hours 21 minutes |

After 5 failed attempts (approximately 6+ hours of downtime), switch to **offline mode**.

## Offline Mode

When KRA systems are unreachable for more than 6 hours:

1. Generate sequential offline invoice numbers (prefixed with "OFF-")
2. Store invoices locally with all required fields
3. Continue normal business operations
4. Monitor VSCU connectivity with periodic health checks
5. When connectivity is restored, submit queued invoices in chronological order
6. Map offline numbers to VSCU control numbers
7. Update stored invoices with control numbers and QR codes

## Rate Limits

- Maximum 100 requests per minute per API key
- Maximum 10,000 invoices per day per VSCU device
- Bulk submission endpoint available for batch processing (max 50 invoices per batch)
