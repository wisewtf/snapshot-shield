FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache curl bash openrc && \
    pip install --no-cache-dir pyVmomi requests tomli

COPY script.py /app/script.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV CRON_SCHEDULE="0 8 * * *"

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]