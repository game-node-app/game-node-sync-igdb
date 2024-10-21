import logging

from igdb.config import get_pika
from igdb.sync import IGDBSyncService
from time import sleep

import json

# 5 minutes
LOOP_ERROR_WAIT_TIME = 300
# 16 seconds
RUN_WAIT_TIME = 16

sync_service = IGDBSyncService()

def run():
    print(f"Starting IGDB sync job...")

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
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            print(e)
            logging.error(e, exc_info=e, stack_info=True)
            sleep(LOOP_ERROR_WAIT_TIME)
