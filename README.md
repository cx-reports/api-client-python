# CxReportClientV1 Usage Example

 `cx-reports-api` is a Python library that provides a simple and intuitive interface for interacting with the cxReports application’s API. This library allows you to perform various operations on cxReports, such as retrieving reports, sending data, and generating PDFs.

## Usage
```python
from cx_report_client import CxReportClientV1

# Initialize the client
client = CxReportClientV1(URL, WORKSPACE, TOKEN)

# Get report types
types = client.get_report_types()

# Get workspaces
workspaces = client.get_workspaces()

# Get reports for a specific type
reports = client.get_reports("other")

# Create an authentication token
token = client.create_auth_token()

# Push temporary data
temp_data = client.push_temporary_data({"title": {'value': '123 123 123 123'}})

# Extract the temporary data ID
temp_data_id = temp_data['tempDataId']

# Generate a PDF report
pdf = client.get_pdf(160)
with open("./test.pdf", 'wb') as pdf_file: pdf_file.write(pdf)

# Generate a PDF report with parameters (e.g., title)
pdf = client.get_pdf(160, {"tempDataId":temp_data_id,"params": {"title": "First page title"}})
with open("./test.pdf", 'wb') as pdf_file: pdf_file.write(pdf)
```