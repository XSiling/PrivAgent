from gmail_authentication import get_gmail_service
from tool import filter_message
from llm_agent import LLMAgent
from data import GmailMessage

# retrieve the messages for certain period of time
def retrieve_messages(start_timestamp = None, end_timestamp = None):
    service = get_gmail_service()

    # currently just get all the messages at a time
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messageIds = results.get('messages',[])
    messages = []
    for messageId in messageIds:
        msg = service.users().messages().get(userId='me', id=messageId['id'], format='full').execute()
        filtered_msg = filter_message(msg)
        messages.append(filtered_msg)
    return messages

class EmailProcessor:
    llm_agent = LLMAgent()

    def generate_prompt(self, message: GmailMessage):
        # to be written
        return ""


    def send_message_to_llm_agent(self, message: str):
        response = self.llm_agent.send_llm_request(message)
        return response

