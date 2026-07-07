# Deli

Deli is a WhatsApp-first food ordering MVP with a Django backend, Nomba payments, restaurant/rider operations through WhatsApp, and a Vite React showcase/admin frontend.

## Quick Start

Backend:

```bash
cd deli
cp .env.example .env
pipenv install
pipenv run python manage.py migrate
pipenv run python manage.py runserver
```

Frontend:

```bash
cd web
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Full VPS hosting guide:

```text
HOSTINGER_NOMBA_DEPLOYMENT.md
```

Full product/technical documentation and Figma/Miro prompt pack:

```text
FULL_APP_DOCUMENTATION.md
```

## MVP Flow

```text
Customer says Hi
        |
        v
Register as Customer / Restaurant / Rider
        |
        v
Set customer location
        |
        v
Home: hot meals, best restaurants, browse, search, orders
        |
        v
Choose restaurant
        |
        v
Browse menu with restaurant image caption
        |
        v
Choose meal image/details
        |
        v
Add to cart
        |
        v
Checkout
        |
        v
Save customer name if missing
        |
        v
Confirm delivery details
        |
        v
Choose delivery rider
        |
        v
Pay with Nomba checkout
        |
        v
Nomba webhook marks order paid
        |
        v
Restaurant and rider are asked "Available?"
        |
        v
Order instructions sent
        |
        v
Restaurant confirms dispatch
        |
        v
Rider confirms delivery
        |
        v
Customer reviews meal or restaurant
```

## Nomba Checklist Status

Security:

- Client secret and webhook secret are loaded from environment variables.
- The real `.env` is ignored and untracked; use `.env.example` for placeholders.
- Nomba webhooks verify `nomba-signature`.
- Webhooks are idempotent through `NombaWebhookEvent.request_id`.
- Payments use unique `merchant_reference` values.
- Payouts use stable unique `merchant_reference` values per order recipient.

Correctness:

- Checkout amounts are sent to Nomba as naira strings, e.g. `7300.00`, because the current checkout endpoint displays numeric values as naira on the hosted page.
- Nomba access tokens are cached for 55 minutes.
- `accountId` header uses the parent account ID.
- Checkout payload is scoped to `NOMBA_SUB_ACCOUNT_ID`.
- Sandbox checkout automatically uses Nomba's `/v1/checkout/order` path when `NOMBA_BASE_URL=https://sandbox.nomba.com/v1`.
- `NOMBA_ALLOWED_PAYMENT_METHODS=Card` can be used during sandbox testing to keep checkout on the reliable card success path.
- Transfer payouts resolve recipient account names before transfer.
- Virtual accounts are not used in this MVP, so over/under-payment handling is not applicable to the current payment path.

Operations:

- `/health/` is available for judges.
- `reconcile_nomba` compares Nomba transactions to local payments.
- Nomba checkout and transfer calls log `merchantTxRef`.
- `payout_delivered_orders` prepares and optionally executes post-delivery payouts.

Marketplace track position:

- The app uses the assigned hackathon sub-account for checkout and transfers.
- It does not create sub-accounts per restaurant because the hackathon guidance says not to create sub-accounts programmatically.
- Restaurants and riders are local marketplace participants in Deli's database.
- Vendor/rider payouts are supported through Nomba bank transfers from the assigned sub-account after delivery.

## Nomba URLs

Recommended sandbox env:

```env
NOMBA_BASE_URL=https://sandbox.nomba.com/v1
NOMBA_ALLOWED_PAYMENT_METHODS=Card
```

Auth uses `/v1`. Production checkout uses `/v1/checkout/order`; sandbox checkout uses `/v1/checkout/order`.

Transfers use `/v2/transfers/bank/{NOMBA_SUB_ACCOUNT_ID}`.

The code normalizes versions, so it does not produce `/v1/v1`.

Sandbox checkout uses Nomba's v1 checkout path internally. To test a successful sandbox card payment, use:

```text
Card number: 5434621074252808
Expiry: any future date
CVV: any 3 digits
PIN: 1234
OTP: 9999
```

Nomba controls the OTP screen. Do not use `999999`; it is not the documented success OTP. If the hosted sandbox page forces a six-digit OTP and rejects `9999`, ask the Nomba hackathon channel for the active six-digit approval OTP.

## Webhooks

Nomba:

```text
https://your-deli-subdomain.duckdns.org/api/v1/payments/webhooks/nomba/
```

WhatsApp:

```text
https://your-deli-subdomain.duckdns.org/api/v1/whatsapp/webhook/
```

## Main Models

