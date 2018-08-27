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

def poll_api(tries, initial_delay, delay, backoff, url):
    time.sleep(initial_delay)
    for n in range(tries):
        try:
            r = requests.get(url, timeout=2)
            return r.json()
        except requests.exceptions.Timeout as e:
            polling_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            print("{0}. Sleeping for {1} seconds.".format(polling_time, delay))
            time.sleep(delay)
            delay *= backoff
        except requests.exceptions.ConnectionError as e:
            polling_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            print("{1}. Connection dropped with error code {1}".format(polling_time, e.errno))
    polling_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    raise ExceededRetries("{0}. Failed to poll {1} within {2} tries.".format(polling_time, url, tries))

for id in range(int(START_ID), int(END_ID)):
    url = BASEURL + 'api.php?request=torrent&id=' + str(id) + '&key=' + API_KEY
    j = poll_api(10, 2, 1, 2, url)
    polling_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print("{0}. ID {1} {2}".format(polling_time, id, '\033[92mSUCCESS\033[0m' if j['status'] == 'success' else '\033[91mFAILURE\033[0m'))
    if j['status'] == 'success':
        j = j['response']['torrent']
        with db_cursor() as cursor:
            cursor.execute('''REPLACE INTO torrents (id, name, size) VALUES (?, ?, ?)''', (id, j['releaseTitle'], j['size']))
