from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import datetime
from data import LLMResponse

# the service for sending API request to the destination
class ActionService:

    def __init__(self):
        pass

    def perform_action(self, response: LLMResponse):
        scopes = response.scope
        service_name = response.service_name.value
        service_version = response.service_version

        service = self.request_service(scopes, service_name, service_version)
        api_result_response = self.send_api_request(service, response)
        return api_result_response

    def request_service(self, scopes, service_name, service_version):
        try:
            creds = None
            credential_file_name = "credentials.json"

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credential_file_name, scopes
                    )
                    creds = flow.run_local_server(port=0)
        except:
            print("No valid credentials")

        service = build(service_name, service_version, credentials=creds)

        return service
    
    def send_api_request(self, service, llm_response: LLMResponse):
        # currently assume we are adding an event
        # event should be request.content.event
        params = llm_response.params
        event = service.events().insert(calendarId=params['calendarId'], body=params['body']).execute()
        return True