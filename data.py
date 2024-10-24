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
