#!/bin/bash

# Copy logrotate config in case user has changed it
cp /home/mcc/logrotate.conf /etc/logrotate.d/

# Start cron service and background it (for rotating logs)
# See http://programster.blogspot.com/2014/01/docker-working-with-cronjobs.html
crond &

# Start Apache
#apachectl -D FOREGROUND

rm -rf /run/httpd/* /tmp/httpd*

exec /usr/sbin/apachectl -DFOREGROUND

