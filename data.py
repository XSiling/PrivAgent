from enum import Enum
from calendar_api_example import get_token

class GmailConfiguration:
    email_whitelist = ["jih119@ucsd.edu", "xisheng@ucsd.edu"]


class ActionServiceName(Enum):
    CALENDAR = "calendar"


class GmailMessage:
    send_from = ""
    date = ""
    send_to = ""
    content = ""

    def __init__(self, send_from, date, send_to, content):
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
        scopes = [scope]
        print(scopes)
        self.scope = scope
        self.api = api
        self.method = HTTPMethod[method]
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {get_token(scopes).token}'
        }
        self.params = params
        self.body = body

    def print(self):
        print("API: ", self.api)
        print("Method: ", self.method)
        print("Headers: ", self.headers)
        print("Params: ", self.params)
        print("Body: ", self.body)
