from enum import Enum

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

class LLMResponse:
    scope = []
    service_name: ActionServiceName
    service_version = ""
    params = {}

    def __init__(self):
        self.service_name = None
        self.service_version = ""
        self.scope = []
        self.params = {}

    def set_service_name(self, service_name: ActionServiceName):
        self.service_name = service_name
    
    def set_scope(self, scope):
        self.scope = scope
    
    def set_service_version(self, version):
        self.service_version = version
    
    def set_params(self, params):
        self.params = params
    
