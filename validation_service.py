from data import APICall, ValidationConfiguration, HTTPMethod
from dateutil.parser import parse, ParserError
from datetime import datetime, timedelta
from email_service import EmailService

class ValidationService:
    def validate_response(self, response: list[APICall], history_resource_id: str):
        self.check_response_not_empty(response)

        for api_call in response:
            self.check_api_in_whitelist(api_call)
            self.check_essential_params(api_call)
            self.check_valid_params(api_call)
            self.check_resource_id_is_related(api_call, history_resource_id)


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

    def get_one_hour_later_datetime(self, start_time):
        end_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=1)
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        return end_time

    def check_essential_params(self, request: APICall):
        req = (request.method, request.api)
        req_index = ValidationConfiguration.api_whitelist.index(req)
        # fill in the blank parameters, if impossible then throw exception

        match req_index:
            # create_calendar_event
            # by default create on right now with 1 hour window
            case 0:
                if not request.body:
                    request.body = {}

                if 'start' not in request.body:
                    request.body['start'] = {
                        'dateTime': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        'timeZone': 'America/Los_Angeles'
                    }
                if 'end' not in request.body:
                    request.body['end'] = {
                        'dateTime': self.get_one_hour_later_datetime(request.body['start']['dateTime']),
                        'timeZone': 'America/Los_Angeles'
                    }
                if 'dateTime' not in request.body['start']:
                    request.body['start']['dateTime'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                if 'dateTime' not in request.body['end']:
                    request.body['end']['dateTime'] = self.get_one_hour_later_datetime(request.body['start']['dateTime'])
                if 'timeZone' not in request.body['start']:
                    request.body['start']['timeZone'] = 'America/Los_Angeles'
                if 'timeZone' not in request.body['end']:
                    request.body['start']['timeZone'] = 'America/Los_Angeles'
                request.params = {}

            # create_doc
            # by default with a title 
            case 1:
                if request.body and 'summary' in request.body:
                    request.body['title'] = request.body['summary']
                if request.body and 'title' in request.body:
                    title = request.body['title']
                else:
                    title = 'LLM Agent Docs'
                request.body = {
                    'title': title
                }

            # create_sheet
            # by default with a title
            case 2:
                if request.body and 'properties' in request.body and 'title' in request.body['properties']:
                    title = request.body['properties']['title']
                else:
                    title = 'LLM Agent Sheet'

                request.body = {
                    "properties":{
                        "title": title
                    }
                }

            # get_calendar_events
            # by default fetch all the events on today
            case 3:
                if 'timeMin' not in request.params:
                    request.params['timeMin'] = datetime.now().strftime("%Y-%m-%dT00:00:00Z")
                elif not request.params['timeMin'].endswith('Z'):
                    request.params['timeMin'] += 'Z'

                if 'timeMax' not in request.params:
                    request.params['timeMax'] = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
                elif not request.params['timeMax'].endswith('Z'):
                    request.params['timeMax'] += 'Z'
                
                if 'singleEvents' not in request.params:
                    request.params['singleEvents'] = True
                if 'orderBy' not in request.params:
                    request.params['orderBy'] = 'startTime'
                if 'timeZone' not in request.params:
                    request.params['TimeZone'] = 'America/Los_Angeles'

            #delete_calendar_event
            case 4:
                request.body = {}
                if not request.params or 'eventId' not in request.params:
                    raise Exception("Lack eventId in delete calendar event api request")

            # delete_file_event
            case 5:
                request.body = {}
                if 'fileId' not in request.params:
                    raise Exception("Lack fileId in delete file event")

    def check_response_not_empty(self, response: list[APICall]):
        if len(response) == 0:
            raise Exception("Email instruction invalid, thus response is empty.")
    

    def check_api_in_whitelist(self, request: APICall):
        req = (request.method, request.api)
        if not req in ValidationConfiguration.api_whitelist:
            raise Exception("API call not allowed.")
        

    def check_resource_id_is_related(self, response: APICall, history_resource_id: str):
        # Check for delete calendar event
        if response.api == "https://www.googleapis.com/calendar/v3/calendars/primary/events/eventId":
            resource_id = response.params["eventId"]
            if history_resource_id != resource_id: 
                raise Exception("Target event is not created by this thread.")
        # Check for delete file
        elif response.api == "https://www.googleapis.com/drive/v2/files/fileId":
            resource_id = response.params["fileId"]
            if history_resource_id != resource_id: 
                raise Exception("Target file is not created by this thread.")
        

    

def is_valid_date(date):
    if not date:
        return False
    try:
        parse(date)
        return True
    except ParserError:
        return False