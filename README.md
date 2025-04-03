# Snapshot Shield

Simple script to check virtual machine snapshots in a VMware Cluster running VCenter. This script must be run either using `cron` or `systemd-timers`. At the specified time, if any snapshot is found a table is created and sent to a Mattermost channel of your choosing, with an output similar to this:

| VM Name | VM MoID | Snapshot Name | Snapshot MoID | Creation Time | Snapshot Count |
|---------|---------|----------------|----------------|----------------|-----------------|
| VM1 | vm-1234 | I FORGOT ABOUT THIS SNAPSHOT 5 YEARS AGO | snapshot-1234 | 2025-03-27 15:07:44 | 100 |
| VM2 | vm-1235 | VEEAM LEFT THIS DANGLING SNAPSHOT FOR 7 MONTHS | snapshot-1234 | 2025-03-26 11:02:55 | 150 |

Mattermost is my use-case, but the script can easily be adjusted for any chat using webhooks which supports a simple payload post request. It must support markdown tables. I considered introducing `Apprise` but I gave up when I realized stuff like Teams do not support tables. So, your milage may vary.

Here's an example set-up using `systemd-timers`, *you may want to not run it as **root***:

```plaintext
# /etc/systemd/system/snapshotshield.timer

[Unit]
Description=Timer to run Snapshotshield

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```plaintext
# /etc/systemd/system/snapshotshield.service

[Unit]
Description=Runs headless snapshotshield's bash script

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/snapshotshield_auto.py
User=root
```

This will run every day at 8AM.

A Dockerfile is provided. It will build an Alpine Linux image and run the script with `crond`. The default is also every day at 8AM.

You can run the Docker with the provided `docker-compose.yml` or using this command:

```bash
docker run -d --name snapshot-shield --network host -v /home/t1adm_p3mh/snapshotshield/config.toml:/app/config.toml snapshot-shield
```

You can specify `-e CRON_SCHEDULE="* * * * *"` to change the scheduling to your liking using `cron`'s format.

`--network host` was convenient for me, but depending on your network requirements you might change it however you like.