```text
Customer
  - phone
  - name
  - account_type
  - default_address

ConversationState
  - current_step
  - selected_restaurant
  - selected_menu_item
  - selected_delivery_rider
  - selected_order
  - delivery details
  - search result ids/types

Restaurant
  - name
  - phone / whatsapp_number
  - area
  - logo / cover_image
  - rating / total_reviews
  - is_active
  - send_orders_to_deli_dash
  - estimated_prep_minutes
  - bank details

MenuItem
  - restaurant
  - category
  - name
  - price
  - image
  - is_available
  - rating / total_reviews

Inventory
  - menu_item
  - quantity
  - low_stock_threshold

DeliveryRider
  - name
  - phone / whatsapp_number
  - area
  - vehicle_type
  - base_fee
  - rating / total_reviews
  - is_available
  - bank details

Order
  - customer
  - restaurant
  - delivery_rider
  - status
  - subtotal / delivery_fee / total
  - checkout_reference
  - payment_reference
  - provider availability statuses

Payment
  - order
  - merchant_reference
  - checkout_url
  - amount
  - status

Payout
  - order
  - recipient_type
  - amount
  - bank details
  - resolved_account_name
  - merchant_reference
  - status

NombaWebhookEvent
  - request_id
  - event_type
  - payload
```

## WhatsApp Commands

Customer:

```text
home
cart
back
search rice
review
clear cart
```

Restaurant admin:

```text
open
closed
orders
menu
sold out ITEM NAME
available ITEM NAME
inventory ITEM NAME = 10
price ITEM NAME = 2500
prep 30
hours MON 09:00-21:00
closed day SUN
```

Add or update a meal:

```text
add meal
Name: Smoky Jollof Rice
Price: 2500
Category: Rice Meals
Description: Party-style jollof with chicken
Stock: 20
Available: yes
```

Update restaurant profile:

```text
profile
Name: Adaeze Kitchen
Cuisine: Home Baker
Address: 12 Admiralty Way, Lekki
Contact: Adaeze
WhatsApp: 2348011112222
```

Restaurant images:

```text
Send image with caption: logo
Send image with caption: meal Smoky Jollof Rice
```

Rider admin:

```text
available
busy
closed
jobs
fee 1500
vehicle Bike
```

Provider order replies:

```text
YES
NO
1
```

`YES` accepts an availability request. `NO` declines. `1` confirms restaurant dispatch or rider delivery depending on who replies.

## WhatsApp Visual Support

Implemented safely:

- Restaurant/logo image messages with captions.
- Meal image messages with details in the caption.
- Interactive buttons for first registration, business home, delivery confirmation, and review choice.
- Inbound interactive replies converted back to normal text commands.
- Fallback to text if Meta rejects interactive messages.

Not implemented yet:

- Product catalogs.
- Carousel cards.
- WhatsApp commerce product cards.

These need additional Meta commerce/catalog setup and richer webhook routing. They should be added after the text/image MVP is stable.

## Important Management Commands

Reconcile Nomba:

```bash
cd deli
pipenv run python manage.py reconcile_nomba
```

Requery Nomba checkout:

```bash
cd deli
pipenv run python manage.py requery_nomba_checkout PAY-REFERENCE
```

Prepare delivered-order payouts without sending money:

```bash
cd deli
pipenv run python manage.py payout_delivered_orders
```

Execute payouts:

```bash
cd deli
pipenv run python manage.py payout_delivered_orders --execute
```

Execute one order:

```bash
cd deli
pipenv run python manage.py payout_delivered_orders --order ORD-REFERENCE --execute
```

Payouts are not automatic by default. When delivery is confirmed, Deli Dash admin receives a WhatsApp message with the restaurant payout, rider payout, Deli fees, bank details, and the exact command to run.

## API Endpoints

Core:

```text
GET  /health/
POST /api/v1/whatsapp/webhook/
POST /api/v1/payments/webhooks/nomba/
GET  /api/v1/payments/return/
GET  /admin/
```

DRF app prefixes:

```text
/api/v1/users/
/api/v1/restaurants/
/api/v1/orders/
/api/v1/cart/
/api/v1/payments/
/api/v1/delivery/
```

## Session And Duplicate Protection

- Incoming WhatsApp message IDs are stored in `ProcessedMessage`.
- Duplicate message IDs are ignored.
- Stale WhatsApp messages older than `WHATSAPP_STALE_MESSAGE_MINUTES` are ignored.
- Default stale/session timeout is 20 minutes.
- If a customer returns with `hi`, `hey`, `home`, `menu`, or `start` after timeout, the conversation resets to the correct home screen.

## AI Decision

AI was not added to this MVP because reliable natural language, voice, and image understanding would require a paid API or a much larger local model host than the cheap VPS target. The implemented admin commands cover the core business actions without extra AI cost.
