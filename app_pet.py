import time
from tool import display_gmail_messages
from email_service import EmailService
from action_service import ActionService
from confirm_service import ConfirmService
from queue import Queue
# continuously running the backend server, including:
# for certain period:
#   retrieve the information

class ConfirmEvent:
    
    def __init__(self, message):
        self.message = message

class Server:
    email_service = EmailService()
    action_service = ActionService()
    confirm_service = ConfirmService()

    event_queue = Queue()
    handler_queue = Queue()

    server_start_time = None

    def __init__(self):
        self.server_start_time = time.time()
        
    def run_server(self):

        # import pdb;pdb.set_trace()
        #check here
        
        # retrive message from email server
        new_messages = self.email_service.retrieve_messages()

        # just process the first message now
        message = new_messages[0]
        # display_gmail_messages([message])

        # send prompt to LLM
        prompt = self.email_service.generate_prompt(message)
        response = self.email_service.send_message_to_llm_agent(prompt)

        # confirm from user
        self.event_queue.put(ConfirmEvent(response))
        confirm_response = self.handler_queue.get()
        # confirm_response = self.confirm_service.get_confirmation(response)

        if confirm_response:
            # send action to action service
            self.action_service.perform_action(response)
            print("has done the action")
        # send history to LLM
        self.email_service.save_history(response, confirm_response)



if __name__ == '__main__':
    server = Server()
    server.run_server()