# External Secrets — Production Secret Injection

Use External Secrets Operator to inject secrets from Vault, AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager. **No plaintext secrets in Git.**

## Prerequisites

- [External Secrets Operator](https://external-secrets.io/) installed in cluster
- SecretStore or ClusterSecretStore configured for your vault

## Setup

1. Create a SecretStore (example for Vault):

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-store
  namespace: taskforge-prod
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "taskforge-backend"
          serviceAccountRef:
            name: default
            namespace: taskforge-prod
```

2. Store secrets in your vault at the path referenced in `external-secret.yaml`.

3. Apply the ExternalSecret (replace paths in the example first):

```bash
kubectl apply -f external-secret.yaml -n taskforge-prod
```

4. Exclude the base placeholder secret from prod. Either:
   - Remove `secret.yaml` from base and add ExternalSecret to prod overlay, or
   - Use a prod-specific kustomization that excludes the base secret and includes this ExternalSecret

## Vault Path Example

For HashiCorp Vault:

```bash
vault kv put secret/taskforge/database \
  url="postgresql://user:pass@host:5432/db" \
  secret_key="$(openssl rand -hex 32)"
```

Adjust `remoteRef.key` and `property` in `external-secret.yaml` to match your vault structure.
