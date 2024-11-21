from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService():
    service = None

    def get_service(self):
        if self.service == None:
            creds = None
            if not os.path.exists('token_privAgent.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token_privAgent.json', 'w') as token:
                    token.write(creds.to_json())
            else:
                creds = Credentials.from_authorized_user_file('token_privAgent.json', SCOPES)
                # If there are no (valid) credentials available, let the user log in.
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        try:
                            creds.refresh(Request())
                        except:
                            flow = InstalledAppFlow.from_client_secrets_file(
                                'credentials.json', SCOPES)
                            creds = flow.run_local_server(port=0)
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('token_privAgent.json', 'w') as token:
                        token.write(creds.to_json())

            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            self.service = service
        return self.service