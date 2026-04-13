---
name: document-capture
description: Receipt/invoice OCR processing and email monitoring pipeline for automated document intake. Maps to Agents 3 (Receipt/Invoice OCR) and 4 (Email Monitor).
---

# Document Capture Skill

This skill handles automated ingestion of financial documents through two channels: image-based OCR for receipts and invoices, and IMAP-based email monitoring for electronic documents.

## Agents

| Agent | Name | Role |
|-------|------|------|
| 3 | Receipt/Invoice OCR | Extract structured data from receipt and invoice images using PaddleOCR + Donut |
| 4 | Email Monitor | Poll IMAP mailbox, classify financial emails, extract attachments |

## Receipt/Invoice OCR (Agent 3)

### Processing Pipeline

1. **Image preprocessing**: deskew, contrast normalization, noise reduction
2. **Text detection**: PaddleOCR for text region detection and recognition
3. **Structured extraction**: Donut (Document Understanding Transformer) for field extraction
4. **VAT validation**: verify VAT amount = 16% of subtotal, validate KRA PIN format
5. **Output**: structured JSON with extracted fields

### Extracted Fields

```json
{
  "vendor_name": "Naivas Supermarket",
  "vendor_pin": "P051234567Z",
  "vendor_address": "Moi Avenue, Nairobi",
  "receipt_number": "RCT-2026-04-00234",
  "date": "2026-04-10",
  "items": [
    {
      "description": "Sugar 2kg",
      "quantity": 1,
      "unit_price": 320.00,
      "total": 320.00,
      "vat_category": "STANDARD"
    }
  ],
  "subtotal": 4310.34,
  "vat_amount": 689.66,
  "total": 5000.00,
  "payment_method": "MPESA",
  "mpesa_reference": "SHK7X2M4LP",
  "etims_cu_number": "CU001234",
  "etims_receipt_number": "0001-0002-0003",
  "currency": "KES"
}
```

See `references/receipt_fields.md` for the full field specification including eTIMS requirements.

### VAT Validation Rules

| Check | Rule | Action on Failure |
|-------|------|-------------------|
| VAT rate | `vat_amount` should equal `subtotal * 0.16` (within KES 1 tolerance) | Flag discrepancy, log warning |
| KRA PIN format | Must match `[AP]\d{9}[A-Z]` | Flag as potentially invalid |
| eTIMS CU number | Must be present for receipts dated after 2024-09-01 | Flag for compliance review |
| Zero-rated items | Items marked zero-rated should have 0% VAT | Verify against zero-rated items list |
| Exempt items | Insurance, financial services, medical, education | Exclude from VAT calculation |

### Supported Document Types

| Type | Detection Method |
|------|-----------------|
| Printed receipt (thermal) | Text layout analysis, presence of till number |
| Tax invoice | "TAX INVOICE" header, KRA PIN, eTIMS fields |
| Proforma invoice | "PROFORMA" header, no eTIMS fields |
| Delivery note | "DELIVERY NOTE" header, item list without totals |
| Credit note | "CREDIT NOTE" header, negative amounts |

## Email Monitor (Agent 4)

### Email Classification

Every incoming email is classified into one of seven categories:

| Category | Description | Routing |
|----------|-------------|---------|
| `BANK_STATEMENT` | Monthly/periodic bank statements | Route to Bank Reconciliation (Agent 5) |
| `SUPPLIER_INVOICE` | Invoices from suppliers/vendors | Route to OCR (Agent 3), then Journal Entry |
| `CUSTOMER_RECEIPT` | Payment receipts or acknowledgments | Route to Accounts Receivable |
| `KRA_NOTICE` | iTax notices, filing reminders, assessments | Route to Tax Compliance (Agent 10) |
| `PAYSLIP` | Employee payslip notifications | Route to Payroll (Agent 16) |
| `INTERNAL` | Internal company emails, memos | Log, no financial action |
| `SPAM` | Marketing, newsletters, unrelated | Ignore, mark as read |

See `references/email_categories.md` for classification examples.

### Email Polling Configuration

| Setting | Value |
|---------|-------|
| Protocol | IMAP (SSL/TLS on port 993) |
| Poll interval | 60 seconds |
| Supported providers | Gmail, Outlook/Office 365, custom IMAP |
| Attachment extraction | PDF, images (PNG/JPG), Excel (XLSX/XLS), CSV |
| Max attachment size | 10 MB |
| Folder monitoring | INBOX (primary), configurable additional folders |

### Email Processing Pipeline

1. **Connect**: IMAP connection with OAuth2 (Gmail/Outlook) or app password
2. **Fetch**: Retrieve unseen emails since last poll
3. **Classify**: Claude Haiku classifies subject + first 500 chars of body
4. **Extract attachments**: Download and store in object storage (S3/GCS)
5. **Route**: Send to appropriate downstream agent based on classification
6. **Mark**: Mark email as read, apply label/folder (e.g., "ADA-Processed")

### Deduplication

- Hash email `Message-ID` header to prevent reprocessing
- Store processed email IDs in Redis with 90-day TTL
- If duplicate detected, skip silently

## LangGraph Node

- **Node name**: `document_capture`
- **State keys consumed**: `document_image`, `email_raw`, `source_channel`
- **State keys produced**: `ocr_result`, `email_classification`, `extracted_document`, `attachments`
- **Next nodes**: `journal_proposal` (for invoices/receipts), `bank_reconciliation` (for bank statements), `tax_compliance` (for KRA notices)

## Model Dependencies

| Component | Model/Library |
|-----------|--------------|
| Text detection | PaddleOCR v2.7+ |
| Document understanding | Donut (MIT) |
| Email classification | Claude Haiku |
| Field extraction fallback | Claude Sonnet (when OCR confidence < 0.8) |
