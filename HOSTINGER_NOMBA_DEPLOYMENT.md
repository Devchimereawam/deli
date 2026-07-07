# Deli Hosting, Nomba, and Test Guide

## Test The Frontend First

From the project root:

```bash
cd web
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Useful frontend environment variables:

```env
VITE_WHATSAPP_NUMBER=2347089823013
VITE_DJANGO_ADMIN_URL=https://your-deli-subdomain.duckdns.org/admin/
VITE_DJANGO_API_URL=https://your-deli-subdomain.duckdns.org
VITE_QR_CODE_URL=
```

QR code setup:

- If you have a public QR image URL, put it in `VITE_QR_CODE_URL`.
- If you have an image file, upload it to `web/public/whatsapp-qr.png`, then set `VITE_QR_CODE_URL=/whatsapp-qr.png`.
- If this variable is empty, the homepage shows a clean QR placeholder instead of breaking.

Production frontend test after deployment:

```bash
cd /var/www/deli/web
npm install
npm run build
```

Open:

```text
https://your-deli-subdomain.duckdns.org
```

## Nomba Webhook To Submit

Submit this clean HTTPS URL to the Nomba webhook form:

```text
https://your-deli-subdomain.duckdns.org/api/v1/payments/webhooks/nomba/
```

For local ngrok testing, submit:

```text
https://your-ngrok-url.ngrok-free.app/api/v1/payments/webhooks/nomba/
```

Also submit your Nomba sub-account ID in the form. The app still needs this webhook even though the customer experience lives in WhatsApp. WhatsApp handles chat messages; Nomba sends payment confirmations to your backend through this webhook.

## Correct Nomba Environment

Use this base URL for sandbox:

```env
NOMBA_BASE_URL=https://sandbox.nomba.com/v1
```

The code normalizes the base URL, so `https://sandbox.nomba.com` will also work, but the recommended `.env` value includes `/v1`. The code will not produce `/v1/v1`.

Required Nomba variables:

```env
NOMBA_BASE_URL=https://sandbox.nomba.com/v1
NOMBA_ACCOUNT_ID=f666ef9b-888e-4799-85ce-acb505b28023
NOMBA_PARENT_ACCOUNT_ID=f666ef9b-888e-4799-85ce-acb505b28023
NOMBA_SUB_ACCOUNT_ID=your-team-sub-account-id
NOMBA_CLIENT_ID=your-test-or-live-client-id
NOMBA_CLIENT_SECRET=your-test-or-live-private-key
NOMBA_WEBHOOK_SECRET=NombaHackathon2026
NOMBA_CALLBACK_URL=https://your-deli-subdomain.duckdns.org/api/v1/payments/return/
NOMBA_ALLOWED_PAYMENT_METHODS=Card
```

Nomba authentication uses `NOMBA_CLIENT_ID` and `NOMBA_CLIENT_SECRET`.

`NOMBA_ALLOWED_PAYMENT_METHODS=Card` is recommended while testing sandbox checkout because it keeps the hosted page on the card path. Leave it blank later if you want Nomba to show every payment method enabled on your account.

## Nomba Marketplace Checklist Position

This app uses the Nomba hackathon account structure like this:

```text
Parent account ID -> used in every accountId header
Team sub-account ID -> used to scope checkout and transfers
Deli restaurants/riders -> stored in Django, not created as Nomba sub-accounts
```

That matches the hackathon guidance that says not to create sub-accounts programmatically. The marketplace participants live in Deli's database, while money movement is scoped to your assigned Nomba sub-account.

Implemented:

- Client secret and webhook secret from `.env`.
- Checkout through Nomba.
- Checkout amount sent as a naira string, e.g. `7300.00`, so the Nomba hosted page displays `₦7,300` instead of `₦730,000`.
- `accountId` header uses parent account ID.
- Checkout payload includes the assigned `NOMBA_SUB_ACCOUNT_ID`.
- Sandbox checkout uses Nomba's v1 checkout path automatically when `NOMBA_BASE_URL=https://sandbox.nomba.com/v1`.
- Webhook signature verification.
- Webhook idempotency by `requestId`.
- Payment references are unique.
- Reconciliation command.
- Payout transfer support after delivery.
- Recipient bank lookup before payout transfer.
- Health endpoint.

Not used in this MVP:

- Nomba virtual accounts, so over/under-payment virtual-account handling is not applicable.
- Direct debits.
- Tokenized cards.

