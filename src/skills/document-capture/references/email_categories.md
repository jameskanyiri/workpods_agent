# Email Classification Categories

## Overview

Agent 4 (Email Monitor) classifies incoming emails into seven categories using Claude Haiku. Classification is based on the email subject line and the first 500 characters of the body text.

## Categories

### 1. BANK_STATEMENT

Monthly or periodic bank statements from commercial banks.

**Routing**: Bank Reconciliation (Agent 5)

**Subject line patterns**:
- "Your monthly statement"
- "Account Statement - April 2026"
- "e-Statement for Account ..."
- "Bank Statement Notification"

**Sender patterns**:
- `*@equitybank.co.ke`
- `*@kcbgroup.com`
- `*@ncbagroup.com`
- `*@co-opbank.co.ke`
- `*@stanbicbank.co.ke`
- `*@absa.co.ke`
- `*@sc.com`

**Attachment types**: PDF, CSV, Excel

**Example**:
```
From: estatements@equitybank.co.ke
Subject: Your Equity Bank Statement for March 2026
Body: Dear Customer, Please find attached your bank statement for the period 01/03/2026 to 31/03/2026...
Attachment: Statement_March_2026.pdf
```

---

### 2. SUPPLIER_INVOICE

Invoices from suppliers or vendors requesting payment.

**Routing**: OCR (Agent 3) for data extraction, then Journal Entry pipeline

**Subject line patterns**:
- "Invoice #..."
- "Tax Invoice"
- "Payment Request"
- "Invoice for services rendered"
- "Proforma Invoice"

**Body indicators**: KRA PIN, amount due, payment terms, bank details, "Please remit"

**Attachment types**: PDF (most common), images

**Example**:
```
From: accounts@supplierxyz.co.ke
Subject: Invoice #INV-2026-0456 - Office Furniture
Body: Dear Sir/Madam, Please find attached our tax invoice for office furniture delivered on 05/04/2026. Amount: KES 125,000 inclusive of VAT. Payment Terms: Net 30. Bank: Equity Bank, A/C: 1234567890...
Attachment: INV-2026-0456.pdf
```

---

### 3. CUSTOMER_RECEIPT

Payment confirmations, receipts, or acknowledgments from customers.

**Routing**: Accounts Receivable update

**Subject line patterns**:
- "Payment Confirmation"
- "Receipt for Payment"
- "Payment Received"
- "Thank you for your payment"

**Body indicators**: "payment of KES...", "receipt number", "transaction reference", "amount received"

**Example**:
```
From: finance@clientcompany.co.ke
Subject: Payment Confirmation - INV-2026-0123
Body: This is to confirm that we have made payment of KES 350,000 via bank transfer. Reference: FT26040912345. Please acknowledge receipt...
```

---

### 4. KRA_NOTICE

Tax-related communications from the Kenya Revenue Authority.

**Routing**: Tax Compliance (Agent 10)

**Subject line patterns**:
- "iTax Notification"
- "Tax Filing Reminder"
- "Notice of Assessment"
- "Tax Compliance Certificate"
- "PIN Certificate"
- "Demand Notice"
- "Objection Decision"

**Sender patterns**:
- `*@kra.go.ke`
- `noreply@itax.kra.go.ke`

**Priority**: HIGH (always surface to business owner)

**Example**:
```
From: noreply@itax.kra.go.ke
Subject: Monthly VAT Return Filing Reminder
Body: Dear Taxpayer, This is a reminder that your VAT return for the period March 2026 is due by 20th April 2026. Please file your return on itax.kra.go.ke...
```

---

### 5. PAYSLIP

Employee payslip notifications or salary-related documents.

**Routing**: Payroll (Agent 16)

**Subject line patterns**:
- "Payslip"
- "Salary Advice"
- "Pay Statement"
- "Remuneration Advice"

**Body indicators**: "basic salary", "PAYE", "NSSF", "NHIF", "Housing Levy", "net pay"

**Example**:
```
From: hr@company.co.ke
Subject: Payslip for March 2026
Body: Dear Employee, Please find attached your payslip for the month of March 2026. Net Pay: KES 85,000...
Attachment: Payslip_March_2026.pdf
```

---

### 6. INTERNAL

Internal company communications that have no direct financial action.

**Routing**: Log only, no financial processing

**Subject line patterns**: Meeting invites, memos, general communications, HR announcements

**Body indicators**: No financial amounts, no invoices, no tax references

**Example**:
```
From: manager@company.co.ke
Subject: Team Meeting - Thursday 2pm
Body: Hi team, reminder about our weekly catch-up meeting tomorrow at 2pm in the boardroom...
```

---

### 7. SPAM

Marketing emails, newsletters, and unsolicited communications.

**Routing**: Ignore, mark as read

**Subject line patterns**:
- "Special Offer"
- "Newsletter"
- "Subscription"
- "Unsubscribe"
- Promotional language

**Example**:
```
From: marketing@randomcompany.com
Subject: SPECIAL OFFER: 50% OFF All Products This Week!
Body: Don't miss out on our biggest sale of the year...
```

## Classification Confidence

| Confidence | Action |
|------------|--------|
| > 0.90 | Auto-route to target agent |
| 0.70 - 0.90 | Route with human notification |
| < 0.70 | Queue for manual classification |

## Multi-Label Handling

Some emails may match multiple categories. Priority order:
1. `KRA_NOTICE` (highest priority - compliance risk)
2. `BANK_STATEMENT`
3. `SUPPLIER_INVOICE`
4. `CUSTOMER_RECEIPT`
5. `PAYSLIP`
6. `INTERNAL`
7. `SPAM` (lowest priority)

If confidence for top two categories is within 0.1, flag for manual review.
