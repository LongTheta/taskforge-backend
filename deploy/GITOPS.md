# GitOps Sync Strategy

## Dev vs Prod

| Environment | Sync | ArgoCD Application |
|-------------|------|---------------------|
| **Dev** | Automated (prune, selfHeal) | `argocd/application.yaml` |
| **Prod** | Manual | `argocd/application-prod.yaml` |

## Rationale

- **Dev:** Fast iteration; automated sync is acceptable. Changes flow from Git after CI passes.
- **Prod:** Manual sync adds explicit approval. Combined with CI promotion gate (GitHub `production` environment), production deployment requires:
  1. CI pass (lint, test, security, SBOM, Docker)
  2. Promotion gate approval (GitHub environment reviewers)
  3. Overlay update (image tag in prod kustomization)
  4. ArgoCD manual sync

## Production Workflow

1. Merge to `main` → CI runs
2. Promote job waits for `production` environment approval
3. After approval, update `deploy/kustomize/overlays/prod/kustomization.yaml` with new image tag
4. Commit and push
5. ArgoCD detects diff; app shows "OutOfSync"
6. Operator runs `argocd app sync taskforge-backend-prod` (or via UI)

## Sync Waves (Optional)

For advanced control, use sync waves to order resource creation (e.g. secrets before deployment). Example:

```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

Apply to secrets; deployment uses wave "0" (default).
