from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# If modifying these scopes, delete the file token.json.
# https://mail.google.com/ allows full read-write access
SCOPES = ['https://mail.google.com/']

#Runs through the user's unread mail and trashes all of it one by one.

#credentials.json should be in the same directory, it can be obtained from
#Google Cloud by starting a new project and generating credentials.
#Otherwise, access must be granted by the owner.

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        
        currentTime = time.ctime(time.time())
        print(f'    Initialized at {currentTime}')
        
        # get a list of 50 message objects, filtered for unread mail
        unreadsRaw = service.users().messages().list(userId='me', q='is:unread', maxResults=50).execute()
        
        unreads = []
        counter = 0
        totalCounter = 0
        
        # list of message ids
        for unread in unreadsRaw['messages']:
            unreads.append(unread['id'])
        
        # loops as long as there is a next page of results
        while int(unreadsRaw['nextPageToken']) > 0:
            page_token = unreadsRaw['nextPageToken']
            # query again with next page token
            unreadsRaw = service.users().messages().list(userId='me', q='is:unread', pageToken = page_token, maxResults=50).execute()
            
            #list of message ids
            for unread in unreadsRaw['messages']:
                unreads.append(unread['id'])
            
            # attempt to report message subjects for context (this does not seem to work)
            for u in unreads:
                # mheadera = service.users().messages().get(userId = 'me', id = u, format='raw').execute()
                # mheaderb = mheadera.get('payload')
                # print(mheadera)
                # mheaders = mheaderb.get('headers')
                # for m in mheaders:
                    # if m['name'] == 'subject':
                        # print(m['value'])
                
                #trash the current message with id 'u'
                try:
                    service.users().messages().trash(userId = 'me', id = u).execute()
                    totalCounter = totalCounter + 1
                except TypeError as error:
                    print(f'Could not trash message with id {u}: {error}')
                
            #flush unreads[]
            unreads = []
            counter = counter + 1
            currentTime = time.ctime(time.time())
            print(f'    {currentTime}')
            print(f'    Cycle {counter} completed')
            print(f'    {totalCounter} emails deleted')
            
        
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')
        
    print('Fin.')
        
    


if __name__ == '__main__':
    main()


'''
RESOURCES:

Angel C Ramirez
https://stackoverflow.com/questions/60750345/gmail-api-unable-to-list-all-mails-by-labels

Ignacio Totino (for attempt at reading subject line)
https://stackoverflow.com/questions/55144261/python-how-to-get-the-subject-of-an-email-from-gmail-api

'''
