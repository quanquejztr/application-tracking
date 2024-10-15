#import getRawEmails
import json
import base64
import re
import datetime
from collections import defaultdict
from bs4 import BeautifulSoup
from transformers import pipeline
from collections import defaultdict
from subprocess import list2cmdline
import spacy
from spacy.matcher import Matcher

"""
This code snippet is a Python script that processes raw emails. It imports various modules and defines three functions: `emailProcessing`, `clean_text`, and `application_categorizer`.

The `emailProcessing` function takes a list of raw emails and processes them into a dictionary. 
The dictionary has the sender email as the key and a list of tuples as the value. Each tuple contains the email id, labelIds, snippet, and internalDate.

The `clean_text` function takes a string and removes all non-ASCII characters and replaces them with an empty string.

The `application_categorizer` function takes a dictionary of emails grouped by sender. It categorizes the emails into two categories: "app_focused" and "non_app_focused". The "app_focused" category contains emails that are application related, while the "non_app_focused" category contains emails that are not application related.

The code snippet also includes a `with open` statement that reads a JSON file named "RawEmails.json" and loads its contents into the `data` variable.

Overall, this code snippet provides functionality for processing raw emails and categorizing them based on certain criteria.

"""

"""
To start, make sure RawEmails.json is on the repository (This is owner account).

Add any print or statement that you need to understand how a particular function works.
"""
with open('RawEmails.json', 'r') as f:
    data = json.load(f)

def emailProcessing(emails):
    """
    Take a list of raw emails, and process them into a dictionary where sender email is the key and a list of tuples containing the email id, labelIds, snippet, and internalDate is the value.
    """
    senders = defaultdict(list)
    
    for sender in emails:
        for s_sender in sender["payload"]["headers"]:
            if "From" in s_sender["name"]:
                headers = sender.get('payload', {}).get('headers', [])
                for header in headers:
                    if header.get('name', '').lower() == 'subject':
                        title = header.get('value', 'No title found')
                if "data" in sender["payload"]["body"]:
                    decoder = base64.urlsafe_b64decode(sender["payload"]["body"]["data"].encode("ASCII")).decode("utf-8")
                    senders[s_sender["value"]].append((sender["id"], sender["labelIds"], title, decoder, sender["internalDate"]))
                elif "data" in sender["payload"]["parts"][0]["body"]:
                    decoder = base64.urlsafe_b64decode(sender["payload"]["parts"][0]["body"]["data"].encode("ASCII")).decode("utf-8")
                    senders[s_sender["value"]].append((sender["id"], sender["labelIds"], title, decoder, sender["internalDate"]))
    
    return senders

def clean_text(message):
    """
    Take a string and remove all non-ASCII characters and replace them with empty string.
    """
    
    return re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff\n\r\xa0\ud83d\ude80\u202f\u2019\u2014\u2605\u2022\u2023\u2024\u034f\u00a9\u00ae\t]', '', BeautifulSoup(message, "lxml").text)

import datetime

from transformers import pipeline
from collections import defaultdict
from subprocess import list2cmdline
import spacy
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_lg')
model_checkpoint = "xlm-roberta-large-finetuned-conll03-english"
token_classifier = pipeline(
    "token-classification", model=model_checkpoint, aggregation_strategy="simple"
)

def Org_classifier(extracted_text):
    # Extract the complete text in the resume
    classifier = token_classifier(extracted_text)
    entity_name = None
    max_score = 0
    for s in classifier:
        if s['entity_group'] == 'ORG':
            if s['score'] > max_score:
                entity_name = s['word']
                max_score = s['score']
    return entity_name


def application_categorizer(content):
    """
    Take a dictionary of emails grouped by sender, with id, labelIds, content, internalDate as the value.
    Return a dictionary with two keys: "app_focused" and "non_app_focused".
    "app_focused" key will point to a dictionary of emails that are application related, with company emails as the key and a list of tuples containing the email id, labelIds, snippet, and internalDate as the value.
    "non_app_focused" key will point to a dictionary of emails that are not application related, with company emails as the key and a list of tuples containing the email id, labelIds, snippet, and internalDate as the value.
    """
    application = defaultdict(list)
    non_application = defaultdict(list)
    combine_list = defaultdict(list)
    for company, email_data in content.items():
        for mailId, mailCategories, mailSubject, mailContent, mailTime in email_data:
            newMailContent = clean_text(mailContent)   
            newMailTime = datetime.datetime.fromtimestamp(int(mailTime)/1e3)
            if ("CATEGORY_PERSONAL" in mailCategories or "CATEGORY_UPDATES" in mailCategories or "IMPORTANT" in mailCategories) and ("great fit" not in mailSubject.lower() or 
                                                                                                        "apply now" not in mailSubject.lower()):
                if any(keyword in mailSubject.lower() or keyword in newMailContent.lower() for keyword in 
                       ["application", "applications", "assessment", "assessments", 
                        "next step", "submission", "submissions", "recruiting"]):
                    application[company].append([mailId, mailCategories, mailSubject, newMailContent, str(newMailTime)])
            else:
                non_application[company].append([mailId, mailCategories, mailSubject, newMailContent, str(newMailTime)])

    
    #Move unnecessary emails from application list non-application list
    temp_list_non_app = [company for company in non_application.keys()]
    for i in temp_list_non_app:
        if i in application.keys():
            non_application[i] = application[i]
            del application[i]
    combine_list["app_focused"] = application
    combine_list["non_app_focused"] = non_application
    
    return combine_list

def gimmeAFunctionName(file):
    app_focused = file['app_focused']
    
    the_fix = defaultdict(list)
    
    for email, content in app_focused.items():
        for mailId, mailCategories, mailSubject, mailContent, mailTime in content:
            mailCorporationName = Org_classifier(mailContent)
            
            # If no company name is found, use the original email address
            if mailCorporationName is None:
                mailCorporationName = email
            
            # Add the email data under the company name
            the_fix[mailCorporationName].append([mailId, mailCategories, mailSubject, mailContent, mailTime])
    # Replace the original 'app_focused' content with the merged version
    file['app_focused'] = the_fix
    
    return file
    
if __name__ == "__main__":
    combine_list = application_categorizer(emailProcessing(data))
    
    with open('categorizer3.json', 'w') as f:
        json.dump(combine_list, f, indent=4)
    
    print(f'Data saved to categorizer.json')