Payout commands:

```bash
cd /var/www/deli/deli
pipenv run python manage.py payout_delivered_orders
pipenv run python manage.py payout_delivered_orders --execute
```

The first command prepares payout rows without sending money. The second command calls Nomba bank lookup first, then transfers from your assigned sub-account.

## Payment Test

1. Set `.env` with the sandbox values above.
2. Restart Django after changing `.env`.
3. Start the backend:

```bash
cd deli
pipenv run python manage.py runserver 0.0.0.0:8000
```

4. Start ngrok:

```bash
ngrok http 8000
```

5. Put the ngrok HTTPS URL into:

```env
PUBLIC_BASE_URL=https://your-ngrok-url.ngrok-free.app
NGROK_URL=https://your-ngrok-url.ngrok-free.app
NOMBA_CALLBACK_URL=https://your-ngrok-url.ngrok-free.app/api/v1/payments/return/
```

6. Restart Django again.
7. Submit the Nomba webhook URL:

```text
https://your-ngrok-url.ngrok-free.app/api/v1/payments/webhooks/nomba/
```

8. Complete a WhatsApp order and open the returned Nomba checkout link.
9. Confirm the Nomba page shows the expected amount, for example `₦7,300`, not `₦730,000`.
10. Use the current Nomba sandbox successful card path:

```text
Card number: 5434621074252808
Expiry: any future date
CVV: any 3 digits
PIN: 1234
OTP: 9999
```

Nomba controls the OTP screen. Do not use `999999`; it is not the documented success OTP. If the hosted sandbox page currently forces a six-digit OTP and rejects `9999`, that is Nomba sandbox behavior, not Deli code. In that case, retry with the card test path Nomba currently gives your team or ask the Nomba hackathon channel for the active six-digit approval OTP.

Do not use the declined sandbox card:

```text
5484497218317651
```

If you use bank transfer in sandbox, the checkout page may wait for a simulated transfer event. For the fastest MVP test, use `NOMBA_ALLOWED_PAYMENT_METHODS=Card` and pay with the card above.

What should happen:

```text
Customer pays in Nomba
        |
        v
Nomba sends webhook to /api/v1/payments/webhooks/nomba/
        |
        v
Deli marks payment successful
        |
        v
Stock is deducted once
        |
        v
Restaurant and rider are asked "Available?"
        |
        v
Deli Dash admin receives settlement preview
```

If the Nomba page keeps saying "processing your payment":

- Your Nomba webhook URL may not be submitted yet.
- Your ngrok URL may have changed after you submitted it.
- Your Django server may not be running.
- Sandbox checkout webhooks can be delayed or inconsistent during hackathon testing.
- You chose bank transfer instead of card. Use the successful sandbox card above for the reliable test path.
- You used a declined sandbox card or the older hackathon card number no longer accepted by the current Nomba checkout sandbox.

Manual status requery:

```bash
cd deli
pipenv run python manage.py requery_nomba_checkout PAY-REFERENCE
```

Credential safety:

- The code does not hardcode Nomba test or live credentials.
- Sandbox testing uses the test credentials in `.env`.
- Live operation uses the live credentials in `.env`.
- `requery_nomba_checkout PAY-REFERENCE` always calls Nomba; it does not fake success.
- `payout_delivered_orders` prepares payout records without sending money.
- `payout_delivered_orders --execute` calls Nomba transfer APIs using the credentials currently in `.env`.

You do not manually inform Nomba that you paid. In sandbox, the successful card flow above is the test payment. After the OTP `9999` is accepted, Nomba marks the sandbox transaction successful and your app receives the webhook or can confirm it with requery.

## Payment And Payout Test Matrix

Test 1: checkout creation

```text
WhatsApp order -> choose rider -> Deli sends Nomba Continue button
```

Expected:

- Payment row is created in Django admin.
- Order status becomes `Awaiting Payment`.
- Nomba receives checkout amount as a naira string, e.g. `7300.00`.
- The Nomba hosted page and WhatsApp message should both show `₦7,300`, not `₦730,000`.

Test 2: webhook success

```text
Complete Nomba payment
```

Expected:

- `NombaWebhookEvent` row is created.
- Duplicate webhook `requestId` is ignored.
- Payment status becomes `Success`.
- Order status becomes `Paid`.
- Inventory is deducted once.
- Restaurant/rider availability messages are sent.

