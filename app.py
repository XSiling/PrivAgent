import time
from email_receiver import retrieve_messages
from tool import display_gmail_messages
from email_receiver import EmailProcessor

# continuously running the backend server, including:
# for certain period:
#   retrieve the information
class Server:
    email_processor = EmailProcessor()

    def run_server(self):
        new_messages = retrieve_messages()
        
        # just process the first message now
        message = new_messages[0]
        display_gmail_messages([message])

        prompt = self.email_processor.generate_prompt(message)
        response = self.email_processor.send_message_to_llm_agent(prompt)

        print("response:", response)

if __name__ == '__main__':
    server = Server()
    server.run_server()