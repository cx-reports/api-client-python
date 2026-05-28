import requests
import base64
import urllib.parse
import json
import warnings
from functools import wraps
from typing import Dict, Any


class CxReportClientV1:
    """
    A client for interacting with the CxReport API.

    This class provides methods for fetching reports, pushing temporary data, and managing authentication tokens.

    Attributes:
        base_url (str): The base URL for the API.
        workspace_id (int): The workspace ID for the API context.
        token (str): The authentication token used for API requests.
    """
    def __init__(self, base_url:str, default_workspace_id:int, token:str):
        self.url = base_url.strip().strip("/")
        self.workspace_id = default_workspace_id
        self.token = token

    def __get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
        }
    
    def __get_url_with_workspace(self, url:str, workspace_id:int = None):
        return f"{self.url}/api/v1/ws/{self.workspace_id if workspace_id == None else workspace_id}/{url}"
    
    def __get_preview_url(self, url:str, workspace_id:int = None):
        return f"{self.url}/ws/{self.workspace_id if workspace_id == None else workspace_id}/{url}"
    
    def __handle_requests_exceptions(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as http_err:
                raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
            except requests.exceptions.ConnectionError as conn_err:
                raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
            except requests.exceptions.Timeout as timeout_err:
                raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
            except requests.exceptions.RequestException as req_err:
                raise RuntimeError(f"An error occurred: {req_err}") from req_err
        return wrapper

    def __check_authentication(self, response):
        """
        Check if the response indicates an authentication failure.

        Args:
            response: The response object from requests.

        Raises:
            RuntimeError: If the response indicates unauthenticated access.
        """
        # Check status code first (401 = Unauthorized, 403 = Forbidden)
        if response.status_code in (401, 403):
            raise RuntimeError("Unauthenticated.")

        # Fallback: Check content type for HTML (backwards compatibility)
        if response.headers.get('Content-Type', '').lower().startswith('text/html'):
            raise RuntimeError("Unauthenticated.")

    @__handle_requests_exceptions
    def get_pdf(self, report_id: int = None, params: dict = None, workspace_id: int = None, theme: str = None, template: str = None, *, reportId: int = None):
        """
        Fetch a PDF report.

        Args:
            report_id (int): The ID of the report.
            params (Optional[Dict[str, Any]]): Optional query parameters.
            workspace_id (int, optional): The workspace ID.
            theme (str, optional): Theme for PDF export/generation.
            template (str, optional): Template for PDF export/generation.
            reportId (int, deprecated): Old name for ``report_id``. Kept for backwards
                compatibility; emits a DeprecationWarning when used.

        Returns:
            bytes: The PDF content.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        if reportId is not None:
            warnings.warn(
                "'reportId' is deprecated; use 'report_id' instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            if report_id is None:
                report_id = reportId
        if report_id is None:
            raise TypeError("get_pdf() missing required argument: 'report_id'")

        if params is None:
            params = {}
        if theme is not None:
            params["theme"] = theme
        if template is not None:
            params["template"] = template

        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"reports/{report_id}/pdf", workspace_id)
        url = self.__append_query_params(url, params)

        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        if "application/pdf" not in response.headers.get("Content-Type", "").lower():
            raise RuntimeError("Invalid content type, expected PDF")

        return response.content

    @__handle_requests_exceptions
    def get_report_types(self, workspace_id:int = None):
        headers = self.__get_headers()
        url = self.__get_url_with_workspace("report-types", workspace_id)

        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()

    @__handle_requests_exceptions
    def get_themes(self, workspace_id: int = None):
        """
        Get the list of themes for the workspace.

        Args:
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.

        Returns:
            List[Dict[str, Any]]: A list of themes, each with code (str), name (str), and id (int).

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace("themes", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()
        return response.json()

    @__handle_requests_exceptions
    def get_templates(self, workspace_id: int = None):
        """
        Get the list of report templates for the workspace.

        Args:
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.

        Returns:
            List[Dict[str, Any]]: A list of report templates, each with code (str), name (str), and id (int).

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace("templates", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()
        return response.json()

    @__handle_requests_exceptions
    def get_workspaces(self):
        """
        Fetch the list of available workspaces.

        Returns:
            List[Dict[str, Any]]: A list of workspaces.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = f"{self.url}/api/v1/workspaces"
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()
            
    @__handle_requests_exceptions
    def get_reports(self, type: str = None, workspace_id:int = None):
        """
        Fetch the list of reports, optionally filtered by report type.

        Args:
            type (str, optional): Filter by given report type. If omitted, all reports are returned.
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.

        Returns:
            List[Dict[str, Any]]: A list of reports.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace("reports", workspace_id)
        if type is not None:
            url = self.__append_query_params(url, {"type": type})
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()

    @__handle_requests_exceptions
    def get_report_pages(self, report_id:int, workspace_id: int = None):
        """
        Get the list of pages for a specific report.

        Args:
            report_id (int): The ID of the report.
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.

        Returns:
            List[Dict[str, Any]]: A list of report pages with their metadata.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"reports/{report_id}/pages", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()
    

    @__handle_requests_exceptions
    def post_pdf(self, report_id: int, request_body: dict = None, workspace_id: int = None):
        """
        Export a report to PDF using POST method (allows passing data in request body).

        Args:
            report_id (int): The ID of the report or report type code.
            request_body (Optional[Dict[str, Any]]): Request body containing:
                - params (dict): Report parameters
                - data (dict): JSON data to be passed to the report
                - lang (str): Preferred language of the report
                - timezone (str): Preferred timezone
                - format (str): Document format (default: "pdf")
                - includeAttachments (bool): Whether to include attachments
                - theme (str): Theme for PDF export/generation
                - template (str): Template for PDF export/generation
            workspace_id (int, optional): The workspace ID.

        Returns:
            bytes: The PDF content.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        headers["Content-Type"] = "application/json"

        url = self.__get_url_with_workspace(f"reports/{report_id}/pdf", workspace_id)

        if request_body is None:
            request_body = {}

        if "format" not in request_body:
            request_body["format"] = "pdf"

        response = requests.post(url, headers=headers, json=request_body)
        self.__check_authentication(response)
        response.raise_for_status()

        if "application/pdf" not in response.headers.get("Content-Type", "").lower():
            raise RuntimeError("Invalid content type, expected PDF")

        return response.content
    
    @__handle_requests_exceptions
    def start_report_export(self, report_id: int, request_body: dict = None, workspace_id: int = None):
        """
        Start asynchronous report generation.

        Args:
            report_id (int): The ID of the report or report type code.
            request_body (Optional[Dict[str, Any]]): Request body containing:
                - params (dict): Report parameters
                - data (dict): JSON data to be passed to the report
                - lang (str): Preferred language of the report
                - timezone (str): Preferred timezone
                - format (str): Document format (default: "pdf")
                - includeAttachments (bool): Whether to zip the report and data attachments
                - excludePages (list[int]): Array of page numbers to exclude from the report
                - tempDataId (int): ID of the temporary data object
                - theme (str): Theme for PDF export/generation
                - template (str): Template for PDF export/generation
            workspace_id (int, optional): The workspace ID.

        Returns:
            Dict[str, Any]: Response containing temporaryFileId for polling status.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        headers["Content-Type"] = "application/json"

        url = self.__get_url_with_workspace(f"reports/{report_id}/export", workspace_id)

        if request_body is None:
            request_body = {}

        if "format" not in request_body:
            request_body["format"] = "pdf"

        response = requests.post(url, headers=headers, json=request_body)

        self.__check_authentication(response)
        if response.status_code != 202:
            response.raise_for_status()

        return response.json()

    @__handle_requests_exceptions
    def get_jobs(self, workspace_id: int = None):
        """
        Get the list of all jobs in the workspace.
    
        Args:
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.
    
        Returns:
            List[Dict[str, Any]]: A list of jobs with their configurations and metadata.
    
        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"jobs", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()
        return response.json()
    
    @__handle_requests_exceptions
    def start_job_run(self, job_id: int, request_body: dict = None, workspace_id: int = None):
        """
        Start a new job run for the specified job.
    
        Args:
            job_id (int): The ID of the job to run.
            request_body (Optional[Dict[str, Any]]): Request body containing:
                - params (dict): Job parameters
                - data (dict): JSON data to be passed to the job
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.
    
        Returns:
            Dict[str, Any]: Response containing jobRunId for tracking the run.
    
        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        headers["Content-Type"] = "application/json"
        url = self.__get_url_with_workspace(f"jobs/{job_id}/runs", workspace_id)
        if request_body is None:
            request_body = {}
        response = requests.post(url, headers=headers, json=request_body)
        self.__check_authentication(response)
        response.raise_for_status()
        return response.json()
    
    @__handle_requests_exceptions
    def get_job_run_status(self, job_id: int, run_id: int, workspace_id: int = None):
        """
        Get the status of a specific job run.
    
        Args:
            job_id (int): The ID of the job.
            run_id (int): The ID of the job run.
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.
    
        Returns:
            Dict[str, Any]: Job run status information including:
                - finished (bool): Whether the job run has completed
                - entries (int): Total number of entries
                - status (dict): Breakdown of entry statuses (queued, review, completed, errors)
    
        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"jobs/{job_id}/runs/{run_id}/status", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()
        return response.json()
    
    @__handle_requests_exceptions
    def get_run_review_document(self, job_id: int, run_id: int, workspace_id: int = None):
        """
        Generate a review document for entries that require review in a job run.
    
        This is typically used when a job has reviewRequired=true and there are entries
        with status 'review' that need to be examined before delivery.
    
        Args:
            job_id (int): The ID of the job.
            run_id (int): The ID of the job run.
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.
    
        Returns:
            Dict[str, Any]: Response containing temporaryFileId for downloading the review document.
    
        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"jobs/{job_id}/runs/{run_id}/generate-review-document", workspace_id)
        response = requests.post(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()
        return response.json()
    
    @__handle_requests_exceptions
    def deliver_job_run_entries(self, job_id: int, run_id: int, workspace_id: int = None):
        """
        Deliver (finalize) the entries from a completed job run.

        This should be called after the job run is finished and any required reviews
        are completed. It triggers the final delivery of all job run entries.

        Args:
            job_id (int): The ID of the job.
            run_id (int): The ID of the job run.
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"jobs/{job_id}/runs/{run_id}/deliver", workspace_id)
        response = requests.post(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()
    
    @__handle_requests_exceptions
    def create_auth_token(self):
        """
        Create a new authentication token.

        Returns:
            Dict[str, Any]: The new authentication token details.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = f"{self.url}/api/v1/nonce-tokens"
        response = requests.post(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()

    @__handle_requests_exceptions
    def push_temporary_data(self, data:dict, workspace_id: int = None):
        """
        Push temporary data to the API.

        Args:
            data (Dict[str, Any]): The data to be pushed.
            workspace_id (int, optional): The workspace ID. If not provided, uses the default workspace.

        Returns:
            Dict[str, Any]: The response from the API.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()

        url = self.__get_url_with_workspace("temporary-data", workspace_id)
        data = {
            "content": data
        }

        response = requests.post(url, headers=headers, json=data)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()
    
    def get_preview_url(self, report_id:int, query_params:dict = None, workspace_id:int = None):
        """
        Get the preview URL for a report.

        Args:
            report_id (int): The ID of the report.
            query_params (Optional[Dict[str, Any]]): Optional query parameters for the request.

        Returns:
            str: The preview URL.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        url = self.__get_preview_url(f"reports/{report_id}/preview", workspace_id)
        nonce_token = self.create_auth_token()['nonce']
        query_params = query_params or {}
        query_params['nonce'] = nonce_token
        url = self.__append_query_params(url, query_params)
        return url

    @__handle_requests_exceptions
    def get_export_status(self, temp_file_id: int, workspace_id: int = None):
        """
        Get the status of an asynchronous export.

        Args:
            temp_file_id (int): The temporary file ID from the export request.
            workspace_id (int, optional): The workspace ID.

        Returns:
            Dict[str, Any]: The export status information.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"exports/{temp_file_id}/status", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.json()

    @__handle_requests_exceptions
    def get_export_content(self, temp_file_id: int, workspace_id: int = None):
        """
        Download the content of a completed export.

        Args:
            temp_file_id (int): The temporary file ID from the export request.
            workspace_id (int, optional): The workspace ID.

        Returns:
            bytes: The exported file content.

        Raises:
            RuntimeError: If any request or processing error occurs.
        """
        headers = self.__get_headers()
        url = self.__get_url_with_workspace(f"exports/{temp_file_id}/content", workspace_id)
        response = requests.get(url, headers=headers)
        self.__check_authentication(response)
        response.raise_for_status()

        return response.content

    def __append_query_params(self, url: str, query_params: Dict[str, Any]) -> str:
        """
        Append query parameters to the URL.

        Args:
            url (str): The base URL.
            query_params (Dict[str, Any]): The query parameters to append.

        Returns:
            str: The URL with query parameters attached.
        """

        if query_params is None:
            return url
        params = {}

        if 'tempDataId' in query_params and isinstance(query_params['tempDataId'], int):
            params['tempDataId'] = query_params['tempDataId']

        if 'params' in query_params and isinstance(query_params['params'], dict):
            json_params = json.dumps(query_params['params'])
            encoded_params = base64.urlsafe_b64encode(json_params.encode()).decode()
            params['params'] = encoded_params

        if 'nonce' in query_params and isinstance(query_params['nonce'], str):
            params['nonce'] = query_params['nonce']

        if 'data' in query_params and isinstance(query_params['data'], str):
            params['data'] = query_params['data']

        if 'timezone' in query_params and isinstance(query_params['timezone'], str):
            params['timezone'] = query_params['timezone']

        if 'lang' in query_params and isinstance(query_params['lang'], str):
            params['lang'] = query_params['lang']

        if 'type' in query_params and isinstance(query_params['type'], str):
            params['type'] = query_params['type']

        if 'includeAttachments' in query_params and isinstance(query_params['includeAttachments'], bool):
            params['includeAttachments'] = query_params['includeAttachments']

        if 'theme' in query_params and isinstance(query_params['theme'], str):
            params['theme'] = query_params['theme']

        if 'template' in query_params and isinstance(query_params['template'], str):
            params['template'] = query_params['template']

        return f"{url}?{urllib.parse.urlencode(params)}"
    
