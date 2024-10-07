import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.labels"]


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    all_messages = []
    next_page_token = None

    # Fetch emails page by page
    while True:
        if next_page_token:
            result = service.users().messages().list(userId='me', pageToken=next_page_token).execute()
        else:
            result = service.users().messages().list(userId='me').execute()

        messages = result.get('messages', [])
        all_messages.extend(messages)

        # Check if there's another page of results
        next_page_token = result.get('nextPageToken')
        if not next_page_token:
            break

    # Fetch full email details for each message
    full_messages = []
    for message in all_messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format = 'full').execute()
        full_messages.append(msg)

    # Save the full messages to a JSON file
    with open('RawEmails.json', 'w') as json_file:
        json.dump(full_messages, json_file, indent=4)

    print(f"File saved to RawEmails.json")

main()