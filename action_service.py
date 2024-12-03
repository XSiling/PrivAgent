from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
import datetime
from data import APICall, GmailMessage, TokenExpirationPolicy
import requests
import hashlib
import time
from threading import Lock

# the service for sending API request to the destination
class ActionService:
    # the map from the stored cache with the used time and created time
    token_cache: dict
    token_expiration_policy: TokenExpirationPolicy
    token_expiration_times: int
    token_expiration_time: int

    # the lock for the token_cache as well as the token expiration policy
    token_lock: Lock

    def __init__(self):
        self.token_cache = {}
        self.token_expiration_policy = TokenExpirationPolicy.EXPIRE_IN_TIMES
        self.token_expiration_times = 1
        self.token_expiration_time = 100
        self.token_lock = Lock()

    def set_policy(self, new_token_policy: TokenExpirationPolicy, new_token_times: int, new_token_time: int):
        self.token_lock.acquire()
        self.token_expiration_policy = new_token_policy
        self.token_expiration_times = new_token_times
        self.token_expiration_time = new_token_time
        self.token_cache = {}
        self.token_lock.release()

    def is_valid_token(self, token_file_name):
        self.token_lock.acquire()
        if token_file_name not in self.token_cache.keys():
            self.token_lock.release()
            return False
        
        # if the policy is expire in times, after using, the token will automatically disappear in cache
        if self.token_expiration_policy == TokenExpirationPolicy.EXPIRE_IN_TIMES:
            if self.token_cache[token_file_name] == 0:
                self.token_cache.pop(token_file_name)
                self.token_lock.release()
                return False

            self.token_cache[token_file_name] -= 1
            if self.token_cache[token_file_name] == 0:
                self.token_cache.pop(token_file_name)
            self.token_lock.release()
            return True
        # otherwise will need to check the time range
        else:
            token_created_time = self.token_cache[token_file_name]
            current_time = int(time.time())
            if (current_time - token_created_time) <= self.token_expiration_time:
                self.token_lock.release()
                return True
            else:
                self.token_lock.release()
                return False
    
    def get_user_email_address(self, token):
        try:
            response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", params = {'access_token': token})
            user_email = response.json()["email"]
            return user_email
        except:
            print("Some error occured while fetching the user email address")
            return None
        
    def get_token(self, scopes, user_address):
        if "https://www.googleapis.com/auth/userinfo.email" not in scopes:
            scopes.append("https://www.googleapis.com/auth/userinfo.email")
        if "openid" not in scopes:
            scopes.append("openid")

        # try to match the token with previously cached token which is not expired
        token_file_name = self.get_hash_file_name(scopes, user_address)
        token_file_location = "user_tokens/" + token_file_name + ".json"
        is_valid_token = self.is_valid_token(token_file_name)
        creds = None
        if is_valid_token:
            creds = Credentials.from_authorized_user_file(token_file_location, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", scopes
                )
                creds = flow.run_local_server(port=0, timeout_seconds=120)
            
            # once has a nice credentials, store that
            with open(token_file_location, "w") as token:
                token.write(creds.to_json())

            self.token_lock.acquire()
            match self.token_expiration_policy:
                case TokenExpirationPolicy.EXPIRE_AFTER_TIME:
                    self.token_cache[token_file_name] = int(time.time())
                case TokenExpirationPolicy.EXPIRE_IN_TIMES:
                    self.token_cache[token_file_name] = self.token_expiration_times - 1
            self.token_lock.release()
        
        return creds

    def get_hash_file_name(self, scopes, user_email):
        m = hashlib.sha256()
        scopes.sort()
        scope_string = ' '.join(scopes)
        encoded_content = scope_string + user_email
        m.update(encoded_content.encode('utf-8'))
        hash_result = m.hexdigest()
        return hash_result
    
    def send_http_request(self, api_call: APICall, gmail_message: GmailMessage):
        try:
            # Get token and add to api_call
            # import pdb;pdb.set_trace()
            api_call.headers['Authorization'] = f'Bearer {self.get_token([api_call.scope], gmail_message.send_from).token}'
            
            # Call the Calendar API
            print("Calling the api")
            match api_call.method:
                case 'GET':
                    response = requests.get(api_call.api, params=api_call.params, headers=api_call.headers)
                case 'POST':
                    response = requests.post(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'PUT':
                    response = requests.put(api_call.api, params=api_call.params, headers=api_call.headers, json=api_call.body)
                case 'DELETE':
                    response = requests.delete(api_call.api, params=api_call.params, headers=api_call.headers)
            print(response.text)
            return response
        except Exception as error:
            print(f"An error occurred: {error}")