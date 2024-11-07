from data import APICall

class ConfirmService:
    def get_confirmation(self, llm_response:APICall):
        confirm_text = self.get_confirmation_text(llm_response)
        response = input(confirm_text)
        return response == "1"
    
    def get_confirmation_text(self, llm_response:APICall):
        api = llm_response.api
        method = llm_response.method
        params = llm_response.params
        body = llm_response.body
        text = "<Action Confirmation>\nWe will try to send a " + method + " request to: " + api + \
            ". \nThe params: " + str(params) + "\nThe body: " + str(body)
        text += ".\nIf you confirm this is correct, please input 1. Otherwise input 0 or else.\nResponse:"
        return text
        
