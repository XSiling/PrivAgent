import time
from tool import display_gmail_messages
from email_service import EmailService
from action_service import ActionService
from confirm_service import ConfirmService
from validation_service import ValidationService
from queue import Queue
from data import APICall, GmailMessage
from threading import Lock
import threading
from typing import List
from collections import defaultdict
import random

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
    validation_service: ValidationService

    event_queue: Queue
    handler_queue: Queue

    server_start_time = None

    test_old_emails = True # Default should be False. Set this to true when testing with sent emails
    test_one_email_only = False # Default should be False. Set this to true when testing with only one email

    gmail_lock: Lock

    # the current queue to process the email
    email_processing_queue: List[GmailMessage]

    fetch_email_thread: threading.Thread
    process_email_thread: threading.Thread

    def __init__(self):
        self.server_start_time = time.time()
        self.email_service = EmailService(self.server_start_time, self.test_old_emails)
        self.action_service = ActionService()
        self.confirm_service = ConfirmService()
        self.validation_service = ValidationService()
        self.event_queue = Queue()
        self.handler_queue = Queue()
        self.gmail_lock = Lock()
        
        self.email_processing_queue = []
        
        self.fetch_email_thread = threading.Thread(target = self.fetch_email)
        self.process_email_thread = threading.Thread(target = self.process_email)
        self.schedule_email_thread = threading.Thread(target = self.schedule_email)

    def schedule_email(self):
        # schedule the current email
        # current scheduling policy: lottery for each user, for one user, the emails remain the time order
        while True:
            self.gmail_lock.acquire()
            user_email_dict = defaultdict(list)
            scheduled_email_processing_queue = []

            for email in self.email_processing_queue:
                user = email.send_from
                user_email_dict[user].append(email)

            while len(user_email_dict.keys()) != 0:
                lottery_user = random.choice(list(user_email_dict.keys()))
                lottery_email = user_email_dict[lottery_user].pop(0)
                scheduled_email_processing_queue.append(lottery_email)

                if len(user_email_dict[lottery_user]) == 0:
                    user_email_dict.pop(lottery_user)

            self.email_processing_queue = scheduled_email_processing_queue

            self.gmail_lock.release()
            time.sleep(20)

    def fetch_email(self):
        if self.test_old_emails:
            fetch_start_timestamp = 1
        else:
            fetch_start_timestamp = time.time()

        while True:
            current_timestamp = time.time()
            new_messages = self.email_service.retrieve_messages(fetch_start_timestamp)
            fetch_start_timestamp = current_timestamp
            self.gmail_lock.acquire()
            self.email_processing_queue += new_messages
            self.gmail_lock.release()
            time.sleep(10)

    def process_email(self):
        while True:
            self.gmail_lock.acquire()
            if len(self.email_processing_queue) == 0:
                current_message = None
            else:
                current_message = self.email_processing_queue.pop(0)
            self.gmail_lock.release()

            if current_message == None:
                time.sleep(0.5)
            else:
                try:
                    prompt = self.email_service.generate_prompt(current_message)
                    response: list[APICall] = self.email_service.send_message_to_llm_agent(prompt)
                    
                    import pdb;pdb.set_trace()
                    
                    self.validation_service.validate_response(response)

                    for api_call in response:
                        self.event_queue.put(ConfirmEvent(api_call))
                        confirm_response = self.handler_queue.get()
                        http_request_response = False

                        if confirm_response:
                            http_request_response = self.action_service.send_http_request(api_call, current_message)
                            print("has done the action")
                        
                        self.email_service.save_history(api_call, http_request_response)
                    
                    if self.test_one_email_only:
                        return

                except Exception as error:
                    print(f"An error occurred: {error}")
            
    def run_server(self):
        self.fetch_email_thread.start()
        self.process_email_thread.start()
        self.schedule_email_thread.start()

if __name__ == '__main__':
    server = Server()
    server.run_server()