from data import GmailMessage
from base64 import urlsafe_b64decode


def extract_email_address_from_sender(sender:str):
    email_address = sender.split(' ')[-1]
    email_address = email_address[1:-1]
    return email_address

def display_gmail_message(msg: GmailMessage):
    print("Send from:", msg.send_from)
    print("Date:", msg.date)
    print("Send to:", msg.send_to)
    print("Content:", msg.content)

def display_gmail_messages(msg_list: [GmailMessage]):
    for msg in msg_list:
        display_gmail_message(msg)

