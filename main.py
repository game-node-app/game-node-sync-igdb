from igdb.config import get_pika
from igdb.sync import IGDBSyncService
from time import sleep

import json
import logging

# 48 hours
LOOP_WAIT_TIME = 86400 * 2
# 10 minutes
LOOP_ERROR_WAIT_TIME = 720
RUN_WAIT_TIME = 16


def run():
    sync_service = IGDBSyncService()
    with get_pika() as pika:
        for games in sync_service.fetch_games():
            pika.basic_publish(exchange="sync", routing_key="sync-igdb", body=json.dumps(games))
            print(f"Successfully sent {len(games)} games to RabbitMQ queue.")
            sleep(RUN_WAIT_TIME)


if __name__ == "__main__":
    # Homemade cronjob, works until it doesn't
    # igdb-sync doesn't check for listeners, so make sure some service is listening to these messages.
    while True:
        try:
            run()
            sleep(LOOP_WAIT_TIME)
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print(e)
            sleep(LOOP_ERROR_WAIT_TIME)
