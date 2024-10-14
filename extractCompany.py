# import json
# with open('resulttt.json', 'r') as f:
#     data = json.load(f)
# print(data['app_focused'])
# import spacy

import spacy

nlp = spacy.load("en_core_web_sm")

def extract_company_names(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "ORG"]

text = "Hi Tri!We are excited you are interested in becoming a Ninja. We have received your resume and application in regards to the open **Data/Business Analyst Summer Intern** role here at **NinjaHoldings**. We are currently reviewing applications and a member of our Talent Team will be in touch soon if there is a good match. However, if it turns out this isn't a good fit, please keep an eye on our website for future openings. We are growing like crazy and may have something better aligned for your skills in the near future.All the best,NinjaHoldings Talent Team"
companies = extract_company_names(text)
print(companies)
