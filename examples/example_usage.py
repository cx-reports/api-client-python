"""
Example usage of CxReportClientV1

Configure the .env file in the project root with your credentials:
- CX_REPORT_URL: Base URL of the CxReports server
- CX_REPORT_TOKEN: Authentication token
- CX_REPORT_WORKSPACE: Workspace ID
- CX_REPORT_ID: Report ID to generate PDF
"""

import os
import time
import json
from dotenv import load_dotenv  # pip install python-dotenv

from cxreports_api_client.v1.client import CxReportClientV1

load_dotenv()

# Configuration from .env
def get_env_var(name: str, cast_type=None, required=True):
    value = os.getenv(name)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    if cast_type and value is not None:
        try:
            value = cast_type(value)
        except Exception:
            raise ValueError(f"Environment variable {name} must be of type {cast_type.__name__}")
    return value

# Configuration from .env
URL = get_env_var("CX_REPORT_URL")
TOKEN = get_env_var("CX_REPORT_TOKEN")
WORKSPACE = get_env_var("CX_REPORT_WORKSPACE", cast_type=int)
REPORT_ID = get_env_var("CX_REPORT_ID", cast_type=int)

def main():
    """Run example usage of CxReportClientV1"""
    
    # Initialize the client
    print(f"Connecting to {URL} with workspace {WORKSPACE}...")
    client = CxReportClientV1(URL, WORKSPACE, TOKEN)
    
    # ========== WORKSPACES ==========
    print("\n=== WORKSPACES ===")
    try:
        workspaces = client.get_workspaces()
        print(json.dumps(workspaces, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== REPORT TYPES ==========
    print("\n=== REPORT TYPES ===")
    try:
        report_types = client.get_report_types()
        print(json.dumps(report_types, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== REPORTS ==========
    print("\n=== REPORTS ===")
    try:
        reports = client.get_reports(type="all")
        print(json.dumps(reports, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== REPORT PAGES ==========
    print(f"\n=== REPORT PAGES (Report ID: {REPORT_ID}) ===")
    try:
        pages = client.get_report_pages(REPORT_ID)
        print(json.dumps(pages, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== TEMPORARY DATA ==========
    print("\n=== PUSHING TEMPORARY DATA ===")
    temp_data_id = None
    try:
        invoice_data = {
            "invoice": {
                "invoiceNumber": "12345",
                "dateIssued": "2024-01-27",
                "dueDate": "2024-02-10",
                "issuer": {
                    "name": "Test Corporation",
                    "address": "123 Business Rd, Business City, BC 12345",
                    "phone": "123-456-7890",
                    "email": "contact@xyzcorporation.com"
                },
                "recipient": {
                    "name": "TEST Enterprises",
                    "address": "456 Enterprise Blvd, Commerce City, CC 67890",
                    "phone": "987-654-3210",
                    "email": "info@abcenterprises.com"
                },
                "items": [
                    {
                        "description": "Product 1",
                        "quantity": 10,
                        "unitPrice": 29.99,
                        "total": 299.90
                    },
                    {
                        "description": "Product 2",
                        "quantity": 5,
                        "unitPrice": 49.99,
                        "total": 249.95
                    }
                ],
                "subTotal": 549.85,
                "taxRate": 0.07,
                "taxAmount": 38.49,
                "total": 588.34,
                "notes": "Thank you for your business. Passing data works!"
            }
        }
        temp_data = client.push_temporary_data(invoice_data)
        temp_data_id = temp_data.get('tempDataId')
        print(f"Temporary Data ID: {temp_data_id}")
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== GET PDF (Simple) ==========
    print(f"\n=== DOWNLOADING PDF (Simple) - Report ID: {REPORT_ID} ===")
    try:
        pdf = client.get_pdf(REPORT_ID)
        with open("./report1.pdf", 'wb') as pdf_file:
            pdf_file.write(pdf)
        print(f"Saved to report1.pdf (size: {len(pdf)} bytes)")
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== GET PDF (With Temp Data) ==========
    if temp_data_id:
        print(f"\n=== DOWNLOADING PDF (With Temp Data) ===")
        try:
            pdf = client.get_pdf(REPORT_ID, {
                "tempDataId": temp_data_id,
                "timezone": "UTC"
            })
            with open("./report2.pdf", 'wb') as pdf_file:
                pdf_file.write(pdf)
            print(f"Saved to report2.pdf (size: {len(pdf)} bytes)")
        except Exception as e:
            print(f"Error: {e}")
    
    # ========== POST PDF ==========
    print(f"\n=== DOWNLOADING PDF (POST with Data) ===")
    try:
        request_body = {
            "data": invoice_data,
            "timezone": "UTC",
            "format": "pdf"
        }
        pdf = client.post_pdf(REPORT_ID, request_body)
        with open("./report3.pdf", 'wb') as pdf_file:
            pdf_file.write(pdf)
        print(f"Saved to report3.pdf (size: {len(pdf)} bytes)")
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== PREVIEW URL ==========
    print("\n=== PREVIEW URL ===")
    try:
        preview_url = client.get_preview_url(REPORT_ID, {
            "tempDataId": temp_data_id
        } if temp_data_id else None)
        print(f"Preview URL: {preview_url}")
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== ASYNC EXPORT ==========
    print(f"\n=== ASYNC EXPORT ===")
    try:
        export_request = {
            "data": invoice_data,
            "format": "pdf",
            "timezone": "UTC",
            "includeAttachments": False
        }
        export_response = client.start_report_export(REPORT_ID, export_request)
        temp_file_id = export_response['temporaryFileId']
        print(f"Export started. Temporary File ID: {temp_file_id}")
        
        # ========== POLLING EXPORT STATUS ==========
        print("\n=== POLLING EXPORT STATUS ===")
        max_attempts = 30
        attempt = 0
        export_ready = False
        
        while not export_ready and attempt < max_attempts:
            time.sleep(2)  # Wait 2 seconds between polls
            
            status = client.get_export_status(temp_file_id)
            attempt += 1
            print(f"Attempt {attempt}: Status={status.get('status')}, IsReady={status.get('isReady')}")
            
            if status.get('isReady'):
                export_ready = True
                print(f"File ready! Name: {status.get('name')}, Size: {status.get('contentSize')} bytes")
            elif status.get('status') == 'Failed':
                print(f"Export failed: {status.get('errorMessage')}")
                break
        
        # ========== DOWNLOADING EXPORTED FILE ==========
        if export_ready:
            print("\n=== DOWNLOADING EXPORTED FILE ===")
            content = client.get_export_content(temp_file_id)
            with open("./report_async.pdf", 'wb') as f:
                f.write(content)
            print(f"Saved to report_async.pdf (size: {len(content)} bytes)")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== NONCE TOKEN ==========
    print("\n=== NONCE TOKEN ===")
    try:
        nonce = client.create_auth_token()
        print(f"Nonce Token: {nonce.get('nonce')}")
        print("(This can be used for iframe authentication)")
    except Exception as e:
        print(f"Error: {e}")
    
    # ========== JOBS ==========
    print("\n=== JOBS ===")
    try:
        jobs = client.get_jobs()
        print(json.dumps(jobs, indent=2))
        
        if jobs and len(jobs) > 0:
            job = jobs[0]
            job_id = job.get('id')
            print(f"\n=== STARTING JOB RUN: {job.get('name')} (ID: {job_id}) ===")
            
            # ========== START JOB RUN ==========
            try:
                job_run_request = {
                    "params": {},
                    "data": {}
                }
                job_run = client.start_job_run(job_id, job_run_request)
                job_run_id = job_run.get('jobRunId')
                print(f"Job run started. Run ID: {job_run_id}")
                
                # ========== POLLING JOB RUN STATUS ==========
                print("\n=== POLLING JOB RUN STATUS ===")
                job_finished = False
                job_attempt = 0
                max_job_attempts = 30
                
                while not job_finished and job_attempt < max_job_attempts:
                    time.sleep(3)  # Wait 3 seconds between polls
                    
                    job_status = client.get_job_run_status(job_id, job_run_id)
                    job_attempt += 1
                    
                    status_info = job_status.get('status', {})
                    print(f"Attempt {job_attempt}: Finished={job_status.get('finished')}, "
                          f"Entries={job_status.get('entries')}, "
                          f"Queued={status_info.get('queued')}, "
                          f"Review={status_info.get('review')}, "
                          f"Completed={status_info.get('completed')}, "
                          f"Errors={status_info.get('errors')}")
                    
                    if job_status.get('finished'):
                        job_finished = True
                        
                        # ========== GENERATE REVIEW DOCUMENT ==========
                        if job.get('reviewRequired') and status_info.get('review', 0) > 0:
                            print("\n=== GENERATING REVIEW DOCUMENT ===")
                            try:
                                review_doc = client.get_run_review_document(job_id, job_run_id)
                                print(f"Review document temporary file ID: {review_doc.get('temporaryFileId')}")
                                
                                # ========== DELIVER JOB RUN ==========
                                print("\n=== DELIVERING JOB RUN (after review) ===")
                                deliver_response = client.deliver_job_run_entries(job_id, job_run_id)
                                print(f"Job delivered successfully")
                            except Exception as e:
                                print(f"Error in review/deliver: {e}")
                        else:
                            print("\nNo review required or no items in review status.")
                
                if not job_finished:
                    print(f"Job run did not finish within {max_job_attempts} attempts")
                    
            except Exception as e:
                print(f"Error running job: {e}")
        else:
            print("No jobs available to run")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== DONE ===")
    print("All examples completed!")


if __name__ == '__main__':
    main()