FROM python:3.8

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y cron vim

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN chmod 0644 crontab

RUN crontab crontab

#CMD ["cron","-f"]

