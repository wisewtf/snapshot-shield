#!/bin/sh

# Update cron schedule dynamically
echo "$CRON_SCHEDULE /usr/local/bin/python3 /app/script.py >> /var/log/cron.log 2>&1" > /etc/crontabs/root

# Start cron in the foreground
crond -f