from enum import Enum
from requests.models import Response

class GmailConfiguration:
    email_whitelist = ["jih119@ucsd.edu", "xisheng@ucsd.edu"]


class ActionServiceName(Enum):
    CALENDAR = "calendar"


class GmailMessage:
    id = ""
    send_from = ""
    date = ""
    send_to = ""
    content = ""

    def __init__(self, id, send_from, date, send_to, content):
        self.id = id
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
    
    def __init__(self, scope, api, method, params, body):
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
        self.body = body if body != {} else None

    def print(self):
        print("API: ", self.api)
        print("Method: ", self.method)
        print("Headers: ", self.headers)
        print("Params: ", self.params)
        print("Body: ", self.body)

class HistoryRecord:
    api_call: APICall
    http_response: Response

    def __init__(self, api_call: APICall, http_response:Response):
        self.api_call = api_call
        self.http_response = http_response