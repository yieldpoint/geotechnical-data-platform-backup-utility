#!/bin/sh

mkdir $GDP_BACKUP_DIR

echo "$GDP_BACKUP_CRON_PERIOD   /usr/local/bin/python /opt/geotechnical-data-platform-backup-utility/backup.py" >> /etc/crontabs/root

crond -f
