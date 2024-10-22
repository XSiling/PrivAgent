from gmail_authentication import get_gmail_service
from data import filter_message

# retrieve the messages for certain period of time
def retrieve_messages(start_timestamp = None, end_timestamp = None):
    service = get_gmail_service()

    # currently just get all the messages at a time
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messageIds = results.get('messages',[])
    messages = []
    for messageId in messageIds:
        msg = service.users().messages().get(userId='me', id=messageId['id'], format='full').execute()
        filtered_msg = filter_message(msg)
        messages.append(filtered_msg)
    return messages
