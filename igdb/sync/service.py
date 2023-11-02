import os
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict
from retry import retry

from auth import IGDBAuthService, JwtService
from config import SingletonMeta
import requests

load_dotenv()

IGDB_FIELDS = [
    "id",
    "name",
    "slug",
    "checksum",
    "aggregated_rating",
    "aggregated_rating_count",
    "status",
    "summary",
    "storyline",
    "url",
    "screenshots.*",
    "game_modes.*",
    "expanded_games.id",
    "expanded_games.name",
    "expanded_games.slug",
    "category",
    "genres.*",
    "platforms.*",
    "dlcs.id",
    "dlcs.name",
    "dlcs.slug",
    "expansions.id",
    "expansions.name",
    "expansions.slug",
    "similar_games.id",
    "similar_games.name",
    "similar_games.slug",
    "cover.*",
    "artworks.*",
    "collection.*",
    "alternative_names.*",
    "external_games.*",
    "franchises.*",
    "keywords.*",
    "game_localizations.*",
    "language_supports.*",
    "first_release_date",
]

ITEMS_PER_PAGE = 500

IGDB_GAMES_ENDPOINT = "https://api.igdb.com/v4/games"


class IGDBSyncService(metaclass=SingletonMeta):
    __igdb_auth_service = IGDBAuthService()
    __jwt_token_service = JwtService()

    def __init__(self):
        pass

    def __build_request_params(self, offset: int) -> Dict:
        auth_token = self.__igdb_auth_service.get_token()
        fields_values = ", ".join(IGDB_FIELDS)

        request_params = {
            "headers": {
                "Client-ID": os.environ.get("TWITCH_CLIENT_ID"),
                "Authorization": f"Bearer {auth_token}",
            },
            "data": f"fields {fields_values}; offset {offset}; limit {ITEMS_PER_PAGE};",
        }
        return request_params

    @retry(tries=3, delay=10, backoff=2)
    def fetch_games_interval(self, offset: int):
        request_params = self.__build_request_params(offset)
        response = requests.post(IGDB_GAMES_ENDPOINT, **request_params)
        return response.json()

    def fetch_games(self):
        has_next_page = True
        current_offset = 0
        while has_next_page:
            response = self.fetch_games_interval(current_offset)
            current_offset += ITEMS_PER_PAGE
            has_next_page = len(response) > 0
            yield response

    def __send_chunk_to_queue(self, chunk: List[Dict], jwt_token: str):
        api_domain = os.environ.get("DOMAIN_API")
        queue_path = f"{api_domain}/v1/game/queue"
        parameters = {
            "url": queue_path,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {jwt_token}",
            },
            "json": {"games": chunk},
        }
        requests.post(
            **parameters,
        )

    def send_games_to_queue(self, games: List[Dict]):
        jwt_token = self.__jwt_token_service.get_jwt()
        # Split games into chunks of 10, to avoid overloading the queue
        chunk_size = 10
        chunks = [games[i : i + chunk_size] for i in range(0, len(games), chunk_size)]
        for chunk in chunks:
            try:
                self.__send_chunk_to_queue(chunk, jwt_token)
            except Exception as e:
                print(f"Failed to send chunk to queue: {e}")
                continue

        print(f"Sent {len(games)} games to queue at {datetime.utcnow()}")
