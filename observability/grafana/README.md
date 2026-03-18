# TaskForge Grafana Dashboards

## taskforge-overview.json

Starter dashboard for request rate, latency, error rate, in-progress requests, and build info.

**Import:** Grafana → Dashboards → Import → Upload `taskforge-overview.json`

**Panels:**
- Health status — `up{job="taskforge-backend"}` (scrape target up/down)
- Request rate (req/s) — `rate(http_requests_total[5m])`
- Latency (p50, p99) — `histogram_quantile` on `http_request_duration_seconds_bucket`
- Error rate (5xx) — ratio of 5xx to total
- Requests in progress — `http_requests_in_progress`
- Build info — `taskforge_build_info` (version, env, git_sha)

**Requirements:** Prometheus scraping `/metrics` with `job="taskforge-backend"`. See `observability/prometheus-scrape.example.yml`.
