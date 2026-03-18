# TaskForge Observability

Starter assets for Prometheus, Grafana, and Loki integration.

## Metrics (Prometheus)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, path, status | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, path | Request duration |
| `http_requests_in_progress` | Gauge | method, path | In-flight requests |
| `taskforge_build_info` | Gauge | version, env, git_sha | Build metadata (value 1) |

**Scrape:** `/metrics` on port 8000. See `prometheus-scrape.example.yml` for config.

## Grafana Dashboard

**Import:** `observability/grafana/taskforge-overview.json`

1. Grafana → Dashboards → Import → Upload JSON
2. Select Prometheus datasource
3. Panels: request rate, latency (p50/p99), error rate, in-progress requests, build info

**Variables:** `datasource` — set to your Prometheus datasource UID.

**Job label:** Panels assume `job="taskforge-backend"`. Ensure your scrape config sets this label.

## Loki / Log Labels

See `loki-labeling-guidance.md` for detailed LogQL examples and label recommendations.

Structured JSON logs include fields suitable for Loki:

| Field | Use |
|-------|-----|
| `timestamp` | Time |
| `level` | Filter by level |
| `logger` | Logger name |
| `message` | Log message |
| `request_id` | Trace requests |
| `method`, `path`, `status_code`, `duration_ms` | Request context |
| `service`, `version`, `env` | Deployment context |

**Example LogQL:**
```
{job="taskforge-backend"} | json | level="ERROR"
{job="taskforge-backend"} | json | request_id="abc-123"
{job="taskforge-backend"} | json | env="production" | status_code>=500
```

## Health and Info

- `/health` — Liveness; returns version, env, git_sha, image_tag
- `/info` — Same as health (deployment metadata)
- `/ready` — Readiness (DB connectivity)

## Kubernetes ServiceMonitor (optional)

If using Prometheus Operator:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: taskforge-backend
  namespace: taskforge-prod
spec:
  selector:
    matchLabels:
      app: taskforge-backend
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
```
