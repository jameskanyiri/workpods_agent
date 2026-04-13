# Intent Classification Taxonomy

## Overview

Agent 1 (WhatsApp Listener) classifies every incoming message into one of five intent categories. Classification uses a lightweight Claude Haiku call with a few-shot prompt. Messages that fail classification default to `NOISE`.

## Categories

### 1. TRANSACTION_RECORDING

The user wants to record a financial event (expense, revenue, transfer, or petty cash entry).

**Trigger signals**: amounts (numbers with currency context), vendor/customer names, payment method mentions, purchase/sale language.

**Examples**:
- "Paid 5k for office supplies via M-Pesa"
- "Received 150,000 from Kamau for invoice #234"
- "Bought fuel 3,500 cash"
- "Transferred 50k to supplier account KCB"
- "Lunch meeting 2.5k mpesa SHK7X2M4LP"
- "Rent paid 80k bank transfer"
- "Sold 10 bags cement at 800 each"
- "Petty cash: tea and snacks 450"
- "USD 500 received from client wire transfer"
- "Staff advance - John 15k mpesa"

### 2. REPORT_REQUEST

The user wants to view, query, or export financial data.

**Trigger signals**: "show me", "how much", "what is", "balance", "report", "summary", "statement", "P&L", "last month", "this week", time-range references.

**Examples**:
- "Show me last month's expenses"
- "What's our revenue this quarter?"
- "P&L for March"
- "How much have we spent on transport?"
- "Send me the trial balance"
- "Outstanding invoices report"
- "Cash flow for this week"
- "What did we pay Supplier X last year?"
- "Aged receivables"
- "VAT report for Q1"

### 3. APPROVAL_RESPONSE

The user is responding to a pending approval request (journal entry, payment, or disbursement).

**Trigger signals**: "approve", "reject", "yes", "no", "ok", "confirmed", "deny", direct reply to an approval message.

**Examples**:
- "Approve"
- "Yes, go ahead"
- "Reject - the amount should be 45k not 50k"
- "Approved. Post it."
- "No, hold that payment"
- "Confirmed"
- "Ok"
- "Reject, wrong account"

**Context requirement**: An approval response is only valid when there is a pending approval in the conversation. If no pending approval exists, reclassify as `QUESTION` or `NOISE`.

### 4. QUESTION

The user is asking a question about their books, accounts, or the system.

**Trigger signals**: question marks, "what", "why", "when", "how", "can you", "is there", inquiry language without a clear report scope.

**Examples**:
- "What's the balance on petty cash?"
- "Why was that entry rejected?"
- "When did we last pay KRA?"
- "What account code is for transport?"
- "Can you explain the variance?"
- "Is the bank reconciliation done?"
- "Who approved the last payment?"
- "What's our NSSF rate?"

### 5. NOISE

Non-financial messages that require no accounting action.

**Trigger signals**: greetings, social messages, media without context, stickers, emojis only, off-topic content.

**Examples**:
- "Good morning"
- "Thanks!"
- "👍"
- (sticker)
- (image without caption)
- "Happy birthday team!"
- "Meeting at 3pm"
- "Hello"

## Classification Rules

1. If the message contains a monetary amount AND a verb implying a financial event, classify as `TRANSACTION_RECORDING`.
2. If the message asks for aggregated data or reports, classify as `REPORT_REQUEST`.
3. If the message is a direct reply to a system-generated approval prompt, classify as `APPROVAL_RESPONSE`.
4. If the message is a question about financial state without requesting a formal report, classify as `QUESTION`.
5. If none of the above apply, classify as `NOISE`.

## Edge Cases

| Message | Classification | Reason |
|---------|---------------|--------|
| "5000" (bare number, no context) | `NOISE` | No verb or financial context |
| "5000 mpesa" | `TRANSACTION_RECORDING` | Payment method implies transaction |
| "How much did we pay?" | `QUESTION` | No specific report scope |
| "How much did we pay last month?" | `REPORT_REQUEST` | Has time range, implies report |
| Image with caption "Receipt from Naivas 3200" | `TRANSACTION_RECORDING` | Caption provides financial context |
| Image without caption | `NOISE` | No financial context (route to OCR separately if receipt detection is enabled) |
| "Ok" with no pending approval | `NOISE` | No approval context |
| "Ok" with pending approval | `APPROVAL_RESPONSE` | Approval context exists |
