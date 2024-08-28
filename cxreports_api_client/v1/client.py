import requests
import base64
import urllib.parse
import json

class CxReportClientV1:
    def __init__(self, base_url:str, workspace_id:int, token:str):
        self.url = base_url
        self.token = token
        self.workspace_id = workspace_id

    def __get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
        }
    
    def __get_url_with_workspace(self, url:str):
        return f"{self.url}/api/v1/ws/{self.workspace_id}/{url}"

    def get_pdf(self, reportId: int,  query_params: dict = None):
        try:
            headers = self.__get_headers()

            url = self.__get_url_with_workspace(f"reports/{reportId}/pdf")

            # Attach optional query parameters
            if query_params:
                params = {}
                if 'tempDataId' in query_params and isinstance(query_params['tempDataId'], int):
                    params['tempDataId'] = query_params['tempDataId']

                if 'params' in query_params and isinstance(query_params['params'], dict):
                    # Encode the params object to a base64 JSON string
                    json_params = json.dumps(query_params['params'])
                    encoded_params = base64.urlsafe_b64encode(json_params.encode()).decode()
                    params['params'] = encoded_params

                # Append the query parameters to the URL
                url = f"{url}?{urllib.parse.urlencode(params)}"
                print(url)

    
            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()

            # Check if the response content is HTML
            if response.headers.get('Content-Type', '').lower().startswith('text/html'):
                raise RuntimeError("Unauthenticated.")

            if "application/pdf" not in response.headers.get("Content-Type"):
                raise RuntimeError("Invalid content type")

            return response.content

        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.ConnectionError as conn_err:
            raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
        except requests.exceptions.Timeout as timeout_err:
            raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"An error occurred: {req_err}") from req_err

    def get_report_types(self):
        try:
            headers = self.__get_headers()

            url =  f"{self.url}/api/v1/ws/{self.workspace_id}/report-types"

            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()

             # Check if the response content is HTML
            if response.headers.get('Content-Type', '').lower().startswith('text/html'):
                raise RuntimeError("Unauthenticated.")

            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.ConnectionError as conn_err:
            raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
        except requests.exceptions.Timeout as timeout_err:
            raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"An error occurred: {req_err}") from req_err

    def get_workspaces(self):
        try:
            headers = self.__get_headers()

            url = f"{self.url}/api/v1/workspaces"

            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()

             # Check if the response content is HTML
            if response.headers.get('Content-Type', '').lower().startswith('text/html'):
                raise RuntimeError("Unauthenticated.")

            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.ConnectionError as conn_err:
            raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
        except requests.exceptions.Timeout as timeout_err:
            raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"An error occurred: {req_err}") from req_err
            
    def get_reports(self, type:str):
        try:
            headers = self.__get_headers()

            url = f"{self.url}/api/v1/ws/{self.workspace_id}/reports?type={type}"

            response = requests.get(url, headers=headers, verify=False)
            response.raise_for_status()

             # Check if the response content is HTML
            if response.headers.get('Content-Type', '').lower().startswith('text/html'):
                raise RuntimeError("Unauthenticated.")

            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.ConnectionError as conn_err:
            raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
        except requests.exceptions.Timeout as timeout_err:
            raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"An error occurred: {req_err}") from req_err
    def create_auth_token(self):
        try:
            headers = self.__get_headers()

            url = f"{self.url}/api/v1/nonce-tokens"

            response = requests.post(url, headers=headers, verify=False)
            response.raise_for_status()

             # Check if the response content is HTML
            if response.headers.get('Content-Type', '').lower().startswith('text/html'):
                raise RuntimeError("Unauthenticated.")

            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.ConnectionError as conn_err:
            raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
        except requests.exceptions.Timeout as timeout_err:
            raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"An error occurred: {req_err}") from req_err

    def push_temporary_data(self, data:dict):
        try:
            headers = self.__get_headers()

            url = self.__get_url_with_workspace("temporary-data")
            data = {
                "content": data
            }

            response = requests.post(url, headers=headers, json=data, verify=False)
            response.raise_for_status()
            
             # Check if the response content is HTML
            if response.headers.get('Content-Type', '').lower().startswith('text/html'):
                raise RuntimeError("Unauthenticated.")

            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
        except requests.exceptions.ConnectionError as conn_err:
            raise RuntimeError(f"Connection error occurred: {conn_err}") from conn_err
        except requests.exceptions.Timeout as timeout_err:
            raise RuntimeError(f"Timeout occurred: {timeout_err}") from timeout_err
        except requests.exceptions.RequestException as req_err:
            raise RuntimeError(f"An error occurred: {req_err}") from req_err