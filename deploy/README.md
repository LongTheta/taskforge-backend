# TaskForge Backend — GitOps Deployment

This directory contains GitOps-ready manifests and documentation for deploying TaskForge Backend.

**Validated by six security and compliance evaluations** — see [`SKILL_EVALUATIONS.md`](../SKILL_EVALUATIONS.md). This deployment has **passed** Zero Trust GitOps Enforcement and DevSecOps Policy Enforcement, with **low risk** from Security Evaluator and **7.4/10** DoD Zero Trust score (Target ZT achieved). Benefits of these passes:

| Evaluation | Outcome | What it means for deployment |
|------------|---------|-----------------------------|
| **Zero Trust GitOps** | PASS | No High violations; prod uses External Secrets, manual sync, NetworkPolicy, cosign |
| **DevSecOps Policy** | PASS | No plaintext secrets, SBOM, pinned deps, artifact traceability, manual promotion gate |
| **Security Evaluator** | Low risk | MFA, ESO, NetworkPolicy, image signing in place |
| **DoD Zero Trust** | 7.4/10 | Target ZT baseline met across User, Application, Network, Automation, Visibility |

You get production-ready controls out of the box: External Secrets in prod (no secrets in Git), NetworkPolicy micro-segmentation, cosign image signing, and manual sync for production.

## Kustomize Structure

```
deploy/
├── kustomize/
│   ├── base/           # Deployment, Service, ConfigMap, NetworkPolicy (no secret)
│   └── overlays/
│       ├── dev/        # secret.yaml (placeholder), patch.yaml
│       └── prod/       # external-secret.yaml, network-policy-patch.yaml, patch.yaml
├── argocd/
│   ├── application.yaml      # Dev (automated sync)
│   └── application-prod.yaml # Prod (manual sync)
├── external-secrets/         # ESO example + README
├── SECRETS.md                # Secrets management guidance
├── GITOPS.md                 # Dev vs prod sync strategy
└── README.md
```

**Apply:**
```bash
# Dev (uses overlay secret.yaml — local/demo only)
kubectl apply -k deploy/kustomize/overlays/dev

# Prod (uses ExternalSecret; requires ESO + SecretStore)
kubectl apply -k deploy/kustomize/overlays/prod
```

**Production secrets:** Base has no secret. Dev overlay includes a placeholder; prod overlay uses `external-secret.yaml` (External Secrets Operator). Configure ESO SecretStore (e.g. `vault-store`) before prod apply. See `deploy/SECRETS.md` and `deploy/external-secrets/README.md`.

## ArgoCD Workflow

1. **Build:** CI builds image, tags with commit SHA (e.g. `taskforge-backend:abc1234`)
2. **Publish:** Push to ghcr.io; **cosign keyless signing** in `push-and-sign` job (main branch)
3. **Update overlay:** Set `images[].newTag` in overlay `kustomization.yaml` to the new SHA
4. **Sync:** Dev auto-syncs; prod requires manual sync. See `deploy/GITOPS.md`.

**Applications:** `argocd/application.yaml` (dev, automated) and `argocd/application-prod.yaml` (prod, manual).

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

| Overlay | Namespace      | Replicas | LOG_LEVEL | Secrets        | NetworkPolicy      |
|---------|----------------|----------|-----------|----------------|--------------------|
| dev     | taskforge-dev  | 1        | DEBUG     | overlay placeholder | base (port 8000) |
| prod    | taskforge-prod | 2        | INFO      | ExternalSecret | base + ingress restriction |

**NetworkPolicy (prod):** Patch restricts ingress to `ingress-nginx` namespace. Adjust `matchLabels` in `overlays/prod/network-policy-patch.yaml` if your ingress controller differs (e.g. `app.kubernetes.io/name: ingress-nginx` for Helm nginx-ingress).

## Security / Compliance Notes

See `SKILL_EVALUATIONS.md` for full assessments. Key deployment actions:

| Area | Action |
|------|--------|
| **ESO** | Configure SecretStore (e.g. `vault-store`) before prod; update `external-secret.yaml` remoteRef paths |
| **NetworkPolicy** | Adjust prod patch `matchLabels` for your ingress controller |
| **DB encryption** | Validate encryption at rest in prod PostgreSQL (RDS, Cloud SQL, etc.) |
| **TLS** | Document TLS termination at ingress/load balancer |
| **Image signing** | CI signs with cosign (keyless); verify in admission if required |

## Future

- Helm chart (if complexity grows)
- ArgoCD Image Updater integration
- Promotion workflow automation
