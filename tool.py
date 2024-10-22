from data import GmailMessage
from base64 import urlsafe_b64decode



SEND_FROM_KEY = 'From'
DATE_KEY = 'Date'
SEND_TO_KEY = 'To'


def display_gmail_message(msg: GmailMessage):
    print("Send from:", msg.send_from)
    print("Date:", msg.date)
    print("Send to:", msg.send_to)
    print("Content:", msg.content)

def display_gmail_messages(msg_list: [GmailMessage]):
    for msg in msg_list:
        display_gmail_message(msg)

def filter_message(msg):
    payload = msg['payload']
    headers = payload['headers']
    parts = payload['parts']
    send_from, date, send_to, content = "", "", "", ""

    for header in headers:
        if header['name'] == SEND_FROM_KEY:
            send_from = header['value']

        if header['name'] == DATE_KEY:
            date = header['value']
        
        if header['name'] == SEND_TO_KEY:
            send_to = header['value']

    for part in parts:
        data = part['body']['data']
        # import pdb;pdb.set_trace()
        content += data

    # import pdb;pdb.set_trace()
    content = urlsafe_b64decode(content)

    gmail_message = GmailMessage(send_from, date, send_to, content)
    return gmail_message