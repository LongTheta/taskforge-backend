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

## Metrics → Dashboard Panels

| Metric | Dashboard panel |
|--------|-----------------|
| `up{job="taskforge-backend"}` | Health status (scrape target up/down) |
| `rate(http_requests_total[5m])` | Request rate (req/s) |
| `http_request_duration_seconds_bucket` | Latency (p50, p99) |
| `http_requests_total` (5xx / total) | Error rate |
| `http_requests_in_progress` | Requests in progress |
| `taskforge_build_info` | Build info (version, env, git_sha) |

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

## Audit Logs → Loki / SIEM

Audit events have `event_type: "audit"`. Route these to Loki or SIEM for security monitoring.

| Audit Field | Purpose |
|-------------|---------|
| `event_type` | Always `audit` — filter for security events |
| `action` | e.g. `login_success`, `login_failure`, `task_created` |
| `user_id` | Actor (when authenticated) |
| `resource_type`, `resource_id` | Affected resource |
| `request_id` | Correlate with request logs |
| `success` | Boolean outcome |

**LogQL for audit events:**
```
{job="taskforge-backend"} | json | event_type="audit"
{job="taskforge-backend"} | json | event_type="audit" | action="login_failure"
{job="taskforge-backend"} | json | event_type="audit" | success=false
```

**SIEM integration:** Configure Promtail/Grafana Agent to send logs to Loki. Use `event_type=audit` as a label or filter. For Splunk/Elastic, parse JSON and index `event_type`, `action`, `user_id`.

## Alerting

See `prometheus-alerts.example.yml` for example alert rules:

- **TaskForgeDown** — Service unreachable
- **TaskForgeHighErrorRate** — 5xx rate > 5%
- **TaskForgeHighLatency** — p99 > 2s

Add to Prometheus `rule_files` or Prometheus Operator Rule.

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
