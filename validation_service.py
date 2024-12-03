from data import APICall, ValidationConfiguration, HTTPMethod
from dateutil.parser import parse, ParserError
from email_service import EmailService

class ValidationService:
    def validate_response(self, response: list[APICall]):
        self.check_response_not_empty(response)

        for api_call in response:
            self.check_api_in_whitelist(api_call)
            self.check_valid_params(api_call)
            self.check_resource_id_is_related(api_call)


    def check_valid_params(self, response: APICall):
        # check the time
        try:
            if response.params and 'timeMin' in response.params:
                parse(response.params['timeMin'])

            if response.params and 'timeMax' in response.params:
                parse(response.params['timeMax'])

            if response.body and 'start' in response.body:
                parse(response.body['start']['dateTime'])

            if response.body and 'end' in response.body:
                parse(response.body['end']['dateTime'])

        except ParserError:
            raise Exception("Time in the params invalid.")



    def check_response_not_empty(self, response: list[APICall]):
        if len(response) == 0:
            raise Exception("Email instruction invalid, thus response is empty.")
    

    def check_api_in_whitelist(self, request: APICall):
        req = (request.method, request.api)
        if not req in ValidationConfiguration.api_whitelist:
            raise Exception("API call not allowed.")
        

    def check_resource_id_is_related(self, response: APICall):
        # Check for delete calendar event
        if APICall.api == "https://www.googleapis.com/calendar/v3/calendars/primary/events/eventId":
            thread_id = APICall.thread_id
            _, id = EmailService.get_related_history(thread_id)
            resource_id = APICall.params["eventId"]
            if id != resource_id: 
                raise Exception("Target event is not created by this thread.")
        # Check for delete file
        elif APICall.api == "https://www.googleapis.com/drive/v2/files/fileId":
            thread_id = APICall.thread_id
            _, id = EmailService.get_related_history(thread_id)
            resource_id = APICall.params["fileId"]
            if id != resource_id: 
                raise Exception("Target file is not created by this thread.")
        

    

def is_valid_date(date):
    if not date:
        return False
    try:
        parse(date)
        return True
    except ParserError:
        return False