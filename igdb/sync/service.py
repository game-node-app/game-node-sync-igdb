import os
from datetime import datetime
from typing import Dict, List

from dotenv import load_dotenv
from retry import retry

from igdb.auth import IGDBAuthService
from igdb.config import SingletonMeta
import requests
import logging

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
    "themes.*",
    "player_perspectives.*",
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
    "involved_companies.*",
    "involved_companies.company.*",
    "involved_companies.company.logo.*",
    "game_engines.*",
    "game_engines.platforms.*",
    "game_engines.companies.*",
    "game_engines.companies.logo.*",
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

LAST_USED_OFFSET = None


class IGDBSyncService(metaclass=SingletonMeta):
    __igdb_auth_service = IGDBAuthService()

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
        # Fallback to return to previous attempt when errors occur
        global LAST_USED_OFFSET
        if LAST_USED_OFFSET is not None:
            current_offset = LAST_USED_OFFSET

        while has_next_page:
            print(f"Current offset: {current_offset}")
            response = self.fetch_games_interval(current_offset)
            print(f"Fetched {len(response)} entries")
            current_offset += ITEMS_PER_PAGE
            LAST_USED_OFFSET = current_offset
            has_next_page = len(response) > 0 and len(response) >= ITEMS_PER_PAGE
            if not has_next_page:
                print(f"Detected last page of results at offset: {current_offset}")
                LAST_USED_OFFSET = None
            yield response
