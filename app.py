import time
from email_receiver import retrieve_messages
from data import display_gmail_messages

# continuously running the backend server, including:
# for certain period:
#   retrieve the information
def run_server():
    while True:
        new_messages = retrieve_messages()
        display_gmail_messages(new_messages)
        time.sleep(5 * 1000)
        break
        # just run one time temporarily
        



if __name__ == '__main__':
    run_server()