Test 3: manual requery

```bash
cd deli
pipenv run python manage.py requery_nomba_checkout PAY-REFERENCE
```

Expected:

- If Nomba reports success, the same post-payment flow runs.
- If Nomba still reports pending, the order stays pending.

Test 4: payout preparation after delivery

```bash
cd deli
pipenv run python manage.py payout_delivered_orders --order ORD-REFERENCE
```

Expected:

- Payout rows are created.
- No money is sent.
- Restaurant payout = food subtotal minus restaurant platform fee.
- Rider payout = delivery fee minus rider platform fee.

Test 5: payout execution

```bash
cd deli
pipenv run python manage.py payout_delivered_orders --order ORD-REFERENCE --execute
```

Expected:

- Nomba bank lookup runs first.
- If account name matches, transfer is sent from your assigned sub-account.
- Payout status becomes `Success` or `Failed`.

Payouts are not automatic by default. After delivery, Deli Dash admin receives a WhatsApp message with payout details and the command to run. This is deliberate for MVP safety. You can automate it later with a cron or admin approval button, but manual `--execute` avoids accidental real transfers during demos.

## WhatsApp Configuration

Required WhatsApp variables:

```env
WHATSAPP_ACCESS_TOKEN=your-meta-cloud-api-token
WHATSAPP_PHONE_NUMBER_ID=your-meta-phone-number-id
WHATSAPP_VERIFY_TOKEN=any-secret-string-you-choose
WHATSAPP_PUBLIC_NUMBER=2347089823013
DELI_DASH_WHATSAPP_NUMBER=234XXXXXXXXXX
WHATSAPP_STALE_MESSAGE_MINUTES=20
```

Where to get `WHATSAPP_PHONE_NUMBER_ID`:

1. Go to Meta Developers.
2. Open your app.
3. Open WhatsApp > API Setup.
4. Copy the Phone number ID, not the display phone number.

Your webhook logs also show it under:

```text
metadata.phone_number_id
```

Meta webhook callback URL:

```text
https://your-deli-subdomain.duckdns.org/api/v1/whatsapp/webhook/
```

Use your `WHATSAPP_VERIFY_TOKEN` when Meta asks for the verify token.

## Hostinger OpenLiteSpeed Django VPS Deployment

Use this section for the Hostinger `Django/OpenLiteSpeed` VPS image you selected.

The lowest VPS plan is acceptable for a hackathon MVP if it runs:

- OpenLiteSpeed as the public web server.
- Django backend on `127.0.0.1:8000`.
- Vite React frontend served as static files from `web/dist`.
- SQLite for the hackathon demo database.
- systemd backend service so the WhatsApp and payment webhooks keep running after SSH closes.

Hostinger VPS plans are usually unmanaged. You should expect to manage Linux updates, firewall, OpenLiteSpeed, SSL, app processes, logs, and backups yourself. Domain promos change; do not depend on a free paid domain being included with the cheapest VPS. Use DuckDNS first if you cannot pay for a domain yet.

If you cannot afford a paid domain yet, use DuckDNS. It is better than free ngrok for this app because Nomba and WhatsApp need stable HTTPS webhook URLs. Free ngrok URLs can change when the tunnel restarts, which breaks submitted webhook URLs.

Recommended free-domain setup:

```text
Frontend: https://your-deli-subdomain.duckdns.org
Django API: https://your-deli-subdomain.duckdns.org/api/
Django admin: https://your-deli-subdomain.duckdns.org/admin/
Nomba webhook: https://your-deli-subdomain.duckdns.org/api/v1/payments/webhooks/nomba/
WhatsApp webhook: https://your-deli-subdomain.duckdns.org/api/v1/whatsapp/webhook/
```

DuckDNS setup:

1. Go to `https://www.duckdns.org`.
2. Sign in with GitHub, Google, Reddit, or Twitter.
3. Create a subdomain, for example `mydeli`.
4. In the IP field, enter your Hostinger VPS public IP address.
5. Click `update ip`.
6. Your app hostname becomes:

```text
https://mydeli.duckdns.org
```

If your VPS public IP changes later, return to DuckDNS and update the IP. Most VPS IPs stay stable.

Recommended Hostinger image:

```text
OS with Control Panel -> Django/OpenLiteSpeed
```

