# Reference: 
# https://lmstudio.ai/docs/basics/server
# https://platform.openai.com/docs/api-reference/chat

from openai import OpenAI
from data import LLMResponse, ActionServiceName

base_url = "http://localhost:1234/v1" # Run LM Studio server on this port before running this code

class LLMAgent: 
    client = OpenAI(base_url=base_url, api_key="lm-studio")

    # Given a user prompt message, return the LLM response
    def send_llm_request(self, message):
        completion = self.client.chat.completions.create(
        model="model-identifier",
        messages=[
            {"role": "system", "content": "Always answer in rhymes."}, # TODO: delete this in actual development
            {"role": "user", "content": message}
        ],
        temperature=0.7,
        )

        response = completion.choices[0].message.content

        LLM_response = self.response_to_LLMResponse(response)

        return LLM_response
    
    def response_to_LLMResponse(self, response):
        llm_response = LLMResponse()
        llm_response.set_service_name(ActionServiceName.CALENDAR)
        llm_response.set_service_version("v3")
        llm_response.set_scope(["https://www.googleapis.com/auth/calendar"])
        
        event = {
            'summary': 'Attend the project meeting',
            'location': 'CSE Building',
            'description': 'Attend the project meeting discussion with Xin',
            'start': {
                'dateTime': '2024-10-24T13:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2024-10-24T14:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
                {'email': 'jih119@ucsd.edu'},
                {'email': 'xisheng@ucsd.edu'},
            ],
            'reminders': {
                'useDefault': True,
            },
        }

        calendarId='primary'
        
        llm_response.set_params({'calendarId':calendarId, 'body':event})
        return llm_response

    

if __name__ == '__main__':
    agent = LLMAgent()
    while True:
        msg = input("You: ")
        agent.send_llm_request(msg)