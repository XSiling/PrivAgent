from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import datetime

# the service for sending API request to the destination
class ActionService:

    def __init__(self):
        pass
    
    def request_service(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # import pdb;pdb.set_trace()
        # current assume that we are trying to add an event in the calendar
        scopes =  ["https://www.googleapis.com/auth/calendar"]

        credential_file_name = "credentials.json"
        service_name = "calendar"
        version = "v3"

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credential_file_name, scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run

        service = build(service_name, version, credentials=creds)
        return service
    
    def send_api_request(self, service, request):
        # currently assume we are adding an event
        # event should be request.content.event

        event = {
            'summary': 'Attend the project meeting',
            'location': 'CSE Building',
            'description': 'Attend the project meeting discussion with Xin',
            'start': {
                'dateTime': '2024-10-24T13:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2024-10-24T14:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
                {'email': 'jih119@ucsd.edu'},
                {'email': 'xisheng@ucsd.edu'},
            ],
            'reminders': {
                'useDefault': True,
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
