import ast
import json
from openai import OpenAI
from data import ActionServiceName
from data import APICall
from utils import get_current_time
import requests

base_url = "http://localhost:1234/v1" # Run LM Studio server on this port before running this code

class LLMAgent: 
    client = OpenAI(base_url=base_url, api_key="lm-studio")
    messages = [None]


    def print_messages(self):
        for m in self.messages:
            print(m)


    # Given a system prompt message and a user prompt message, return the LLM response, and save the conversation to messages
    def get_llm_response(self, system_msg, user_msg):
        self.messages[0] = {"role": "system", "content": system_msg}
        self.messages.append({"role": "user", "content": user_msg})

        completion = self.client.chat.completions.create(
            model="model-identifier",
            messages=self.messages,
            temperature=0.7,
        )

        response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})

        return response
    

    # Simple chatbot in rhymes
    def chat(self, message):
        response = self.get_llm_response("", message)
        print(response)
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
            You don't need steps about fetching time or location. Use Los Angeles pacific timezone. \
            Example prompt: Delete a calendar event tomorrow at 9am and create a new one called 'meeting'. \
            Example answer: \
            Get the list of calendar events for tomorrow around 9am. \
            Delete the calendar event obtained from previous step, with start time at tomorrow 9am. \
            Create a new calendar event tomorrow at 9am with name 'meeting'. "
        response = self.get_llm_response(system_msg, message)

        # Parse the response into a list
        action_list = response.split("\n")
        action_list = [i for i in action_list if i != ""]

        print("List of instructions: ", action_list)
        return action_list


    def get_service_code(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google API. \
            Based on the user's (sender's) desired action on Google account, return a piece of code using Google HTTP API to perform the user-specified action. \
            DO NOT use Google Python Client Library. \
            Use time in the date of original forwarded email. Use Los Angeles pacific timezone. \
            Do not give instructions, do not give multiple outputs. \
            "
        
        response = self.get_llm_response(system_msg, message)

        print("Code: ", response)
        return response


    # Deprecated: For APICall_python only
    def get_service_name(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Based on the user's desired action on Google account, return the exact Google API Service name of the user-specified action. \
            Do not give instructions, do not format the output, just one single plain English word of the high level API service name. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Example answer: calendar \
            Example prompt 2: Send an email to Jieyi. \
            Example answer 2: gmail \
            Accepted output format: 'calendar' 'gmail' 'doc' 'meeting' \
            "
        
        response = self.get_llm_response(system_msg, message)

        print("Service Name: ", response)
        return response


    # Deprecated: For APICall_python only
    def get_service_version(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Based on the user's desired action on Google account and the above generated service name, return only one word of the Google API Service version of the user-specified instruction. \
            Do not give instructions, do not format the output, do not write code, do not include the service name, \
            just simply tell me the current API version. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Example answer: v3 \
            "
        
        response = self.get_llm_response(system_msg, message)

        print("Service Version: ", response)
        return response


    def get_service_scope(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Based on the user's desired action on Google account and the above generated service name, return one line of the minimal Google API authentication scope of the user-specified instruction\" \
            Do not give instructions, do not format the output, do not include http params, do not include sentences like 'the scope is xxx', just a plain Google API scope string. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Example answer: https://www.googleapis.com/auth/calendar \
            "
        
        response = self.get_llm_response(system_msg, message)

        print("Service Scope: ", response)
        return response


    # Deprecated: For APICall_python only
    def get_service_methods(self, message):
        # TODO: doesn't work, try first generate the code, then parse out the function calls
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Based on the user's desired action on Google account and the above generated code, \
            return in one line a list of Google Python Client Library functions we need to call to perform the user-specified instruction\" \
            Do not give instructions, do not format the output, do not include the params for the function call, just a plain python list of Google Python function names. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Example answer: ['events', 'insert'] \
            "
        
        response = self.get_llm_response(system_msg, message)
        print("Service Methods: ", response)

        return response


    # Deprecated: For APICall_python only
    def get_service_params_depr(self, message):
        # TODO: doesn't work
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            The user will call the function that you told them just now. \
            Based on the user's desired action on Google account and the above generated service name, \
            return a python object of Google Python Client Library functions we need to call to perform the user-specified instruction\" \
            Do not give instructions, do not format the output, do not include the params for the function call, just a plain python list of Google Python function names. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Use Los Angeles pacific timezone. \
            Example answer: {{body: {{ \
                'summary': 'meeting', \
                'start': {{ \
                    'dateTime': '2024-10-24T09:00:00-07:00', \
                    'timeZone': 'America/Los_Angeles', \
                }}, \
                'end': {{ \
                    'dateTime': '2024-10-24T10:00:00-07:00', \
                    'timeZone': 'America/Los_Angeles', \
                }}, \
            }} \
            "
        
        response = self.get_llm_response(system_msg, message)

        print("Service Params: ", response)
        return response
    

    def get_service_api(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google HTTP API. \
            Based on the user's desired action on their Google account and the above generated code, \
            return in one line the Google API we need to call in order to perform the user-specified instruction. \
            Do not give instructions, do not format the output, do not include the params for the function call, do not include params in the link, just a plain API link. \
            Example prompt: Create a calendar event tomorrow at 9am. Calendar ID: primary \
            Example answer: https://www.googleapis.com/calendar/v3/calendars/primary/events \
            "
        
        response = self.get_llm_response(system_msg, message)
        print("Service API: ", response)

        return response


    def get_service_method(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google HTTP API. \
            Based on the user's desired action on their Google account and the above generated code, \
            return in one word the HTTP method of the Google API we need to call in order to perform the user-specified instruction\" \
            Do not give instructions, do not format the output, do not include the params for the function call, just a plain API link. \
            Example prompt: Create a calendar event tomorrow at 9am. Calendar ID: primary \
            Example answer: POST \
            "
        
        response = self.get_llm_response(system_msg, message)
        print("Service Method: ", response)

        return response


    def get_service_params(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Extract the 'params' variable in the above generated code, and return it in one line as a valid python dictionary. \
            Do not include the variable name, do not give instructions, do not include the variable name and the = sign, do not include any markdown format, just a plain python object of API call parameters. \
            If there's no params needed, simply give me a pair of curly braces representing the empty dictionary. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Example answer: FALSE \
            Example prompt: Delete the calendar event tomorrow at 9am. Calendar ID: primary, Event ID: 12345 \
            Example answer: {{'calendarId': 'primary', 'eventId': '12345'}} \
            "
        
        response = self.get_llm_response(system_msg, message).strip("`")
        print("Service Params: ", response)

        return ast.literal_eval(response)


    def get_service_body(self, message):
        system_msg = "You are an LLM agent that helps user generate function calls to Google Python Client Library. \
            Based on the user's desired action on Google account and the above generated code, \
            return a Python dictionary of the contents we need to pass to the API as body or data, as a one-line string. \
            If there's no body or data needed, simply give me a pair of curly braces representing the empty dictionary. \
            Do not give instructions, do not format the output, do not include the params for the function call, do not include any markdown format, just a plain python list of Google Python function names. \
            Do not include variable names. Change it into user information based on your knowledge. If nothing is known, use some default information. \
            Example prompt: Create a calendar event tomorrow at 9am. \
            Example answer: {{ \
                'summary': 'Meeting', \
                'description': 'description', \
                'start': {{'dateTime': '2024-10-27T09:00:00+08:00'}}, \
                'end': {{ 'dateTime': '2024-10-27T10:00:00+08:00'}} \
            }} \
            "
        
        response = self.get_llm_response(system_msg, message).strip("`")
        print("Service Body: ", response)

        return ast.literal_eval(response)


    # For APICall_python only
    def get_api_calls_python(self, message):
        print("---------Generating an api call---------")
        self.messages = [None]
        instructions = self.get_list_of_instructions(message)
        api_calls = []
        for inst in instructions:
            print("---Working on an instruction---")
            code = self.get_service_code(inst)
            service_name = self.get_service_name(inst)
            version = self.get_service_version(inst)
            scope = self.get_service_scope(inst)
            methods = self.get_service_methods(inst)
            params = self.get_service_params(inst)
            curr_api_call = APICall(
                service_name, version, scope, methods, params,
            )
            curr_api_call.print()
            api_calls.append(curr_api_call)
        
        self.messages = [None]
        return api_calls
    
    
    def get_api_calls(self, message):
        print("---------Generating an api call---------")
        self.messages = [None]
        # instructions = self.get_list_of_instructions(message)
        instructions = [message]    # TODO: improve accuracy of the above function
        api_calls = []
        for inst in instructions:
            print("---Working on an instruction---")
            code = self.get_service_code(inst)
            scope = self.get_service_scope(inst)
            api = self.get_service_api(code)
            method = self.get_service_method(code)
            params = self.get_service_params(code)
            body = self.get_service_body(code)
            curr_api_call = APICall(
                scope, api, method, params, body
            )
            curr_api_call.print()
            api_calls.append(curr_api_call)
        
        self.messages = [None]
        return api_calls
    

def test_api_call_on_prompt():
    agent = LLMAgent()
        
    message = "create a calendar event 'meeting' tomorrow at 9am. The google account is xisheng@ucsd.edu and use calendarId = primary"
    # # message = "Delete my calendar event tomorrow at 9am, then create a new event at the same time called 'my meeting', invite jih119@ucsd.edu"
    # # message = "show me all my unread emails and reply them all with 'I'm not available right now'."
    api_calls = agent.get_api_calls(message)

    try:
        # Call the Calendar API
        print("Calling the api")
        match api_calls[0].method:
            case 'GET':
                response = requests.get(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)
            case 'POST':
                response = requests.post(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)
            case 'PUT':
                response = requests.put(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)
            case 'DELETE':
                response = requests.delete(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)

        print(response.text)

    except Exception as error:
        print(f"An error occurred: {error}")

    # while True:
    #     message = input("You: ")
    #     agent.chat(message)

def test_api_call_on_email():
    from email_service import EmailService
    from data import GmailMessage
    send_from = "Xin Sheng <xisheng@ucsd.edu>"
    date = "Tue, 22 Oct 2024 15:10:32 -0700"
    send_to = "myprivagent@gmail.com"
    content = b'@myprivagent@gmail.com <myprivagent@gmail.com> Help me create an event on the calendar.  ---------- Forwarded message --------- From: Jieyi Huang <jih119@ucsd.edu> Date: Tue, Oct 22, 2024 at 3:09\xe2\x80\xafPM Subject: About the project meeting To: Xin Sheng <xisheng@ucsd.edu>   Hi Xin,  I have discussed some issues with other team members about the project. Would you like to meet at 13:00pm this Thursday about it at the CSE building?  Looking forward to hearing from you.  Best, Jieyi '
    email = GmailMessage(send_from, date, send_to, content)
    email_service = EmailService()
    prompt = email_service.generate_prompt(email)
    api_calls = email_service.send_message_to_llm_agent(prompt)
    try:
        # Call the Calendar API
        print("Calling the api")
        match api_calls[0].method:
            case 'GET':
                response = requests.get(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)
            case 'POST':
                response = requests.post(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)
            case 'PUT':
                response = requests.put(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)
            case 'DELETE':
                response = requests.delete(api_calls[0].api, params=api_calls[0].params, headers=api_calls[0].headers, json=api_calls[0].body)

        print(response.text)

    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    test_api_call_on_email()