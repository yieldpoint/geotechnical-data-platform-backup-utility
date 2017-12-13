#!/usr/bin/python

import csv
import datetime
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from StringIO import StringIO

from settings import *

auth = HTTPBasicAuth(USER, PASSWORD)
base_url = 'http://{}:8000'.format(HOST)
base_data_url = ('{}/instruments/{}/displacement-values/?format={}&start_timestamp={}')

files_dir = '%s/%s' % (BACKUP_DIR, datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'))
if not os.path.exists(files_dir):
    os.makedirs(files_dir)

backup_status = dict()
with open('backup_status.csv') as file:
    for row in csv.reader(file):
        backup_status[row[0]] = row[1]

backup_status_new = []

instruments = json.loads(requests.get('{}/instruments'.format(base_url), auth=auth).text)
for instrument in instruments['data']:
    instrument_id = instrument['id']
    data_url = base_data_url.format(base_url, instrument_id, FORMAT, '')
    if INCREMENTIVE:
        if instrument_id in backup_status:
            start_timestamp = backup_status[instrument_id]
            data_url = base_data_url.format(base_url, instrument_id, FORMAT, start_timestamp)
    data = requests.get(data_url, auth=auth).text
    with open('%s/%s.csv' % (files_dir, instrument_id), 'w') as file:
        file.write(data)

    if INCREMENTIVE:
        last_timestamp = list(csv.reader(StringIO(data)))[-1][0]
        backup_status_new.append((instrument_id, last_timestamp))

with open('backup_status.csv', 'wb') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
    for instrument in backup_status_new:
        writer.writerow(instrument)
