from enum import Enum
from requests.models import Response

class GmailConfiguration:
    email_whitelist = ["jih119@ucsd.edu", "xisheng@ucsd.edu"]

class TokenExpirationPolicy(Enum):
    # expire in certain times
    EXPIRE_IN_TIMES = "expire_in_times"

    # expire after certain time period
    EXPIRE_AFTER_TIME = "expire_after_time"
    
class GmailMessage:
    id = ""
    thread_id = ""
    send_from = ""
    date = ""
    send_to = ""
    content = ""

    def __init__(self, id, thread_id, send_from, date, send_to, content):
        self.id = id
        self.thread_id = thread_id
        self.send_from = send_from
        self.date = date
        self.send_to = send_to
        self.content = content

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

class APICall:
    scope = None 
    api = None
    method = None
    headers = None
    params = None
    body = None
    thread_id = None
    
    def __init__(self, scope, api, method, params, body, thread_id):
        if not isinstance(params, dict) or not isinstance(body, dict):
            raise TypeError("Params or body is not a Python dictionary.")
        self.scope = scope
        self.api = api
        self.method = HTTPMethod[method]
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': ''
        }
        self.params = params if params != {} else None
        self.body = body if self.method in [HTTPMethod.POST, HTTPMethod.PUT] and body != {} else None
        self.thread_id = thread_id

    def print(self):
        print("API: ", self.api)
        print("Method: ", self.method)
        print("Headers: ", self.headers)
        print("Params: ", self.params)
        print("Body: ", self.body)

class HistoryRecord:
    gmail_message: GmailMessage
    api_call: APICall
    http_response: Response
    error: Exception

    def __init__(self, gmail_message: GmailMessage, api_call: APICall, http_response:Response, error = None):
        self.gmail_message = gmail_message
        self.api_call = api_call
        self.http_response = http_response
        self.error = error


class ValidationConfiguration:
    create_calendar_event = (HTTPMethod.POST, "https://www.googleapis.com/calendar/v3/calendars/primary/events")
    create_doc = (HTTPMethod.POST, "https://docs.googleapis.com/v1/documents")
    create_sheet = (HTTPMethod.POST, "https://sheets.googleapis.com/v4/spreadsheets")
    get_calendar_events = (HTTPMethod.GET, "https://www.googleapis.com/calendar/v3/calendars/primary/events")
    delete_calendar_event = (HTTPMethod.DELETE, "https://www.googleapis.com/calendar/v3/calendars/primary/events/eventId")
    delete_file_event = (HTTPMethod.DELETE, "https://www.googleapis.com/drive/v2/files/fileId")
    api_whitelist = [create_calendar_event, create_doc, create_sheet, get_calendar_events, delete_calendar_event, delete_file_event]