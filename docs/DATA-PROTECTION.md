# Data Protection and Encryption

## Data Stored

| Data Type | Classification | Storage |
|-----------|----------------|---------|
| User credentials (hashed) | Password hash | PostgreSQL |
| User email | PII | PostgreSQL |
| Tasks | User-scoped application data | PostgreSQL |
| Notes | User-scoped application data | PostgreSQL |
| JWT tokens | Session/transient | Client-held |

**Not implemented:** Formal data classification engine, DLP, field-level encryption.

## Production Expectations

### TLS in Transit

- **API:** TLS termination at ingress/load balancer. Application does not terminate TLS.
- **Database:** Use `postgresql://` with `sslmode=require` (or equivalent) in `DATABASE_URL` for production.

### Encryption at Rest

- **Database:** PostgreSQL encryption at rest is deployment-dependent. Use managed PostgreSQL (e.g. RDS, Cloud SQL) with encryption enabled, or configure PostgreSQL for encryption at rest.
- **Secrets:** Use External Secrets Operator or Vault; avoid plaintext in ConfigMaps.

### Secure Secret Injection

- **Production:** No placeholder secrets. Use `deploy/external-secrets/` or equivalent.
- **Rotation:** Rotate `SECRET_KEY` and DB credentials periodically; no built-in rotation.

### Audit Log Handling

- Audit logs include `event_type: audit`, `user_id`, `action`, `resource_id`, `request_id`.
- **Retention:** Configure at log aggregation layer (Loki, SIEM).
- **Sensitivity:** No passwords or tokens in audit logs.

## Compliance Notes

- **NIST 800-53 SC-28:** Encryption at rest — validate at deployment.
- **NIST 800-53 SC-8:** Encryption in transit — TLS at ingress and DB connection.
- **FedRAMP:** Document encryption and key management in your deployment.
