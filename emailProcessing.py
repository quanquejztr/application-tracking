import getRawEmails
import json
from collections import defaultdict
import base64

''' Email is group by sender, with id, labelIds, snippet, internalDate
internalDate should be converted from Unix Epoch to Human date
'''
with open('RawEmails.json', 'r') as f:
    data = json.load(f)

def emailProcessing(emails):
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
                
    return {"output": senders}

with open('my_result.json', 'w') as json_file:
    json.dump(emailProcessing(data), json_file, indent=4)