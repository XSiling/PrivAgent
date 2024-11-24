from data import APICall, ValidationConfiguration, HTTPMethod

class ValidationService:
    def check_response_not_empty(self, response: list[APICall]):
        if len(response) == 0:
            raise Exception("Email instruction invalid, thus response is empty.")
    
    def check_api_in_whitelist(self, request: APICall):
        req = (request.method, request.api)
        if not req in ValidationConfiguration.api_whitelist:
            raise Exception("API call not allowed.")