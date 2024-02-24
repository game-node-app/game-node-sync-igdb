import logging

from sync import IGDBSyncService
from time import sleep

# 12 hours
LOOP_WAIT_TIME = 43200
LOOP_ERROR_WAIT_TIME = 360

RUN_WAIT_TIME = 8


def run():
    sync_s = IGDBSyncService()
    for games in sync_s.fetch_games():
        sync_s.send_games_to_queue(games)
        sleep(RUN_WAIT_TIME)


if __name__ == "__main__":
    # Homemade cronjob, works until it doesn't
    # Use while I figure out why crontab -f is not working :)
    while True:
        try:
            run()
            sleep(LOOP_WAIT_TIME)
        except Exception as e:
            logging.error(e)
            sleep(LOOP_ERROR_WAIT_TIME)
