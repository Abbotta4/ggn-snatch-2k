#!/usr/bin/python3

import requests, json, ConfigParser, sqlite3

# Load the configuration file
try:
    with open("config.ini") as f:
        raw_config = f.read()
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.readfp(io.BytesIO(raw_config))
except:
    print('Could not find a config file.')

BASEURL = config.get('baseurl')
API_KEY = config.get('api_key')
END_ID = config.get('end_id')

class db_cursor:
    def __init__(self):
        self.connfile = 'torrents.db'
        self.conn = sqlite3.connect(self.connfile)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS torrents (id INT PRIMARY KEY, name TEXT, size INT)''')
    def __enter__(self):
        return self.cursor
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.cursor.close()

for id in range(1, END_ID):
    url = BASURL + 'api.php?request=torrent&id=' + str(id) + '&key=' + API_KEY
    r = requests.get(url)
    j = r.json()['response']['torrent']
    with db_cursor() as cursor:
        cursor.execute('''INSERT INTO torrents (id, name, size) VALUES (?, ?, ?)''', (id, j['releaseTitle'], j['size']))
