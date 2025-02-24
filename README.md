# CxReportClientV1 Usage Example

 `cxreports-api-client` is a Python library that provides a simple and intuitive interface for interacting with the CxReports application’s API. This library allows you to perform various operations on CxReports, such as retrieving reports, sending data, and generating PDFs.

## Usage
```python
from cx_report_client import CxReportClientV1

# Initialize the client
client = CxReportClientV1(URL, DEFAULT_WORKSPACE, TOKEN)

types = client.get_report_types()
print(types)

types_from_another_ws = client.get_report_types(26)
print(types_from_another_ws)

workspaces = client.get_workspaces()
print(workspaces)

reports = client.get_reports("other")
print(reports)

reports_from_another_ws = client.get_reports("showcase", 26)
print(reports_from_another_ws)

token = client.create_auth_token()
print(token)

temp_data = client.push_temporary_data({"title": {'value': '123 123 123 123'}})
print(temp_data)

# get tempDataId from temp_data
temp_data_id = temp_data['tempDataId']

# Generate a PDF report
pdf = client.get_pdf(160)
with open("./test1.pdf", 'wb') as pdf_file: pdf_file.write(pdf)

# Generate a PDF report with parameters (e.g., title)
pdf = client.get_pdf(160, {"tempDataId":temp_data_id,"params": {"title": "First page title"}})
with open("./test2.pdf", 'wb') as pdf_file: pdf_file.write(pdf)

# Generate a PDF report from another WS
pdf = client.get_pdf(149, None, 26)
with open("./signature.pdf", 'wb') as pdf_file: pdf_file.write(pdf)