from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
from collections import Counter


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Grab emails from given category (label)
    extract sender info in headers (From) 
    and dump list along with occurrences in a text file
    Code for login is pasted from quickstart.py located at https://developers.google.com/gmail/api/quickstart/python

    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    
    ## get list of senders for messages with label CATEGORY_PROMOTIONS
    print (datetime.datetime.now(),'Start collecting messages ...')
    label = 'CATEGORY_SOCIAL'
    results = service.users().messages().list(labelIds=label, userId='me', maxResults=1000).execute()
    messages = results.get('messages', [])
    nextPageToken = results.get('nextPageToken')

    while (nextPageToken):
        results2 = service.users().messages().list(labelIds=label, userId='me', pageToken=nextPageToken, maxResults=1000).execute()
        messages = messages + results2.get('messages', [])
        nextPageToken = results2.get('nextPageToken')

    print (datetime.datetime.now(),'End collecting messages ...')
    if not messages:
        print('Error')
    else:
        print(datetime.datetime.now(),'Collecting data from message headers using get (can take a while) ...')
        i = 0
        senders =[]
        for message in messages:
            i+=1
            content = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders='From').execute()
            headers = content['payload']['headers']
            newone = [header['value'] for header in headers]
            senders.append(newone[0])
            
        print('Total number of messages : ', i)
        print (datetime.datetime.now(),'Finished collecting header From ... Starting to count occurences')
        unique_senders=Counter(senders).most_common()
        print (unique_senders)  # unique_senders is a list of tuples

        print (datetime.datetime.now(),'Finished counting occurences ... Writing to file') 
        filename = 'results_'+ label + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M") +'.txt'
        with open (filename, 'w') as wf:
            wf.write('\n'.join('%s %s' % item for item in unique_senders))
        print (datetime.datetime.now(),'Finished writing to file')
            
if __name__ == '__main__':
    main()