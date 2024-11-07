from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import datetime
from data import APICall
import requests

# the service for sending API request to the destination
class ActionService:

    def __init__(self):
        pass
    
    def send_http_request(self, api_call: APICall):
        try:
            # Call the Calendar API
            print("Calling the api")
            match api_call.method:
                case 'GET':
                    response = requests.get(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'POST':
                    response = requests.post(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'PUT':
                    response = requests.put(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'DELETE':
                    response = requests.delete(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)

            print(response.text)
        except Exception as error:
            print(f"An error occurred: {error}")