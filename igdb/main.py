from sync import IGDBSyncService
from time import sleep


def run():
    sync_s = IGDBSyncService()
    for games in sync_s.fetch_games():
        sync_s.send_games_to_queue(games)
        sleep(8)


if __name__ == "__main__":
    run()
