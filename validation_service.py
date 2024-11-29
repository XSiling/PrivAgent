from data import APICall, ValidationConfiguration, HTTPMethod
from dateutil.parser import parse, ParserError

class ValidationService:
    def validate_response(self, response: list[APICall]):
        self.check_response_not_empty(response)

        for api_call in response:
            self.check_api_in_whitelist(api_call)
            self.check_valid_params(api_call)


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
        

    

def is_valid_date(date):
    if not date:
        return False
    try:
        parse(date)
        return True
    except ParserError:
        return False