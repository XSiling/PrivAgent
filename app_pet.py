import time
from tool import display_gmail_messages
from email_service import EmailService
from action_service import ActionService
from confirm_service import ConfirmService
from queue import Queue
from data import APICall
# continuously running the backend server, including:
# for certain period:
#   retrieve the information

class ConfirmEvent:
    message: APICall
    
    def __init__(self, message):
        self.message = message

class Server:
    email_service: EmailService
    action_service: ActionService
    confirm_service: ConfirmService

    event_queue: Queue
    handler_queue: Queue

    server_start_time = None

    def __init__(self):
        self.server_start_time = time.time()
        fake_start_time = 1731018098000
        self.email_service = EmailService(self.server_start_time)
        # self.email_service = EmailService(fake_start_time)
        self.action_service = ActionService()
        self.confirm_service = ConfirmService()
        self.event_queue = Queue()
        self.handler_queue = Queue()

    def run_server(self):
        while True:
            # retrive message from email server
            new_messages = self.email_service.retrieve_messages()

            for message in new_messages:
                # send prompt to LLM
                prompt = self.email_service.generate_prompt(message)
                response = self.email_service.send_message_to_llm_agent(prompt)[0]

                # confirm from user
                self.event_queue.put(ConfirmEvent(response))
                confirm_response = self.handler_queue.get()
                # confirm_response = self.confirm_service.get_confirmation(response)

                if confirm_response:
                    # send action to action service
                    self.action_service.send_http_request(response)
                    print("has done the action")
                # send history to LLM
                self.email_service.save_history(response, confirm_response)

            time.sleep(2)


if __name__ == '__main__':
    server = Server()
    server.run_server()