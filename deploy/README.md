# TaskForge Backend — GitOps Deployment

This directory contains GitOps-ready manifests and documentation for deploying TaskForge Backend.

## Kustomize Structure

```
deploy/
├── kustomize/
│   ├── base/           # Deployment, Service, ConfigMap, Secret
│   └── overlays/
│       ├── dev/        # taskforge-dev namespace, DEBUG logs
│       └── prod/       # taskforge-prod namespace, 2 replicas
├── argocd/
│   └── application.yaml   # Example ArgoCD Application
├── examples/
│   └── argocd-application.yaml   # Same example, generic placement
└── README.md
```

**Apply:**
```bash
# Dev
kubectl apply -k deploy/kustomize/overlays/dev

# Prod (update image tag in kustomization.yaml first)
kubectl apply -k deploy/kustomize/overlays/prod
```

**Prerequisites:** Create the secret before applying:
```bash
kubectl create secret generic taskforge-backend-secrets \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db' \
  --from-literal=SECRET_KEY="$(openssl rand -hex 32)" \
  -n taskforge-prod
```

## ArgoCD Workflow

1. **Build:** CI builds image, tags with commit SHA (e.g. `taskforge-backend:abc1234`)
2. **Publish:** Push image to registry (ghcr.io, ECR, etc.)
3. **Update overlay:** Set `images[].newTag` in overlay `kustomization.yaml` to the new SHA
4. **Sync:** ArgoCD detects the change and syncs the Application

**Example Application:** `deploy/argocd/application.yaml` or `deploy/examples/argocd-application.yaml` points at `deploy/kustomize/overlays/dev`. Adjust `repoURL`, `path`, and `targetRevision` for your setup.

**Image update options:**
- Manual: Update overlay, commit, push
- ArgoCD Image Updater: Automate image tag updates
- CI step: After promote, update overlay and push (GitOps push model)

## Deployment Metadata

| Variable    | Description              | Example        |
|-------------|--------------------------|----------------|
| `APP_ENV`   | Environment mode         | `production`   |
| `APP_VERSION`| Version override (optional) | `0.1.0`    |
| `GIT_SHA`   | Git commit SHA (CI)      | `abc1234`      |
| `IMAGE_TAG` | Container image tag (CI) | `abc1234`      |

Set via ConfigMap or env. Exposed in `/health` and `/info`.

## Immutable Builds

- **Image tags:** Use commit SHA, not `latest`
- **Config:** Env vars; no baked-in secrets
- **Promotion:** Same image tag through dev → stage → prod

## Environment Separation

| Overlay | Namespace      | Replicas | LOG_LEVEL |
|---------|----------------|----------|-----------|
| dev     | taskforge-dev  | 1        | DEBUG     |
| prod    | taskforge-prod | 2        | INFO      |

## Future

- Helm chart (if complexity grows)
- ArgoCD Image Updater integration
- Promotion workflow automation
