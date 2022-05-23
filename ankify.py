import sqlite3
import sys
import json
import urllib.request

con1 = ""
try: 
    con1 = sqlite3.connect('/Volumes/Kindle/system/vocabulary/vocab.db')
except:
    print("kindle not connected")
    sys.exit()

cur1 = con1.cursor()
tables = [x for x in cur1.execute("SELECT name FROM sqlite_master")]

if not tables: 
    print("kindle not connected")
    sys.exit()

con2 = sqlite3.connect('./Dictionary.db')
cur2 = con2.cursor()

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        if response['error'] != 'cannot create note because it is a duplicate':
            raise Exception(response['error'])
        return None
    return response['result']

note = {
        "deckName": "vocab",
        "modelName": "Basic",
        "fields": {
            "Front": "front content1",
            "Back": "back content"
            },
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "deck",
            },
        "tags": []
        }
        
invoke('createDeck', deck='vocab')

all_words = [a for a in cur1.execute("SELECT word FROM 'WORDS'")]
vocab = {}
words_slice = all_words[0:200] # need to fix this, for some reason query breaks with full slice 

for w in words_slice:
    defs = [a for a in cur2.execute(f"SELECT  definition FROM entries WHERE word='{w[0]}'")]
    if defs:
        for d in defs:
            clean_def = d[0].replace("\n","").replace("   ", " ")
            vocab.setdefault(w[0], [] ).append(clean_def)

for key, value in vocab.items():
    cleaned = '\n\n'.join(value)
    note['fields']['Front'] = key.lower()
    note['fields']['Back'] = cleaned
    response = invoke('addNote', note=note)
    if response is not None:
        print(key.lower())

con1.close()
con2.close()


