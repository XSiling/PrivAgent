import datetime
import os.path
import requests
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


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
  SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
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
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

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
            'Authorization': 'Bearer ya29.a0AeDClZDCxG8wDvdi1TOOR6XZL7pLGAS7YpLpejDj_zgdtwjb62vayckGzN3jGnYSvpETUGXm5zvTZI2VO-aF7gauOpXsYQDYb22V_0zbj93k4wvS6VdR91Xe1ztENMuwl0nEe1OYYGmV6OKauxZl4zLoAiWjQKJBW_-k6yveaCgYKAT4SARASFQHGX2Mip0OaCNaaDTA31VHghX9oHw0175'
        }
        params = {}
        body = {'summary': 'Project Meeting with Jieyi', 'description': '', 'start': {'dateTime': '2024-10-24T13:00:00', 'timeZone': 'America/Los_Angeles'}, 'end': {'dateTime': '2024-10-24T14:30:00', 'timeZone': 'America/Los_Angeles'}}
        response = requests.post("https://www.googleapis.com/calendar/v3/calendars/primary/events", params=params, headers=headers, json=body)

        print(response.text)

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_file_with_http_api():

    try:
        print("Creating file in Google Drive")
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ya29.a0AeDClZCbAFXYnhdnUYR8YrtyvgOuF5ZLi1cLw6leC6kR-pNJynRHbo6pgiCeqEazDqYe2-7xaCVt8jk0HRBnlN_7qMmt-XpbeuJBkq9t1NQZOXwxtUmX2JJuDhrr-HxZ5UCUFK95rG-GNT70WFssfCWIffb8dW4PAzDKur8EaCgYKAaASARASFQHGX2MileQTY42FKzEOyvohsz6HDw0175'
        }
        params = {'name': 'Test doc 20241112010734', 'parents': ['root'], 'body': {'content': 'this is a test doc', 'mimeType': 'text/markdown'}}
        body = {'name': 'Test doc 20241112010734', 'parents': ['root'], 'body': {'content': 'this is a test doc', 'mimeType': 'text/markdown'}}
        response = requests.post("https://www.googleapis.com/drive/v3/files", params=params, headers=headers, json=body)

        print(response.text)

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_doc_with_http_api():

    try:
        print("Creating Google Doc")
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ya29.a0AeDClZCbAFXYnhdnUYR8YrtyvgOuF5ZLi1cLw6leC6kR-pNJynRHbo6pgiCeqEazDqYe2-7xaCVt8jk0HRBnlN_7qMmt-XpbeuJBkq9t1NQZOXwxtUmX2JJuDhrr-HxZ5UCUFK95rG-GNT70WFssfCWIffb8dW4PAzDKur8EaCgYKAaASARASFQHGX2MileQTY42FKzEOyvohsz6HDw0175'
        }
        params = {'body': {'content': 'this is a test doc', 'location': {'index': 0, 'relativePositioning': {}}}, 'title': 'Test doc', 'bodyLocation': 'LOCATION_HEADER_OR_FOOTER', 'parent': {'id': 'root'}, 'resourceId': {'documentId': 'auto'}, 'timeZone': 'America/Los_Angeles', 'createdTime': '2024-11-12T09:07:34-08:00', 'modifiedTime': '2024-11-12T09:07:34-08:00'}
        body = {'summary': 'Meeting', 'description': 'description', 'start': {'dateTime': '2024-11-13T09:00:00+08:00', 'timeZone': 'America/Los_Angeles'}, 'end': {'dateTime': '2024-11-13T10:00:00+08:00', 'timeZone': 'America/Los_Angeles'}}
        response = requests.post("https://docs.googleapis.com/v1/documents", params=params, headers=headers, json=body)

        print(response.text)

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_cal_events_with_http_api():

    try:
        print("Getting calendar events")
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ya29.a0AeDClZBo-SnrW8t_MQofNaGwN2E59YPtdhvU7OcaiUE81y-dgMrQE_9lKUzxv1ZtzNSev9P_1bnXRuyMc3YKuwtLgrn8eTFTRCrY_wcAFy_nSvw7N7yb3dys2nqZPGxCPxTANjN22R4h2lnQ4hjLGWlwha0Pub8DVVOhP6dmaCgYKAQoSARASFQHGX2Mi4x4qfVzryzbxKrHRgdZ4fw0175'
        }
        params = None
        body = None
        response = requests.get("https://www.googleapis.com/calendar/v3/calendars/primary/events", params=params, headers=headers, json=body)

        print(response.text)

    except HttpError as error:
        print(f"An error occurred: {error}")


def delete_cal_event():

    try:
        print("Deleting calendar events")
        headers = {
            'Content-Type': 'application/json', 
            'Authorization': 'Bearer ya29.a0AeDClZBo-SnrW8t_MQofNaGwN2E59YPtdhvU7OcaiUE81y-dgMrQE_9lKUzxv1ZtzNSev9P_1bnXRuyMc3YKuwtLgrn8eTFTRCrY_wcAFy_nSvw7N7yb3dys2nqZPGxCPxTANjN22R4h2lnQ4hjLGWlwha0Pub8DVVOhP6dmaCgYKAQoSARASFQHGX2Mi4x4qfVzryzbxKrHRgdZ4fw0175'
        }
        params = {"eventId": "11"}
        body = None
        response = requests.delete("https://www.googleapis.com/calendar/v3/calendars/primary/events", params=params, headers=headers, json=body)

        print(response.text)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    print(get_token("https://www.googleapis.com/auth/calendar").token)
    create_calendar_event_with_http_api()
