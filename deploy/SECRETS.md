# Secrets Management

## Production Requirements

**Do not use the placeholder secret in `kustomize/base/secret.yaml` for production.** It contains example values and is intended for local development and demos only.

### Production-Safe Options

| Approach | Use Case | Implementation |
|----------|----------|----------------|
| **External Secrets Operator** | Production, cloud vaults | See `deploy/external-secrets/` |
| **Sealed Secrets** | GitOps with encrypted secrets | `kubeseal` to encrypt, ArgoCD syncs |
| **Manual secret creation** | Small teams, non-GitOps | `kubectl create secret` before apply |

### Required Secrets

| Key | Description | Example |
|-----|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing key (32+ bytes hex) | `openssl rand -hex 32` |

### Local / Dev Only

For local development or demos, you may use the placeholder in `base/secret.yaml`:

```bash
# Dev overlay applies the placeholder secret from base
kubectl apply -k deploy/kustomize/overlays/dev
```

**Never commit real credentials.** The placeholder values are safe for local PostgreSQL only.
