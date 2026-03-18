# Loki Labeling Guidance for TaskForge Backend

Structured JSON logs from TaskForge Backend include fields suitable for Loki ingestion and LogQL queries.

## Log Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO timestamp |
| `level` | string | INFO, WARNING, ERROR, DEBUG |
| `logger` | string | Python logger name |
| `message` | string | Log message |
| `request_id` | string | X-Request-ID; trace requests across logs |
| `method` | string | HTTP method (GET, POST, etc.) |
| `path` | string | Request path |
| `status_code` | number | HTTP status |
| `duration_ms` | number | Request duration in ms |
| `service` | string | Always `taskforge-backend` |
| `version` | string | App version |
| `env` | string | development, production, test |
| `exception` | string | Stack trace (errors only) |

## Recommended Loki Labels

Keep label cardinality low. Use:

- `job` — e.g. `taskforge-backend`
- `env` — from log field `env` (if extracted)
- `level` — from log field `level` (if needed for filtering)

Avoid using high-cardinality fields (`request_id`, `path`) as labels. Query them with LogQL instead.

## Example LogQL Queries

```
# Errors only
{job="taskforge-backend"} | json | level="ERROR"

# Trace a request by ID
{job="taskforge-backend"} | json | request_id="abc-123"

# 5xx in production
{job="taskforge-backend"} | json | env="production" | status_code>=500

# Slow requests (>1s)
{job="taskforge-backend"} | json | duration_ms>1000

# Auth-related logs
{job="taskforge-backend"} | json | path=~".*auth.*"
```

## Promtail / Agent Config

If using Promtail or Grafana Agent, ensure the scrape config sets `job="taskforge-backend"` so LogQL queries match. Parse JSON with `| json` in queries or configure pipeline stages to extract fields.
