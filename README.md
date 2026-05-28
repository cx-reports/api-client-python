# cxreports-api-client

Official Python client for the [CxReports](https://cx-reports.com) reporting platform. Generate PDFs, push report data, manage templates and themes, schedule jobs — all from Python, with a small, idiomatic surface.

The client wraps the CxReports v1 REST API. It handles authentication, URL construction, query-string encoding, and async polling so you can focus on report content.

## Features

- **Synchronous PDF generation** via `GET` (parameters in the URL) or `POST` (parameters in the body)
- **Asynchronous export** for large or slow reports — start, poll, download
- **Temporary data** — push a JSON payload once, reference it by ID across multiple report runs
- **Themes & templates** — list and override per request
- **Jobs** — list, start runs, poll status, generate review documents, deliver entries
- **Iframe-friendly preview URLs** with single-use nonce tokens
- **Multi-workspace** — every method accepts an optional `workspace_id` to target a specific workspace without re-instantiating the client

## Installation

```bash
pip install cxreports-api-client
```

Requires Python 3.7+ and `requests`.

## Quick start

```python
from cxreports_api_client import CxReportClientV1

client = CxReportClientV1(
    base_url="https://your-tenant.cx-reports.app",
    default_workspace_id=1,
    token="<your-personal-access-token>",
)

pdf = client.get_pdf(report_id=160)
with open("report.pdf", "wb") as f:
    f.write(pdf)
```

### Authentication

The client uses Bearer-token authentication. Generate a Personal Access Token from the CxReports UI under **Account → API tokens** and pass it as the `token` constructor argument. Tokens are sent in the `Authorization: Bearer <token>` header on every request.

### Targeting workspaces

The `default_workspace_id` passed to the constructor is used unless you override it per call:

```python
themes_in_default_ws = client.get_themes()
themes_in_other_ws   = client.get_themes(workspace_id=26)
```

This pattern applies to every method that operates inside a workspace.

## Workspaces, report types, themes, templates

```python
workspaces   = client.get_workspaces()       # all workspaces you have access to
report_types = client.get_report_types()     # report types in the default workspace
themes       = client.get_themes()           # themes available for rendering
templates    = client.get_templates()        # report templates available
```

## Reports

```python
# All reports in the workspace
reports = client.get_reports()

# Filtered by report type code
reports = client.get_reports(type="other")

# Page metadata (useful for excludePages-style operations later on)
pages = client.get_report_pages(report_id=160)
```

## Generating PDFs

### `GET` — small parameter sets

Use when your parameters fit comfortably in a URL.

```python
# Basic
pdf = client.get_pdf(report_id=160)

# With a parameters dict
pdf = client.get_pdf(160, {
    "tempDataId": temp_data_id,
    "params": {"title": "First page title"},
    "timezone": "UTC",
})

# Override theme or template (by id or code)
pdf = client.get_pdf(160, theme="3", template="Default")
```

### `POST` — large payloads

Use when the report consumes a JSON `data` object that's too large for a query string, or when you prefer not to put data in URLs.

```python
pdf = client.post_pdf(160, {
    "data": {
        "invoiceNumber": "12345",
        "items": [{"description": "Widget", "quantity": 10}],
    },
    "params": {"title": "Q1 invoice"},
    "timezone": "UTC",
    "format": "pdf",
    "theme": "3",
    "template": "2",
})
```

### Asynchronous export

For reports that take more than a few seconds to render. Start the export, poll until it's ready, then download the bytes.

```python
import time

export = client.start_report_export(160, {
    "data": {"title": "Quarterly portfolio report"},
    "format": "pdf",
    "timezone": "UTC",
    "includeAttachments": False,
})
temp_file_id = export["temporaryFileId"]

while True:
    status = client.get_export_status(temp_file_id)
    if status.get("isReady"):
        break
    if status.get("status") == "Failed":
        raise RuntimeError(status.get("errorMessage"))
    time.sleep(2)

content = client.get_export_content(temp_file_id)
with open("report.pdf", "wb") as f:
    f.write(content)
```

## Temporary data

Upload a JSON payload once; reference it from any number of subsequent report requests via `tempDataId`. Useful for large datasets you don't want to re-send on every render.

```python
temp = client.push_temporary_data({
    "invoice": {"invoiceNumber": "12345", "items": [...]},
})
temp_data_id = temp["tempDataId"]

pdf = client.get_pdf(160, {"tempDataId": temp_data_id})
```

## Preview URLs (iframe embedding)

Returns a nonce-signed URL suitable for embedding in an `<iframe>` — the nonce is single-use and converts to a session cookie on first navigation, so the API token never leaves the server.

```python
url = client.get_preview_url(160)
url_with_data = client.get_preview_url(160, {"tempDataId": temp_data_id})
```

## Auth tokens

If you need a raw nonce token for a custom auth flow:

```python
token = client.create_auth_token()   # {'nonce': '...'}
```

## Jobs

Jobs are pre-configured, repeatable report-generation tasks defined in the CxReports UI. They support optional review steps before delivery.

```python
jobs = client.get_jobs()

# Start a new run
run = client.start_job_run(job_id=42, request_body={"params": {}, "data": {}})
run_id = run["jobRunId"]

# Poll until the run finishes
while True:
    status = client.get_job_run_status(job_id=42, run_id=run_id)
    if status.get("finished"):
        break
    time.sleep(3)

# If the job requires review, generate a consolidated review document.
# The returned temporaryFileId can be polled via get_export_status / downloaded via get_export_content.
review = client.get_run_review_document(job_id=42, run_id=run_id)

# After approval, deliver all entries.
client.deliver_job_run_entries(job_id=42, run_id=run_id)
```

## Naming conventions

Python identifiers use snake_case per [PEP 8](https://peps.python.org/pep-0008/) — `report_id`, `workspace_id`, `temp_data_id`. JSON body and query-parameter keys are forwarded as-is, in the camelCase form the server expects (`tempDataId`, `includeAttachments`, `excludePages`). This matches the public CxReports API documentation, so payloads can be copied between the docs and your Python code without translation.

## Error handling

All HTTP errors are wrapped in `RuntimeError` with a descriptive message:

```python
try:
    pdf = client.get_pdf(999999)
except RuntimeError as e:
    # e.g. "HTTP error occurred: 404 Not Found ..."
    print(e)
```

Authentication failures (HTTP `401` / `403`) surface as `RuntimeError("Unauthenticated.")` so they can be caught distinctly from other HTTP errors if needed.

## TLS verification

TLS certificate validation is **on by default** in this version. If you need to talk to a CxReports instance with a self-signed certificate, configure your environment's trust store rather than disabling verification.

## Links

- [CxReports homepage](https://cx-reports.com)
- [API reference (Swagger)](https://master.cx-reports.app/swagger)
- [Source code](https://github.com/cx-reports/api-client-python)
- [Issue tracker](https://github.com/cx-reports/api-client-python/issues)

## License

MIT
