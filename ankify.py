import sqlite3
import sys
import json
import urllib.request

#### utilizes ankiconnect, which is a plugin for anki that exposes an REST API on port 8765

# exit if Kindle is not connected
con1 = ""
try: 
    con1 = sqlite3.connect('/Volumes/Kindle/system/vocabulary/vocab.db')
except:
    print("kindle not connected")
    sys.exit()

# exit if vocab db doesnt have any tables
cur1 = con1.cursor()
tables = [x for x in cur1.execute("SELECT name FROM sqlite_master")]
if not tables: 
    print("kindle db has no tables")
    sys.exit()

print("Adding new words from Kindle to Anki vocab deck:")

# establish connection to dictionary which is in the directory
con2 = sqlite3.connect('./dict.db')
cur2 = con2.cursor()

# request builder
def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

# ankiconnect request handler
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

# note template for addNote call; probably should make a template/data type
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
        
# create deck in Anki, will not overwrite if already exists
invoke('createDeck', deck='vocab')

# find all words from kindle vocab.db
all_words = [a for a in cur1.execute("SELECT word FROM 'WORDS'")]

# dictionary mapping words to definitions
vocab = {}

# create array if definitions for every word and add it to vocab dictionary
for w in all_words:
    word = w[0]
    word = word.replace("'", "''") # single quotes are escaped in sqlite with an additional single quote
    defs = [a for a in cur2.execute(f"SELECT definition FROM entries WHERE word='{word}'")]
    if defs:
        for d in defs:
            clean_def = d[0].replace("\n","").replace("   ", " ")
            vocab.setdefault(w[0], [] ).append(clean_def)

# create note and add to deck for every key/value pair in vocab dict; will not add duplicates
for key, value in vocab.items():
    cleaned = '\n\n'.join(value)
    note['fields']['Front'] = key.lower()
    note['fields']['Back'] = cleaned
    response = invoke('addNote', note=note)
    if response is not None:
        print(key.lower())

# close connections
con1.close()
con2.close()
