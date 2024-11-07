from gmail_authentication import GmailService
from llm_agent import LLMAgent
from data import GmailMessage, GmailConfiguration, APICall
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

    # apply the possible rules to filter out the emails
    # 1. only allow those are in the whitelist to send the emails
    # 2. extract the format from the internal Gmail to GmailMessage
    def filter_message(self, msg):
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
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                content += data

        content = urlsafe_b64decode(content)
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff\xe2\x80\xaf]', '', str(content)).replace('\\r','').replace('\\n',' ')
        print("Send From: ", send_from)
        print("Date: ", date)
        print("Send To: ", send_to)
        print("Content: ", content)

        gmail_message = GmailMessage(send_from, date, send_to, content)

        email_address = extract_email_address_from_sender(gmail_message.send_from)
        if email_address not in self.gmail_configurations.email_whitelist:
            return None

        return gmail_message
    
    def retrieve_messages(self, start_timestamp = None, end_timestamp = None):
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
        print("Prompt: ", prompt)
        return prompt

    def send_message_to_llm_agent(self, message: str):
        response : list[APICall] = self.llm_agent.get_api_calls(message)
        return response
    
    def save_history(self, response: APICall, confirm_response: bool):
        # to be written, save the history to the RAG
        pass

