import datetime
import os.path
import requests
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_token(scopes):
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


def get_calendar_events_with_python_library():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = get_token(SCOPES)
  
  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="xisheng@ucsd.edu",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")


def get_calendar_events_with_http_api():
    creds = get_token(SCOPES)
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    end = (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
    print(end)

    try:
        # Call the Calendar API
        print("Getting the upcoming 10 events")
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Accept': 'application/json'
        }
        params = {
            "timeMin": now,
            "singleEvents": True,
            "timeMax": end,
            "orderBy": "startTime"
        }
        response = requests.get("https://www.googleapis.com/calendar/v3/calendars/xisheng@ucsd.edu/events", params=params, headers=headers)

        if response.status_code == 200:
            events = response.json().get('items', [])
            if not events:
                print('No events found for tomorrow.')
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(f"Event: {event['summary']}, Start: {start}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_calendar_event_with_http_api():

    try:
        # Call the Calendar API
        print("Creating calendar event")
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ya29.a0AeDClZCm-VAwu6ZJ3QFaUqk46zy0SWD6xVYAuCKoY_XQX3JVufeVyxhzt_r96XCoO8Eyhz03q4_dpixWJqKNxdm1FPHbUYbE7ES41noKz6T3lFPd4Y_cf6ewHTfeknL88H55kk7ASVZ96wLoYRt6KcGsKjto1BUpPTtxmF_-aCgYKAa0SARASFQHGX2Mie3UAOtUE1ThDM3gYoDwxkA0175'
        }
        params = {'summary': 'Project Meeting with Jieyi', 'description': '', 'start': {'dateTime': '2024-10-24T13:00:00', 'timeZone': 'America/Los_Angeles'}, 'end': {'dateTime': '2024-10-24T14:30:00', 'timeZone': 'America/Los_Angeles'}}
        body = {'summary': 'Project Meeting with Jieyi', 'description': '', 'start': {'dateTime': '2024-10-24T13:00:00', 'timeZone': 'America/Los_Angeles'}, 'end': {'dateTime': '2024-10-24T14:30:00', 'timeZone': 'America/Los_Angeles'}}
        response = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", params=params, headers=headers, json=body)

        print(response.text)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == '__main__':
    create_calendar_event_with_http_api()
