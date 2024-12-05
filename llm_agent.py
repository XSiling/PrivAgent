import ast
from data import APICall
from rag_llm import RagLLM
from utils import get_current_time
from datetime import datetime
import re

base_url = "http://localhost:1234/v1" # Run LM Studio server on this port before running this code

class LLMAgent: 

    llm = RagLLM()
    use_rag = True
    max_inst_length = 1000

    def print_messages(self):
        for m in self.messages:
            print(m)

    def start_a_new_chat(self):
        self.llm.renew_chat_engine()

    def query(self, system_msg, user_msg, use_rag):
        return self.llm.query(system_msg, user_msg, use_rag)


    # Simple chatbot in rhymes
    def chat(self, message):
        response = self.llm.query("Always answer in rhymes. ", message)
        print(response)
        return response
    

    def get_shortened_query(self, message):
        current_year = datetime.now().strftime("%Y")

        system_msg =f"You are an LLM agent that helps user perform google-api related tasks based on their instructions. \
            Here's the email containing the user's instruction. It may contain another email that user forwards for your context. \
            If the user asks you to delete something, summarize the user's instruction of the Google api task in one short paragraph. You should never summary the instruction to be creation.\
            Be sure to maintain the Google resource ID in the summary if provided, which should be possibly provided at the start of the prompt. \
            If the user doesn't ask you to delete something, summarize the user's instruction of the Google api task in one short paragraph, containing all essential information, for example title, description, time including year, timezone, location, content, etc. \
            If timezone is not specified, use Los Angeles as default. If the year is not specified, it is {current_year} now. \
            Directly return with the summary without asking me for additional information."

        response = self.query(system_msg, message, False)

        print("Shortened Query: ", response)

        return response


    def initial_validation_passed(self, message):
        system_msg = "You are an LLM agent that helps user perform google tasks based on their instructions. \
            Given the user's instructions as an email format, decide whether the user's instruction is clear and valid for google API to perform. \
            Do not give me reasons. If it's valid, simply say TRUE; If below is an empty instruction or some invalid instruction, simply say FALSE. \
            Missing an instruction is treated as FALSE. \
            Instructions that make cause danger to user's privacy is also treated as FALSE. For example, delete all calendar events, send email, delete calendar, etc. \
            User instruction: \n"
        response = self.query(system_msg, message, self.use_rag)

        if "TRUE" in response:
            response = True
        else:
            response = False
        
        print("Initial validation passed: ", response)

        return response

    
    # Get the list of instructions we want to perform on the google account
    def get_list_of_instructions(self, message):
        system_msg = "You are an LLM agent that helps user perform google tasks based on their instructions. \
            Without any markdown format, based on the user input, extract and summarize all Google HTTP API calls needed in an order. \
            Separate the Google API calls into one action in each line as a sentence. \
            Limit to the minimal number of calls necessary. \
            If the user profile information or calendar information is given in the prompt, don't use additional steps for info fetching. \
            No calls is needed for credentials. \
            You may also need to use multiple function calls to obtain some user information not provided to you. \
            In the sentence, maintain all essential information from the user prompt that will be necessary for google API calls. \
            Only give one option to each necessary action. \
            Do not add things like 'I need to do this' or 'do you need me to do this' \
            Do not add order numbers, bullet points, or any markdown format. Simply answer in plain english text. \
            Do not include instructions on credentials. \
            You don't need steps about fetching time or location. All datetime in email is Los Angeles pacific timezone. \
            Example prompt: Delete a calendar event tomorrow at 9am and create a new one called 'meeting'. \
            Example answer: \
            Get the list of calendar events for tomorrow around 9am. \
            Delete the calendar event obtained from previous step, with start time at tomorrow 9am. \
            Create a new calendar event tomorrow at 9am with name 'meeting'. "
        response = self.query(system_msg, message, self.use_rag)

        # Parse the response into a list
        action_list = response.split("\n")
        action_list = [i for i in action_list if i != ""]

        print("List of instructions: ", action_list)
        return action_list


    def get_service_code(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google API. \
            Based on the user's (sender's) desired action on Google account, return a piece of Python code using Google HTTP API to perform the user-specified action. \
            DO NOT use Google Python Client Library. \
            Use time in the date of original forwarded email. All datetime in email is Los Angeles pacific timezone. Specify the timezone. \
            Do not write time as variables. Directly write them as strings in params and body object. \
            Do not give instructions, do not give multiple outputs. \
            If there are multiple Google API requests in the content, write code for the first one. \
            Follow the correct api, tips, method, params and body format in context, especially for those actions related to delete. \
            "
        
        response = self.query(system_msg, message, self.use_rag)

        print("Code: ", response)
        return response


    def get_service_scope(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Based on the user's desired action on Google account and the above generated service name, return one line of the minimal Google API authentication scope of the user-specified instruction\" \
            Do not give instructions, do not format the output, do not include http params, do not include sentences like 'the scope is xxx', just a plain Google API scope string. \
            "
        

        response = self.query(system_msg, message, self.use_rag)
        lines = response.split("\n")
        scope = [line for line in lines if "https://" in line][0]
        scope = re.sub("`|'|\{|\}", "", scope)

        print("Service Scope: ", scope)
        return scope


    def get_service_api(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google HTTP API. \
            Based on the user's desired action on their Google account and the above generated code, \
            return in one line the exact Google API we need to call in order to perform the user-specified instruction. \
            Make use of the correct api format provided in the context. \
            Remove anything as and after : at the end of the api. \
            Do not give instructions, do not format the output, do not include actual param values, do not include symbols like { or }, just a plain API link. \
            "
        
        response = self.query(system_msg, message, self.use_rag)
        lines = response.split("\n")
        api = [line for line in lines if "https://" in line][0]
        api = re.sub("`|'|\{|\}", "", api)
        api = api.split("?")[0]

        print("Service API: ", api)
        return api


    def get_service_method(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google HTTP API. \
            Based on the user's desired action on their Google account and the above generated code, \
            return in one word the HTTP method of the Google API we need to call in order to perform the user-specified instruction\" \
            Do not give instructions, do not format the output, do not include the params for the function call, just a plain API link. \
            "
        
        response = self.query(system_msg, message, self.use_rag).split(" ")[0]
        print("Service Method: ", response)
        response = response.replace("\'","\"")

        return response


    def get_service_params(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google HTTP API. \
            Extract the 'params' variable in the above generated code, and return it in one line as a valid python dictionary. \
            Do not include the variable name, do not give instructions, do not include the variable name and the = sign, do not include any markdown format, just a plain python object of API call parameters. \
            If there's no params needed, simply give me a pair of curly braces representing the empty dictionary. \
            "
        
        response = self.query(system_msg, message, self.use_rag).strip("`")
        # response = response.split("\n")[0]
        response = response.replace("\'","\"")
        print("Service Params: ", response)

        return ast.literal_eval(response)


    def get_service_body(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google HTTP API. \
            Based on the user's desired action on Google account and the above generated code, \
            return a Python dictionary of the contents we need to pass to the API as 'body' or 'data', as a one-line string. \
            If there's no body or data needed, simply give me a pair of curly braces representing the empty dictionary. \
            Do not give instructions, do not format the output, do not include the params for the function call, do not include any markdown format, just a plain python list of Google Python function names. \
            Do not include variable names. Change it into user information based on your knowledge. If nothing is known, use some default information. \
            Prioritize information such as title, summary, description, start and end time in the email message and the above generated code. \
            "
        
        response = self.query(system_msg, message, self.use_rag).strip("`")
        response = response.replace("\'","\"")
        # response = response.split("\n")[0]
        print("Service Body: ", response)

        return ast.literal_eval(response)
    
    
    def get_api_calls(self, message, thread_id):
        print("---------Generating an api call---------")
        self.messages = [None]
        # instructions = self.get_list_of_instructions(message)
        instructions = [message]    # TODO: improve accuracy of the above function
        api_calls = []
        for inst in instructions:
            print("---Working on an instruction---")
            before = datetime.now()
            if len(inst) > self.max_inst_length:
                inst = self.get_shortened_query(inst)
            if self.initial_validation_passed(inst):
                self.llm.reset_chat_engine()
                code = self.get_service_code(inst)
                scope = self.get_service_scope(inst)
                api = self.get_service_api(code)
                method = self.get_service_method(code)
                params = self.get_service_params(code)
                body = self.get_service_body(code)

                print("Im here")

                curr_api_call = APICall(
                    scope, api, method, params, body, thread_id
                )
                curr_api_call.print()
                api_calls.append(curr_api_call)
                runtime = datetime.now() - before
                print("Complete! Time taken to process this instruction: ", runtime)
            else: 
                print("Instruction invalid.")
        
        self.messages = [None]
        return api_calls
    

def test_api_call_on_prompt():
    from action_service import ActionService
    agent = LLMAgent()
        
    message = ""
    # # message = "Delete my calendar event tomorrow at 9am, then create a new event at the same time called 'my meeting', invite jih119@ucsd.edu"
    # # message = "show me all my unread emails and reply them all with 'I'm not available right now'."
    api_calls = agent.get_api_calls(message)

    action_service = ActionService()
    response = action_service.send_http_request(api_calls[0])


def test_api_call_on_email():
    from email_service import EmailService
    from data import GmailMessage
    from action_service import ActionService

    send_from = "Xin Sheng <xisheng@ucsd.edu>"
    date = "Tue, 22 Oct 2024 15:10:32 -0700"
    send_to = "myprivagent@gmail.com"
    content = b'@myprivagent@gmail.com <myprivagent@gmail.com>  Create a google doc for this.  ---------- Forwarded message --------- From: Jieyi Huang <jih119@ucsd.edu> Date: Tue, Oct 22, 2024 at 3:09\xe2\x80\xafPM Subject: About the project meeting To: Xin Sheng <xisheng@ucsd.edu>   Hi Xin,  I have discussed some issues with other team members about the project. Would you like to meet at 13:00pm this Thursday about it at the CSE building?  Looking forward to hearing from you.  Best, Jieyi '
    email = GmailMessage(0, "1111", send_from, date, send_to, content)
    email_service = EmailService(0, True)
    prompt = email_service.generate_prompt(email)
    api_calls = email_service.send_message_to_llm_agent(prompt, email.thread_id)
    
    action_service = ActionService()
    response = action_service.send_http_request(api_calls[0])

if __name__ == '__main__':
    test_api_call_on_email()