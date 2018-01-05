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
# turn off unnecessary logs
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

auth = HTTPBasicAuth(GDP_BACKUP_USER, GDP_BACKUP_PASSWORD)
base_url = 'http://{}:8000'.format(GDP_BACKUP_HOST)
base_data_url = ('{}/instruments/{}/displacement-values/?format={}&start_timestamp={}')


logging.info('--------------------------------------------------------------')
files_dir = '%s/%s' % (GDP_BACKUP_DIR, datetime.datetime.now().strftime('%m%d%y%H%M%S'))
if not os.path.exists(files_dir):
    os.makedirs(files_dir)
    logging.debug("Backup folder created: %s" % files_dir)

if GDP_BACKUP_IS_INCREMENTIVE:

    # create file if it doesn't exist
    if not os.path.exists(GDP_BACKUP_STATUS_FILE):
        open(GDP_BACKUP_STATUS_FILE, 'w')

    # read backup status file
    backup_status = dict()
    with open(GDP_BACKUP_STATUS_FILE, 'r+') as file:
        for row in csv.reader(file):
            if row:
                backup_status[row[0]] = row[1]
        logging.debug("Old backup_status: %s" % backup_status)

# dict for a new backup status file after this run
backup_status_new = dict()

instruments = json.loads(requests.get('{}/instruments'.format(base_url), auth=auth).text)
for instrument in instruments['data']:
    instrument_id = instrument['id']
    start_timestamp = ''
    # url without start_timestamp so it backs up ALL data
    data_url = base_data_url.format(base_url, instrument_id, GDP_BACKUP_FORMAT, '')
    if GDP_BACKUP_IS_INCREMENTIVE:
        if instrument_id in backup_status:
            start_timestamp = backup_status[instrument_id]
            # url for incrementive backup with start_timestamp specified, it rewrites prev url
            data_url = base_data_url.format(base_url, instrument_id,
                                            GDP_BACKUP_FORMAT, start_timestamp)
    logging.debug("Data url: %s" % data_url)
    data = requests.get(data_url, auth=auth).text

    # if last timestamp is different it'll get rewritten down below
    if start_timestamp:
        backup_status_new[instrument_id] = start_timestamp

    if not data:
        logging.debug("No data")
        continue

    # data string to data list to be able to manipulate data
    data_list = list(csv.reader(StringIO(data)))

    if GDP_BACKUP_IS_INCREMENTIVE:
        # first timestamp might be a repetition of the last timestamp from previous run
        # note: the first row is a header
        first_timestamp = data_list[1][0]
        if first_timestamp == start_timestamp:
            # if there is only a header and one row of data with repetition
            if len(data_list) == 2:
                continue
            data_list_new = data_list[0]
            data_list_new += data_list[2:]
            data_list = data_list_new

        # write the last timestamp to know where to start next time
        backup_status_new[instrument_id] = data_list[-1][0]

    # write data to csv file
    with open('%s/%s.csv' % (files_dir, instrument_id), 'w') as file:
        writer = csv.writer(file)
        writer.writerows(data_list)

# capture updated backup status file
if GDP_BACKUP_IS_INCREMENTIVE:
    with open(GDP_BACKUP_STATUS_FILE, 'wb') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for instrument_id, timestamp in backup_status_new.iteritems():
            writer.writerow((instrument_id, timestamp))
        logging.debug("New backup_status: %s" % backup_status_new)
