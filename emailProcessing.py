#import getRawEmails
import json
import base64
import re
import datetime
from collections import defaultdict
from bs4 import BeautifulSoup

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
                if "data" in sender["payload"]["body"]:
                    decoder = base64.urlsafe_b64decode(sender["payload"]["body"]["data"].encode("ASCII")).decode("utf-8")
                    senders[s_sender["value"]].append((sender["id"], sender["labelIds"], decoder, sender["internalDate"]))
                elif "data" in sender["payload"]["parts"][0]["body"]:
                        decoder = base64.urlsafe_b64decode(sender["payload"]["parts"][0]["body"]["data"].encode("ASCII")).decode("utf-8")
                        senders[s_sender["value"]].append((sender["id"], sender["labelIds"], decoder, sender["internalDate"]))
    
    return senders

def clean_text(message):
    """
    Take a string and remove all non-ASCII characters and replace them with empty string.
    """
    
    return re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff\n\r\xa0\ud83d\ude80\u202f\u2019\u2014\u2605\u2022\u2023\u2024\u034f\u00a9\u00ae\t]', '', BeautifulSoup(message, "lxml").text)

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
        for mailId, mailCategories, mailContent, mailTime in email_data:
            if "CATEGORY_PERSONAL" in mailCategories or "CATEGORY_UPDATES" in mailCategories or "IMPORTANT" in mailCategories or company == 'Stephen Luong <stephenluong24@gmail.com>':
                newMailContent = clean_text(mailContent)     
                newMailTime = datetime.datetime.fromtimestamp(int(mailTime)/1e3)
                application[company].append([mailId, mailCategories, newMailContent, str(newMailTime)])
            else:
                newMailContent = clean_text(mailContent)
                newMailTime = datetime.datetime.fromtimestamp(int(mailTime)/1e3)
                non_application[company].append([mailId, mailCategories, newMailContent, str(newMailTime)])

    #Move unnecessary emails from application focused list non-application list
    temp_list_app = [company for company in application.keys()]
    temp_list_non_app = [company for company in non_application.keys()]
    for i in temp_list_non_app:
        if i in application.keys():
            non_application[i] = application[i]
            del application[i]
    combine_list["app_focused"] = application
    combine_list["non_app_focused"] = non_application
    
    return combine_list
    
if __name__ == "__main__":
    combine_list = application_categorizer(emailProcessing(data))
    
    with open('categorizer.json', 'w') as f:
        json.dump(combine_list, f, indent=4)
    
    print(f'Data saved to categorizer.json')