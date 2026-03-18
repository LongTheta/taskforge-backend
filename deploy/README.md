# TaskForge Backend — GitOps Deployment

This directory documents how TaskForge Backend fits into a GitOps deployment model.

## Deployment Metadata

The app supports environment-driven metadata via env vars:

| Variable    | Description              | Example        |
|-------------|--------------------------|----------------|
| `APP_ENV`   | Environment mode         | `production`   |
| `GIT_SHA`   | Git commit SHA (CI)      | `abc1234`      |
| `IMAGE_TAG` | Container image tag (CI)  | `0.1.0` or `abc1234` |

Version comes from the package; `GIT_SHA` and `IMAGE_TAG` are optional env overrides. All are exposed in `/health` (non-sensitive only).

## Immutable Builds

- **Image tags:** Use version or commit SHA, not `latest`:
  - `taskforge-backend:0.1.0`
  - `taskforge-backend:abc1234`
- **Config:** Environment-specific config via env vars; no baked-in secrets.

## Config Separation

| Environment | Config Source        | Typical Use |
|-------------|----------------------|-------------|
| **local**   | `.env`               | Development |
| **dev**     | Env vars / ConfigMap | Dev cluster |
| **stage**   | Env vars / ConfigMap | Staging     |
| **prod**    | Env vars / Secret    | Production  |

## CI/CD Supply Chain

- **Actions:** Pinned by full 40-char SHA.
- **SBOM:** CycloneDX JSON generated in CI; artifact `sbom`.
- **Build metadata:** `build-metadata` artifact with `git_sha`, `image_tag`, `version`.
- **Promotion gate:** `promote` job uses `production` environment; configure required reviewers in Settings → Environments.

## Future GitOps

- **Helm:** Chart could wrap app, env vars, and probes.
- **Kustomize:** Base + overlays per environment.
- **ArgoCD:** Application manifests pointing at Git repo.
- **Promotion:** Promote same image tag through dev → stage → prod.

## Docker Build

```bash
docker build --target prod -t taskforge-backend:0.1.0 .
```

Set `GIT_SHA` and `IMAGE_TAG` as runtime env vars for deployment traceability.
