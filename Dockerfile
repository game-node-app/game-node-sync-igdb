FROM python:3.8

RUN apt-get update && apt-get -y install cron vim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY crontab /etc/cron.d/crontab

RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab

COPY . .

RUN echo $PYTHONPATH