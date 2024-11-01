from enum import Enum
from calendar_api_example import get_token

class GmailConfiguration:
    email_whitelist = ["jih119@ucsd.edu", "xisheng@ucsd.edu"]


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

class LLMResponse:
    permission = []
    api_call = []

    def __init__(self):
        self.permission = []
        self.api_call = []

class APICall_python:
    service_name = None
    version = None
    scope = None
    methods = None
    params = None

    def __init__(self, service_name, version, scope, methods, params):
        self.service_name = service_name
        self.version = version
        self.scope = scope
        self.methods = methods
        self.params = params

    def print(self):
        print("Service name: ", self.service_name)
        print("Version: ", self.version)
        print("Scope: ", self.scope)
        print("Methods: ", self.methods)
        print("Params: ", self.params)


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
        print("Headers: ", self.headers)
        print("Params: ", self.params)
        print("Body: ", self.body)