from gmail_authentication import GmailService
from llm_agent import LLMAgent
from data import GmailMessage, GmailConfiguration, APICall, HistoryRecord
from base64 import urlsafe_b64decode
from tool import extract_email_address_from_sender
import re

SEND_FROM_KEY = 'From'
DATE_KEY = 'Date'
SEND_TO_KEY = 'To'

class EmailService:
    gmail_service = GmailService()
    llm_agent = LLMAgent()
    gmail_configurations = GmailConfiguration()

    def __init__(self, server_start_time, test_old_emails):
        self.server_start_time = server_start_time
        self.test_old_emails = test_old_emails
        self.email_history = []

    # apply the possible rules to filter out the emails
    # 1. only allow those are in the whitelist to send the emails
    # 2. extract the format from the internal Gmail to GmailMessage
    def filter_message(self, msg):
        internalDate = msg['internalDate']
        id = msg['id']
        payload = msg['payload']
        headers = payload['headers']
        parts = payload['parts']
        send_from, date, send_to, content = "", "", "", ""

        # the email is sent before the server starts, ignore it
        if not self.test_old_emails and float(internalDate)/1000 <= self.server_start_time:
            return None
        
        # the email is already processed before, ignore it
        if id in self.email_history:
            return None

        for header in headers:
            if header['name'] == SEND_FROM_KEY:
                send_from = header['value']

            if header['name'] == DATE_KEY:
                date = header['value']
            
            if header['name'] == SEND_TO_KEY:
                send_to = header['value']

        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                content += data

        content = urlsafe_b64decode(content)
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff\xe2\x80\xaf]', '', str(content)).replace('\\r','').replace('\\n',' ')

        gmail_message = GmailMessage(id, send_from, date, send_to, content)

        email_address = extract_email_address_from_sender(gmail_message.send_from)
        if email_address not in self.gmail_configurations.email_whitelist:
            return None

        return gmail_message
    
    def retrieve_messages(self):
        service = self.gmail_service.get_service()

        # currently just get all the messages at a time
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messageIds = results.get('messages',[])
        messages = []
        for messageId in messageIds:
            msg = service.users().messages().get(userId='me', id=messageId['id'], format='full').execute()
            filtered_msg = self.filter_message(msg)
            if filtered_msg != None:
                messages.append(filtered_msg)
        return messages
    
    def generate_prompt(self, message: GmailMessage):
        # TODO: Improve this
        prompt = "Sender: " + message.send_from + "\nReceiver: " + message.send_to + "\nDate: " + message.date + "\nContent: " + str(message.content)
        print("Prompt: \n", prompt)
        return prompt

    def send_message_to_llm_agent(self, message: str):
        response : list[APICall] = self.llm_agent.get_api_calls(message)
        return response
    
    def save_history(self, response: APICall, confirm_response):
        self.email_history.append(
            HistoryRecord(response, confirm_response)
        )

    def get_history_as_string(self):
        content = ""
        for record in self.email_history:
            record_string = ""
            record_string += "scope: {}\t".format(" ".join(record.api_call.scope))
            record_string += "api: {}\t".format(str(record.api_call.api))
            record_string += "method: {}\t".format(str(record.api_call.method))
            record_string += "headers: {}\t".format(str(record.api_call.headers))
            record_string += "params: {}\t".format(str(record.api_call.params))
            record_string += "body: {}\t".format(str(record.api_call.body))

            record_string += "response: {}\t".format(str(record.http_response))
            content += record_string 
            content += "\n"
        return content

