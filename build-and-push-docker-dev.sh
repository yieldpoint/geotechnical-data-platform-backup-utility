#!/bin/sh

docker build --no-cache -t gdp_backup .
docker tag gdp_backup updates.yieldpoint.com:5000/gdp_backup
docker push updates.yieldpoint.com:5000/gdp_backup
#docker tag gdp_backup yieldpointadmin/gdp_backup
#docker push yieldpointadmin/gdp_backup
