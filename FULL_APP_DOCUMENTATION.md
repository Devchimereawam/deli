# Deli Full Product And Technical Documentation

## Product Summary

Deli is a WhatsApp-first food ordering marketplace. Customers discover meals near them, order through WhatsApp, pay through Nomba, and receive restaurant/rider updates in the same chat. Restaurants and delivery riders can also use WhatsApp to register, update availability, manage simple inventory, and coordinate orders.

The MVP has three surfaces:

- WhatsApp conversation app for customers, restaurants, and riders.
- Django backend for state, menus, cart, orders, payments, payouts, admin, and webhooks.
- Vite React public site for the showcase homepage and simple partner/admin entry points.

AI is not required for the MVP. The "Type Order" feature uses deterministic matching against menu item names so it can run on the same low-cost VPS without paying for an AI model API.

## Core User Roles

Customer:
- Registers once per WhatsApp number.
- Sets location.
- Sees hot meals and best rated restaurants near the saved area.
- Uses Type Order, Browse Restaurants, or Search Food.
- Adds items to cart.
- Confirms delivery details.
- Chooses rider.
- Pays with Nomba.
- Tracks order updates.
- Reviews meal or restaurant after delivery.

Restaurant:
- Registers by WhatsApp with name, contact, phone, WhatsApp, cuisine, address, and bank details.
- Uses business home: Admin or Order Food.
- Updates status, prep time, hours, prices, sold out/available state, and inventory through WhatsApp.
- Receives order availability prompt.
- Accepts/rejects orders.
- Confirms dispatch after handing food to rider.

Delivery rider:
- Registers by WhatsApp with name, phone, WhatsApp, vehicle, base fee, and bank details.
- Uses business home: Admin or Order Food.
- Updates available/busy status.
- Updates fee and vehicle.
- Receives delivery prompt.
- Confirms pickup and delivery.

Deli Dash admin:
- Receives settlement/payout preview after order completion.
- Can run payout preparation and payout execution commands.
- Handles fallback fulfillment for big restaurants or providers that do not respond.

## Customer Flow

```text
Hey
  -> first-time registration if needed
  -> location
  -> home
  -> Type Order / Browse Restaurants / Search Food
  -> menu item details
  -> cart
  -> checkout
  -> ask name if missing
  -> delivery details
  -> confirm delivery details
  -> choose rider
  -> Nomba checkout
  -> webhook success
  -> restaurant/rider coordination
  -> delivered
  -> review
```

## Type Order Flow

The home menu includes `Type Order`.

Example user message:

```text
3 plates of jollof rice, 2 cokes, 1 meat pie
```

The parser:

- Searches available menu items in the customer's area.
- Matches exact/simple menu item names.
- Reads nearby numeric quantities or number words.
- Defaults quantity to `1`.
- Keeps the order within one restaurant.
- Shows a confirmation before adding items to the cart.

If the text cannot be confidently matched, the customer is sent to Search Food or Browse Restaurants.

## WhatsApp Interactive Support

Implemented:

- Registration account type buttons.
- Home menu list.
- Restaurant list.
- Menu item list inside a restaurant.
- Meal detail buttons: Add to Cart, Back to Menu, Menu.
- Cart checkout buttons.
- Delivery confirmation buttons.
- Delivery rider list.
- Payment URL button to Nomba.
- Review buttons.
- Inbound button/list replies normalize back into text commands.
- Outbound buttons/lists fall back to text if Meta rejects the payload.

Not implemented in this MVP:

- WhatsApp product catalogs.
- Carousel cards.
- Commerce product cards.

Those require additional Meta catalog/commerce setup and are better as a second pass after the core order/payment flow is stable.

## Payment And Nomba Design

Nomba is used for checkout and payout support.

Environment:

```env
NOMBA_BASE_URL=https://sandbox.nomba.com/v1
NOMBA_ACCOUNT_ID=f666ef9b-888e-4799-85ce-acb505b28023
NOMBA_PARENT_ACCOUNT_ID=f666ef9b-888e-4799-85ce-acb505b28023
NOMBA_SUB_ACCOUNT_ID=your-team-sub-account-id
NOMBA_CLIENT_ID=your-test-or-live-client-id
NOMBA_CLIENT_SECRET=your-test-or-live-private-key
NOMBA_WEBHOOK_SECRET=NombaHackathon2026
NOMBA_CALLBACK_URL=https://your-domain/api/v1/payments/return/
NOMBA_ALLOWED_PAYMENT_METHODS=Card
```

Important behavior:

- The parent account ID is used in the `accountId` header.
- The team sub-account ID scopes checkout/transfers.
- Checkout amount is sent as a naira string, for example `7300.00`, so hosted checkout shows NGN 7,300, not NGN 730,000.
- Sandbox checkout uses the v1 checkout path automatically.
- Nomba access tokens are cached.
- Webhook signatures are verified with `NombaHackathon2026`.
- Duplicate webhooks are ignored by unique request ID.
- Payment references are unique.
- Payout references are unique.

