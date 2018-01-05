#!/bin/sh

echo "$GDP_BACKUP_CRON_PERIOD   /usr/bin/python /opt/geotechnical-data-platform-backup-utility/backup.py" >> /etc/crontabs/root

crond -f
