# Receipt and Invoice Fields Specification

## Overview

This document defines all expected fields from Kenyan receipts and invoices, including mandatory eTIMS (Electronic Tax Invoice Management System) fields effective since September 2024.

## Standard Receipt Fields

### Vendor Information

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vendor_name` | string | Yes | Business/trading name |
| `vendor_pin` | string | Yes | KRA PIN (format: `[AP]\d{9}[A-Z]`) |
| `vendor_address` | string | No | Physical address |
| `vendor_phone` | string | No | Contact phone number |
| `vendor_email` | string | No | Contact email |

### Receipt Identification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_number` | string | Yes | Unique receipt/invoice number |
| `date` | date | Yes | Transaction date (DD/MM/YYYY) |
| `time` | time | No | Transaction time (HH:MM:SS) |
| `cashier` | string | No | Cashier name or ID |
| `till_number` | string | No | POS terminal or till number |

### Line Items

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | array | Yes | List of purchased items |
| `items[].description` | string | Yes | Item name/description |
| `items[].quantity` | number | Yes | Quantity purchased |
| `items[].unit_price` | number | Yes | Price per unit (KES) |
| `items[].total` | number | Yes | Line total (quantity x unit_price) |
| `items[].vat_category` | enum | Yes | `STANDARD` (16%), `ZERO_RATED` (0%), `EXEMPT` |
| `items[].hs_code` | string | No | Harmonized System code (for eTIMS) |

### Totals

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subtotal` | number | Yes | Sum of all line items before VAT |
| `vat_amount` | number | Yes | Total VAT (16% of taxable subtotal) |
| `total` | number | Yes | Grand total (subtotal + VAT) |
| `discount` | number | No | Any discount applied |
| `rounding` | number | No | Rounding adjustment |

### Payment

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payment_method` | enum | Yes | `MPESA`, `CASH`, `CARD`, `BANK_TRANSFER`, `CHEQUE`, `CREDIT` |
| `mpesa_reference` | string | Conditional | Required if payment_method = MPESA |
| `card_last_four` | string | Conditional | Last 4 digits if payment_method = CARD |
| `amount_tendered` | number | No | Cash tendered (for cash payments) |
| `change_given` | number | No | Change returned |

## eTIMS Fields (Mandatory since September 2024)

All tax invoices and receipts issued in Kenya must comply with KRA's eTIMS requirements.

### eTIMS Device Information

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `etims_cu_number` | string | Yes | Control Unit serial number (format: `CU\d{6}`) |
| `etims_cu_invoice_number` | string | Yes | Sequential invoice number from the CU |
| `etims_receipt_number` | string | Yes | eTIMS receipt number (format: `\d{4}-\d{4}-\d{4}`) |
| `etims_date_time` | datetime | Yes | Timestamp from the CU |
| `etims_qr_code` | string | No | QR code data for verification |
| `etims_verification_url` | string | No | URL for online verification |

### eTIMS Tax Breakdown

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tax_category_A` | number | Yes | Taxable amount at 16% (standard rate) |
| `tax_category_B` | number | Yes | Taxable amount at 0% (zero-rated) |
| `tax_category_C` | number | Yes | Exempt amount |
| `tax_category_D` | number | No | Taxable amount at 8% (petroleum) |
| `tax_category_E` | number | No | Excise duty applicable amounts |

## Tax Invoice Additional Fields

For formal tax invoices (as opposed to simple receipts), these additional fields are expected:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `buyer_name` | string | Yes | Purchaser business name |
| `buyer_pin` | string | Yes | Purchaser KRA PIN |
| `buyer_address` | string | No | Purchaser address |
| `invoice_type` | enum | Yes | `ORIGINAL`, `COPY`, `CREDIT_NOTE`, `DEBIT_NOTE` |
| `payment_terms` | string | No | e.g., "Net 30", "Due on Receipt" |
| `due_date` | date | Conditional | Required if payment_terms specified |
| `purchase_order_ref` | string | No | Reference to buyer's PO |
| `delivery_note_ref` | string | No | Reference to delivery note |

## VAT Categories in Kenya

| Category | Rate | Examples |
|----------|------|----------|
| Standard | 16% | Most goods and services |
| Zero-rated | 0% | Exports, certain agricultural inputs, books |
| Exempt | N/A | Financial services, insurance, education, medical |
| Petroleum | 8% | Petroleum products (special rate) |

## Zero-Rated Items (Common)

- Exported goods and services
- Goods supplied to EPZ enterprises
- Agricultural pest control products
- Seeds and fertilizers
- Locally manufactured passenger motor vehicles (first registration)
- Supply of coffee, tea, and pyrethrum to specified processors

## Exempt Items (Common)

- Unprocessed agricultural products
- Financial and insurance services
- Residential accommodation (rent)
- Medical and dental services
- Educational services
- Veterinary services
- Transportation of passengers

## OCR Confidence Thresholds

| Field | Minimum Confidence | Fallback Action |
|-------|-------------------|-----------------|
| `vendor_pin` | 0.95 | Manual verification required |
| `total` | 0.90 | Cross-check against line item sum |
| `vat_amount` | 0.85 | Recalculate from subtotal * 0.16 |
| `date` | 0.90 | Use upload/receive date as fallback |
| `items[].description` | 0.70 | Accept with flag for review |
| `etims_cu_number` | 0.95 | Mandatory re-scan or manual entry |
