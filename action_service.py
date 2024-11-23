from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import datetime
from data import APICall
import requests

# the service for sending API request to the destination
class ActionService:

    def __init__(self):
        pass

    def get_token(self, scopes):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", scopes
                )
                creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # with open("token.json", "w") as token:
        #     token.write(creds.to_json()) # TODO: For future security improvement, write this file encrypted, or don't write at all
        
        return creds

    
    def send_http_request(self, api_call: APICall):
        try:
            # Get token and add to api_call
            api_call.headers['Authorization'] = f'Bearer {self.get_token([api_call.scope]).token}'
            # Call the Calendar API
            print("Calling the api")
            match api_call.method:
                case 'GET':
                    response = requests.get(api_call.api, params=api_call.params, headers=api_call.headers)
                case 'POST':
                    response = requests.post(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'PUT':
                    response = requests.put(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'DELETE':
                    response = requests.delete(api_call.api, params=api_call.params, headers=api_call.headers)
            print(response.text)
            return response
        except Exception as error:
            print(f"An error occurred: {error}")