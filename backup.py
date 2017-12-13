#!/usr/bin/python

import json
import requests
from requests.auth import HTTPBasicAuth

from settings import *

host = 'localhost'
auth = HTTPBasicAuth('yieldpoint', 'YPfuture')

base_url = 'http://%s:8000' % host

instruments = json.loads(requests.get('%s/instruments' % base_url, auth=auth).text)
for instrument in instruments['data']:
    data_url = '%s/instruments/%s/displacement-values/?format=%s' % (base_url, instrument['id'], FORMAT)
    data = requests.get(data_url, auth=auth).text
    with open('%s.csv' % instrument['id'], 'w') as file:
        file.write(data)
