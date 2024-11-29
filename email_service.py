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
        self.email_history: list[HistoryRecord] = []


    def extract_message_content(self, payload):
        mime_type = payload['mimeType']
        recursive_type = ['multipart/mixed', 'multipart/alternative']
        direct_process_type = ['text/plain']
        ignore_type = ['text/html']

        total_content = ""
        if mime_type in recursive_type:
            parts = payload['parts']
            for part in parts:
                content = self.extract_message_content(part)
                total_content += content

        if mime_type in direct_process_type:
            content = payload['body']['data']
            total_content += content

        if mime_type in ignore_type:
            pass

        return total_content
    
    # apply the possible rules to filter out the emails
    # 1. only allow those are in the whitelist to send the emails
    # 2. extract the format from the internal Gmail to GmailMessage
    def filter_message(self, msg):
        # import pdb;pdb.set_trace()
        internalDate = msg['internalDate']
        id = msg['id']
        payload = msg['payload']
        headers = payload['headers']
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

        email_address = extract_email_address_from_sender(send_from)
        if email_address not in self.gmail_configurations.email_whitelist:
            return None
        
        content = self.extract_message_content(payload)
        content = urlsafe_b64decode(content)
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff\xe2\x80\xaf]', '', str(content)).replace('\\r','').replace('\\n',' ')

        gmail_message = GmailMessage(id, send_from, date, send_to, content)

        return gmail_message
    
    def retrieve_messages(self, start_timestamp):
        service = self.gmail_service.get_service()
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=f"after:{start_timestamp}").execute()
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
    
    def save_history(self, gmail_message: GmailMessage, response: APICall, confirm_response, error: Exception = None):
        self.email_history.append(
            HistoryRecord(gmail_message, response, confirm_response, error)
        )

    def get_history_as_string(self):
        content = ""
        for record in self.email_history:
            record_string = ""
            if record.gmail_message: 
                record_string += "gmail id: {}\t".format(str(record.gmail_message.id))
                record_string += "gmail send from: {}\t".format(str(record.gmail_message.send_from))
                record_string += "gmail date: {}\t".format(str(record.gmail_message.date))
                record_string += "send to: {}\t".format(str(record.gmail_message.send_to))
                record_string += "content: {}\t".format(str(record.gmail_message.content))
            if record.api_call:
                record_string += "scope: {}\t".format(" ".join(record.api_call.scope))
                record_string += "api: {}\t".format(str(record.api_call.api))
                record_string += "method: {}\t".format(str(record.api_call.method))
                record_string += "headers: {}\t".format(str(record.api_call.headers))
                record_string += "params: {}\t".format(str(record.api_call.params))
                record_string += "body: {}\t".format(str(record.api_call.body))
            if record.http_response: 
                record_string += "response: {}\t".format(str(record.http_response))
            if record.error:
                record_string += "error: {}\t".format(str(record.error))
            content += record_string 
            content += "\n"
        return content

