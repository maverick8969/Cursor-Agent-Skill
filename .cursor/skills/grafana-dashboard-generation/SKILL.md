---
name: grafana-dashboard-generation
description: Generate production Grafana dashboards and integrate database datasources with efficient queries, variables, alerts, and dashboard-as-code workflows. Use when users request Grafana dashboards, SQL-backed panels, or datasource provisioning.
---

# Grafana Dashboard Generation

Build Grafana dashboards that are useful in operations, efficient on datasource load, and maintainable in version control.

## When to Use

- User asks for new Grafana dashboards
- User needs SQL datasource integration (PostgreSQL/MySQL/MSSQL)
- User wants dashboard JSON, Terraform provisioning, or API import payloads
- User requests alert panels tied to application/database health

## Workflow

1. Define dashboard goals and target audience
2. Confirm datasource, schema, and key metrics
3. Draft panel/query map with variable strategy
4. Generate dashboard JSON and alert definitions
5. Validate query efficiency and dashboard readability
6. Provide provisioning instructions and handoff notes

## Required Inputs

- Primary use case (incident response, capacity, product KPI, etc.)
- Datasource type and connection name
- Database tables/views and time column
- Filter dimensions (service, region, env, tenant)
- SLO/SLA thresholds for warning and critical states
- Desired refresh interval and default time range

If inputs are missing, ask for the smallest set required to produce a safe first version.

## Panel Design Rules

- Put high-level health indicators in the top row (`stat` or concise `timeseries`)
- Keep each panel answerable ("What decision does this panel enable?")
- Use consistent units, labels, and legends across panels
- Use variables for environment/service/region filters
- Avoid over-dense dashboards; split into multiple dashboards if needed

## SQL Query Rules

- Always include explicit time filtering via Grafana macros
- Prefer bounded queries and avoid unbounded full-table scans
- Group and aggregate for visualization needs, not raw dumps
- Add limits/order for table panels
- Highlight indexing needs for repeated dashboard queries

Example time-filtered query pattern:

```sql
SELECT
  $__timeGroupAlias(created_at, '5m'),
  service_name,
  COUNT(*) AS request_count
FROM requests
WHERE $__timeFilter(created_at)
  AND service_name IN (${service:sqlstring})
GROUP BY 1, 2
ORDER BY 1;
```

## Datasource Integration Checklist

- Use read-only credentials
- Store secrets in env/secret manager, not dashboard JSON
- Validate timezone handling and timestamp datatype
- Test variable queries independently
- Confirm dashboard load time at default range

## Output Format

Provide results in this order:

1. **Dashboard intent** (1-3 bullets)
2. **Datasource config assumptions** (name/type/access)
3. **Panel plan** (panel title + query purpose)
4. **Dashboard JSON** (or Terraform resource using `config_json`)
5. **Alert thresholds** (warn/critical + rationale)
6. **Validation notes** (query cost risks, next optimizations)

## Provisioning Patterns

Terraform:

```hcl
resource "grafana_dashboard" "db_observability" {
  config_json = file("${path.module}/dashboards/db-observability.json")
}
```

File provisioning:

```yaml
apiVersion: 1
providers:
  - name: default
    type: file
    options:
      path: /etc/grafana/dashboards
```

## Guardrails

- Do not suggest write-capable datasource accounts for dashboards
- Do not use queries without time filters unless explicitly justified
- Do not produce massive all-in-one dashboards when domain split is clearer
- Prefer actionable alerts over noisy metric-only alerts
