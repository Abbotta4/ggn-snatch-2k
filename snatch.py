#!/usr/bin/python3

import sqlite3, requests, configparser
from ggn-snatch-2k import db_cursor

# Load the configuration file
try:
    with open("config.ini") as f:
        config = configparser.ConfigParser()
        config.read('config.ini')
except:
    print('Could not find a config file.')
    exit()

AUTHKEY = config['DEFAULT']['authkey']
TORRENT_PASS = config['DEFAULT']['torrent_pass']

def download_file(url, name):
    local_filename = name
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename

with db_cursor() as cursor:
    cursor.execute('''SELECT id,name FROM (SELECT id,name FROM torrents ORDER BY size LIMIT 10);''')
    tosnatch = cursor.fetchall()

base_url = 'https://gazellegames.net/torrents.php?action=download'
for f in tosnatch:
    url = '{}&id={}&authkey={}&torrent_pass={}'.format(base_url, f[0], AUTHKEY, TORRENT_PASS)
    name = f[1] + '.torrent'
    download_file(url, name)