During first SSH login, OpenLiteSpeed may ask for a domain. Use your DuckDNS subdomain after you create it, for example:

```text
mydeli.duckdns.org
```

If you have not created DuckDNS yet, press `CTRL+C`, finish DuckDNS first, then SSH again and complete the prompt.

Connect to the VPS:

```bash
ssh root@YOUR_VPS_PUBLIC_IP
```

Update the server:

```bash
apt update
apt upgrade -y
```

Get the OpenLiteSpeed WebAdmin password:

```bash
cat /root/.litespeed_password
```

Open WebAdmin:

```text
https://YOUR_VPS_PUBLIC_IP:7080
```

If port `7080` is blocked, allow it temporarily:

```bash
ufw allow 7080
```

After setup, close WebAdmin again:

```bash
ufw delete allow 7080
```

Install packages:

```bash
apt install -y python3 python3-pip python3-venv pipenv nodejs npm git ufw certbot
which pipenv
which npm
```

If `which pipenv` returns `/usr/bin/pipenv`, keep `/usr/bin/pipenv` in the systemd service below. If it returns a different path, use that path.

Clone or upload the project:

```bash
mkdir -p /var/www
cd /var/www
git clone your-repo-url deli
```

Backend setup:

```bash
cd /var/www/deli/deli
cp .env.example .env
nano .env
pipenv install
pipenv install gunicorn
pipenv run python manage.py migrate
pipenv run python manage.py createsuperuser
pipenv run python manage.py collectstatic
```

Use `DEBUG=False` in production:

```env
DEBUG=False
SECRET_KEY=generate-a-long-random-secret
PUBLIC_BASE_URL=https://your-deli-subdomain.duckdns.org
NGROK_URL=
NOMBA_CALLBACK_URL=https://your-deli-subdomain.duckdns.org/api/v1/payments/return/
```

Create backend systemd service:

```bash
nano /etc/systemd/system/deli-backend.service
```

```ini
[Unit]
Description=Deli Django Backend
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/deli/deli
Environment="PIPENV_VENV_IN_PROJECT=1"
ExecStart=/usr/bin/pipenv run gunicorn deli.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 90
Restart=always

[Install]
WantedBy=multi-user.target
```

Frontend setup:

```bash
cd /var/www/deli/web
nano .env
```

```env
VITE_WHATSAPP_NUMBER=2347089823013
VITE_DJANGO_ADMIN_URL=https://your-deli-subdomain.duckdns.org/admin/
VITE_DJANGO_API_URL=https://your-deli-subdomain.duckdns.org
VITE_QR_CODE_URL=
```

Build:

```bash
npm install
npm run build
```

Start backend service:

```bash
systemctl daemon-reload
systemctl enable deli-backend
systemctl start deli-backend
systemctl status deli-backend
```

## Domain And OpenLiteSpeed

Recommended free option: DuckDNS.

```text
DuckDNS subdomain: your-deli-subdomain.duckdns.org
DuckDNS IP value:  VPS_PUBLIC_IP
```

This single hostname is enough.

OpenLiteSpeed will route:

```text
/                       -> Vite static frontend at /var/www/deli/web/dist/
/api/                   -> Django backend on 127.0.0.1:8000
/admin/                 -> Django backend on 127.0.0.1:8000
/health/                -> Django backend on 127.0.0.1:8000
/static/                -> /var/www/deli/deli/staticfiles/
/media/                 -> /var/www/deli/deli/media/
```

OpenLiteSpeed WebAdmin setup:

1. Visit `https://YOUR_VPS_PUBLIC_IP:7080`.
2. Log in with username `admin` and the password from `cat /root/.litespeed_password`.
3. Go to `Virtual Hosts`.
4. Open the default virtual host, usually `Example`.
5. Go to `External App`.
6. Add `Web Server` external app:

```text
Name: deli_django
Address: 127.0.0.1:8000
Max Connections: 100
Initial Request Timeout: 90
Retry Timeout: 0
```

7. Go to `Context`.
8. Add static context for Django static files:

```text
Type: Static
URI: /static/
Location: /var/www/deli/deli/staticfiles/
Accessible: Yes
```

9. Add static context for media files:

```text
Type: Static
URI: /media/
Location: /var/www/deli/deli/media/
Accessible: Yes
```

10. Add proxy context for Django API:

```text
Type: Proxy
URI: /api/
Web Server: deli_django
```

11. Add proxy context for Django admin:

```text
Type: Proxy
URI: /admin/
Web Server: deli_django
```

12. Add proxy context for health check:

```text
Type: Proxy
URI: /health/
Web Server: deli_django
```

13. Add static context for the public frontend:

```text
Type: Static
URI: /
Location: /var/www/deli/web/dist/
Accessible: Yes
```

14. Save changes and perform a `Graceful Restart`.

For SSL, use the domain prompt if OpenLiteSpeed offers it after SSH login. If you need to create the certificate manually:

```bash
certbot certonly --webroot -w /var/www/html/ -d your-deli-subdomain.duckdns.org
```

Then in OpenLiteSpeed WebAdmin:

```text
Listeners -> SSL
Private Key File: /etc/letsencrypt/live/your-deli-subdomain.duckdns.org/privkey.pem
Certificate File: /etc/letsencrypt/live/your-deli-subdomain.duckdns.org/fullchain.pem
Chained Certificate: Yes
```

Save and perform a `Graceful Restart`.

Force HTTPS rewrite:

```text
Virtual Hosts -> Example -> Rewrite -> Rewrite Rules
```

```apache
RewriteCond %{SERVER_PORT} 80
RewriteRule ^(.*)$ https://your-deli-subdomain.duckdns.org/$1 [R,L]
```

After SSL, update `/var/www/deli/deli/.env`:

```env
PUBLIC_BASE_URL=https://your-deli-subdomain.duckdns.org
NOMBA_CALLBACK_URL=https://your-deli-subdomain.duckdns.org/api/v1/payments/return/
```

Submit these production webhooks:

```text
Nomba:    https://your-deli-subdomain.duckdns.org/api/v1/payments/webhooks/nomba/
WhatsApp: https://your-deli-subdomain.duckdns.org/api/v1/whatsapp/webhook/
```

If you later buy a domain, keep the same OpenLiteSpeed contexts and replace `your-deli-subdomain.duckdns.org` with your paid domain.

Restart:

```bash
systemctl restart deli-backend
systemctl restart lsws
```

## Keep The App Always On

This service keeps the backend running after SSH closes. The frontend is static, so OpenLiteSpeed serves it directly from `web/dist` and no frontend process is needed.

```bash
sudo systemctl status deli-backend
```

Logs:

```bash
sudo journalctl -u deli-backend -f
```

Firewall:

```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

Do you need a cron job for Nomba webhooks?

- If you host on this Hostinger VPS with DuckDNS and systemd services, you do not need a cron job just to keep the webhook awake. VPS services stay online.
- A cron health check is still useful so you notice failures quickly.
- If you use ngrok, Render free tier, or anything that sleeps/changes URL, you do need a pinger or a stable hosting option.

Recommended health cron:

```bash
crontab -e
```

```cron
*/5 * * * * curl -fsS https://your-deli-subdomain.duckdns.org/health/ >/dev/null || systemctl restart deli-backend
```

Nomba signs webhooks with:

```env
NOMBA_WEBHOOK_SECRET=NombaHackathon2026
```

The endpoint must be reachable at the exact moment Nomba sends the event. If your server is down, asleep, or the URL changed, the webhook can be lost.

## Health Checks

Judge/backend health endpoint:

```text
https://your-deli-subdomain.duckdns.org/health/
```

Expected response:

```json
{
  "status": "healthy",
  "service": "Deli",
  "version": "1.0.0"
}
```

## Nightly Nomba Reconciliation

Manual:

```bash
cd /var/www/deli/deli
pipenv run python manage.py reconcile_nomba
```

Cron:

```bash
crontab -e
```

```cron
30 2 * * * cd /var/www/deli/deli && /usr/bin/pipenv run python manage.py reconcile_nomba >> /var/log/deli-reconcile.log 2>&1
```

## WhatsApp Visual Support

Implemented safely:

- Text menus with cleaner visual hierarchy.
- Images sent with restaurant/menu captions.
- Interactive reply buttons for registration, business home, delivery confirmation, and reviews.
- Inbound button/list replies are converted back into normal text commands.
- Buttons fall back to text if Meta rejects the interactive payload.

Not implemented yet:

- Product catalogs.
- Carousel cards.
- WhatsApp commerce product cards.

Reason: those need additional Meta commerce/catalog setup and richer webhook routing. They are good next steps, but not worth risking the MVP flow on launch day.