Webhook to submit:

```text
https://your-deli-subdomain.duckdns.org/api/v1/payments/webhooks/nomba/
```

The app needs this webhook even though the customer experience is on WhatsApp. WhatsApp receives chat events; Nomba sends payment events.

## Sandbox Payment Testing

Use this successful card:

```text
Card number: 5434621074252808
Expiry: any future date
CVV: any 3 digits
PIN: 1234
OTP: 9999
```

Nomba controls the OTP screen. Do not use `999999`; it is not the documented success OTP. If the hosted sandbox page forces a six-digit OTP and rejects `9999`, ask the Nomba hackathon channel for the active six-digit approval OTP.

Use `NOMBA_ALLOWED_PAYMENT_METHODS=Card` during sandbox testing to stay on the reliable card path.

You do not manually tell Nomba that you paid. Completing the sandbox card flow is the test payment. If the webhook does not arrive, use:

```bash
cd deli
pipenv run python manage.py requery_nomba_checkout PAY-REFERENCE
```

## Payouts

Payouts are deliberately not automatic in this MVP.

After delivery, Deli Dash admin receives details. Then run:

```bash
cd deli
pipenv run python manage.py payout_delivered_orders --order ORD-REFERENCE
```

To execute transfers:

```bash
pipenv run python manage.py payout_delivered_orders --order ORD-REFERENCE --execute
```

The command:

- Prepares payout rows.
- Runs Nomba bank lookup before transfer.
- Sends transfers only when `--execute` is used.
- Uses the current `.env`, so test credentials hit sandbox and live credentials hit production.

## Inventory And Ratings

Inventory:

- Cart creation does not deduct stock.
- Payment success deducts inventory once.
- If inventory reaches zero, the menu item becomes unavailable.

Ratings:

- Menu item reviews update menu item rating.
- Restaurant reviews update restaurant rating.
- Home recommendations use top rated available menu items and restaurants in the customer's area.

## Hosting Summary

Recommended hackathon deployment:

- Hostinger VPS with Django/OpenLiteSpeed image.
- DuckDNS free subdomain.
- OpenLiteSpeed reverse proxy.
- Django backend on `127.0.0.1:8000`.
- Vite React frontend served as static files from `web/dist`.
- SQLite database.
- systemd for backend/frontend uptime.
- Certbot/Let's Encrypt SSL.

No keep-awake cron is required on a real VPS, but a health cron is useful:

```cron
*/5 * * * * curl -fsS https://your-deli-subdomain.duckdns.org/health/ >/dev/null || systemctl restart deli-backend
```

Detailed deployment steps live in:

```text
HOSTINGER_NOMBA_DEPLOYMENT.md
```

## Key Endpoints

```text
GET  /health/
GET  /api/v1/payments/return/
POST /api/v1/payments/webhooks/nomba/
GET  /api/v1/whatsapp/webhook/
POST /api/v1/whatsapp/webhook/
GET  /admin/
```

## Files To Know

```text
deli/whatsapp/services/router_service.py      WhatsApp state router
deli/whatsapp/services/home_handler.py        Customer home menu
deli/whatsapp/handlers/typed_order.py         Typed order parser
deli/whatsapp/handlers/menu.py                Restaurant menu list
deli/whatsapp/handlers/checkout.py            Item/cart/checkout/rider/payment flow
deli/whatsapp/services/whatsapp_service.py    Meta Cloud API sender
deli/payments/services/payment_service.py     Nomba auth/checkout/webhook/transfer client
deli/orders/services/order_service.py         Order creation, inventory deduction, provider notifications
web/app/page.tsx                              Public homepage
web/app/globals.css                           Public/admin styling
```

## MVP Readiness Checklist

- Customer can start from WhatsApp.
- First-time users choose account type.
- Returning users skip registration.
- Session can restart from home after stale timeout/hello flow.
- Customer can browse restaurants near their saved area.
- Customer can browse menu items in an interactive list.
- Customer can view meal image/details with Add to Cart buttons.
- Customer can type an order in one message.
- Cart blocks mixed-restaurant checkout.
- Checkout asks name only if missing.
- Delivery details are confirmed before rider selection.
- Rider choice includes fee/rating/vehicle.
- Nomba checkout opens through a URL button.
- Payment webhook is verified and idempotent.
- Stock deducts once after payment success.
- Restaurant/rider are contacted after payment.
- Deli Dash fallback exists for provider timeout.
- Review flow updates ratings.
- Health endpoint exists.
- Reconciliation command exists.
- Payout preparation and execution command exists.
- Hostinger OpenLiteSpeed deployment guide exists.
