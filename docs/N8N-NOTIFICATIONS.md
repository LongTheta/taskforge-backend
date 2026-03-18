# N8N Notifications — Email & SMS via Webhook

TaskForge can send audit events to an N8N webhook. Use N8N workflows to deliver **emails** or **SMS** for security and user events.

## Setup

1. **Configure the webhook URL** in your environment:

   ```bash
   NOTIFICATION_WEBHOOK_URL=https://your-n8n.instance/webhook/xxx
   ```

2. **Create an N8N Webhook trigger** — the URL is your `NOTIFICATION_WEBHOOK_URL`.

3. **Build workflows** that react to the payload and send email or SMS.

## Events Sent

| Action | When | Email in payload |
|--------|------|------------------|
| `login_failure` | Invalid login attempt | `email` (attempted) |
| `mfa_enabled` | Admin enabled MFA | `email` (user) |
| `user_registered` | New user registered | `email` (new user) |

## Webhook Payload

```json
{
  "event_type": "audit",
  "action": "login_failure",
  "success": false,
  "timestamp": "2025-03-18T12:00:00.000000Z",
  "request_id": "abc-123",
  "email": "user@example.com",
  "reason": "invalid_credentials"
}
```

## N8N Workflow Examples

### 1. Email on Login Failure

1. **Webhook** trigger — receives POST from TaskForge
2. **IF** node — filter `action === "login_failure"`
3. **Gmail** or **SendGrid** node — send email to `{{ $json.email }}`:
   - Subject: *"TaskForge: Failed login attempt"*
   - Body: *"Someone tried to log in to your account. If this wasn't you, please contact support."*

### 2. SMS on Login Failure (Twilio)

1. **Webhook** trigger
2. **IF** node — filter `action === "login_failure"`
3. **Twilio** node — send SMS to user's phone (requires phone lookup in DB or separate mapping)
4. Or: use **HTTP Request** to call your user API to resolve `user_id` → phone

### 3. Welcome Email on Registration

1. **Webhook** trigger
2. **IF** node — filter `action === "user_registered"`
3. **Gmail** / **SendGrid** — send welcome email to `{{ $json.email }}`

### 4. MFA Enabled Confirmation

1. **Webhook** trigger
2. **IF** node — filter `action === "mfa_enabled"`
3. **Gmail** / **SendGrid** — send confirmation to `{{ $json.email }}`:
   - Subject: *"TaskForge: MFA enabled"*
   - Body: *"Multi-factor authentication has been enabled for your account."*

## N8N Nodes Used

- **Webhook** — trigger (POST)
- **IF** — filter by `action`
- **Gmail** / **SendGrid** / **SMTP** — email
- **Twilio** — SMS
- **Set** — reshape payload for your use case

## Security Notes

- Webhook is fire-and-forget; TaskForge does not wait for N8N response.
- Use HTTPS for the webhook URL.
- Consider adding a shared secret in N8N (validate `X-Webhook-Secret` header) if you add custom auth later.
- `email` is included for notification delivery; no passwords or tokens are ever sent.
