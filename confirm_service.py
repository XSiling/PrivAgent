from data import LLMResponse

class ConfirmService:
    def get_confirmation(self, llm_response:LLMResponse):
        service_name = llm_response.service_name
        service_version = llm_response.service_version
        params = llm_response.params
        text = "<Action Confirmation>\nWe will try to send a request to: " + service_name.value + " with version: " + service_version + ". The params:" + str(params)
        text += ".\nIf you confirm this is correct, please input 1. Otherwise input 0 or else.\nResponse:"

        response = input(text)
        return response == "1"
        
