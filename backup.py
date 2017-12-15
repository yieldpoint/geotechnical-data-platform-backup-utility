#!/usr/bin/python

import csv
import datetime
import json
import logging
import os
import os.path
import requests
from requests.auth import HTTPBasicAuth
from StringIO import StringIO

try:
    from settings import *
except ImportError:
    GDP_BACKUP_FORMAT = os.environ['GDP_BACKUP_FORMAT']
    GDP_BACKUP_IS_INCREMENTIVE = os.environ['GDP_BACKUP_IS_INCREMENTIVE']
    GDP_BACKUP_HOST = os.environ['GDP_BACKUP_HOST']
    GDP_BACKUP_USER = os.environ['GDP_BACKUP_USER']
    GDP_BACKUP_PASSWORD = os.environ['GDP_BACKUP_PASSWORD']
    GDP_BACKUP_DIR = os.environ['GDP_BACKUP_DIR']
    GDP_BACKUP_STATUS_FILE = os.environ['GDP_BACKUP_STATUS_FILE']


logging.basicConfig(filename='/var/log/gdp/backup.log', level=logging.DEBUG)

auth = HTTPBasicAuth(GDP_BACKUP_USER, GDP_BACKUP_PASSWORD)
base_url = 'http://{}:8000'.format(GDP_BACKUP_HOST)
base_data_url = ('{}/instruments/{}/displacement-values/?format={}&start_timestamp={}')

files_dir = '%s/%s' % (GDP_BACKUP_DIR, datetime.datetime.now().strftime('%m-%d-%y %H:%M:%S'))
if not os.path.exists(files_dir):
    os.makedirs(files_dir)
    logging.debug("Backup folder created: %s" % files_dir)

if GDP_BACKUP_IS_INCREMENTIVE:

    if not os.path.exists(GDP_BACKUP_STATUS_FILE):
        open(GDP_BACKUP_STATUS_FILE, 'w')

    backup_status = dict()
    with open(GDP_BACKUP_STATUS_FILE, 'r+') as file:
        for row in csv.reader(file):
            if row:
                backup_status[row[0]] = row[1]
        logging.debug("Old backup_status: %s" % backup_status)

backup_status_new = []

instruments = json.loads(requests.get('{}/instruments'.format(base_url), auth=auth).text)
for instrument in instruments['data']:
    instrument_id = instrument['id']
    data_url = base_data_url.format(base_url, instrument_id, GDP_BACKUP_FORMAT, '')
    if GDP_BACKUP_IS_INCREMENTIVE:
        if instrument_id in backup_status:
            start_timestamp = backup_status[instrument_id]
            data_url = base_data_url.format(base_url, instrument_id,
                                            GDP_BACKUP_FORMAT, start_timestamp)
    logging.debug("Data url: %s" % data_url)
    data = requests.get(data_url, auth=auth).text
    if not data:
        logging.debug("No data")
        backup_status_new.append((instrument_id, start_timestamp))
        continue
    with open('%s/%s.csv' % (files_dir, instrument_id), 'w') as file:
        file.write(data)

    if GDP_BACKUP_IS_INCREMENTIVE:
        last_timestamp = list(csv.reader(StringIO(data)))[-1][0]
        backup_status_new.append((instrument_id, last_timestamp))


if GDP_BACKUP_IS_INCREMENTIVE:
    with open(GDP_BACKUP_STATUS_FILE, 'wb') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for instrument in backup_status_new:
            writer.writerow(instrument)
        logging.debug("New backup_status: %s" % backup_status_new)
