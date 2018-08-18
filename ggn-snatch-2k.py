#!/usr/bin/python3

import requests, json, configparser, sqlite3, time

# Load the configuration file
try:
    with open("config.ini") as f:
        config = configparser.ConfigParser()
        config.read('config.ini')
except:
    print('Could not find a config file.')
    exit()

BASEURL = config['DEFAULT']['baseurl']
API_KEY = config['DEFAULT']['api_key']
START_ID = config['DEFAULT']['start_id']
END_ID = config['DEFAULT']['end_id']

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

for id in range(int(START_ID), int(END_ID)):
    time.sleep(2)
    url = BASEURL + 'api.php?request=torrent&id=' + str(id) + '&key=' + API_KEY
    r = requests.get(url)
    print('id: ' + str(id) + ' ' + r.json()['status'].upper())
    if r.json()['status'] == 'success':
        j = r.json()['response']['torrent']
        with db_cursor() as cursor:
            cursor.execute('''REPLACE INTO torrents (id, name, size) VALUES (?, ?, ?)''', (id, j['releaseTitle'], j['size']))
