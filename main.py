import logging
import os

from igdb.auth.jwt import JWTService
from igdb.sync import IGDBSyncService
from time import sleep
import requests

import json

# 5 minutes
LOOP_ERROR_WAIT_TIME = 300
# 16 seconds
RUN_WAIT_TIME = 16

sync_service = IGDBSyncService()
jwt_service = JWTService()

def run():
    print(f"Starting IGDB sync job...")
    jwt = jwt_service.get_jwt()
    server_url = os.environ.get("SERVER_URI", "http://localhost:5000")
    sync_url = f"{server_url}/v1/sync/igdb"

    for games in sync_service.fetch_games():
        requests.post(sync_url, json=games, headers={"Authorization": f"Bearer {jwt}"})
        print(f"Successfully sent {len(games)} games to server.")
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
