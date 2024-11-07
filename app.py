import time
from tool import display_gmail_messages
from email_service import EmailService
from action_service import ActionService
from confirm_service import ConfirmService

# continuously running the backend server, including:
# for certain period:
#   retrieve the information
class Server:
    email_service = EmailService()
    action_service = ActionService()
    confirm_service = ConfirmService()

    def run_server(self):
        # retrive message from email server
        new_messages = self.email_service.retrieve_messages()

        # just process the first message now
        message = new_messages[0]
        # display_gmail_messages([message])

        # send prompt to LLM
        prompt = self.email_service.generate_prompt(message)
        response = self.email_service.send_message_to_llm_agent(prompt)

        # confirm from user
        confirm_response = self.confirm_service.get_confirmation(response[0])

        if confirm_response:
            # send action to action service
            self.action_service.send_http_request(response[0])

        # send history to LLM
        self.email_service.save_history(response[0], confirm_response)



if __name__ == '__main__':
    server = Server()
    server.run_server()