FROM jfloff/alpine-python:2.7

RUN apk update && apk upgrade &&  \
    apk add git

RUN git clone -b master https://c9f540eaec04f7b3750d402675f07b5c2fc2f267@github.com/yieldpoint/geotechnical-data-platform-backup-utility.git /opt/geotechnical-data-platform-backup-utility/

RUN rm /opt/geotechnical-data-platform-backup-utility/settings.py

ENV GDP_BACKUP_FORMAT csv2
ENV GDP_BACKUP_IS_INCREMENTIVE true
ENV GDP_BACKUP_HOST 192.168.2.83
ENV GDP_BACKUP_USER yieldpoint
ENV GDP_BACKUP_PASSWORD YPfuture

ENV GDP_BACKUP_DIR /var/lib/gdp/backups
ENV GDP_BACKUP_STATUS_FILE /var/lib/gdp/backups/backup_status.csv

RUN pip install requests

ADD crontab /etc/cron.d/gdp-backup-cron
RUN chmod 0644 /etc/cron.d/gdp-backup-cron

CMD ["crond", "-f"]
