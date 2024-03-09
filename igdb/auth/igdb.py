import os
from datetime import datetime

from igdb.config import SingletonMeta, get_redis_connection
import requests
import asyncio

from igdb.interface.igdb_token_response import IGDBTokenResponse


class IGDBAuthService(metaclass=SingletonMeta):
    _IGDB_TOKEN_CACHE_KEY = "igdb-token"
    _MINIMUM_EXPIRATION_TIME_SECONDS = 259200

    def _get_token_from_store(self) -> str:
        with get_redis_connection() as redis:
            # While this returns an Awaitable, it runs synchronously here.
            token_on_store = redis.get(self._IGDB_TOKEN_CACHE_KEY)
            if isinstance(token_on_store, bytes):
                return token_on_store.decode("utf-8")

            return token_on_store

    def _set_token_to_store(
        self, token: str, expires_in: int = _MINIMUM_EXPIRATION_TIME_SECONDS
    ) -> None:
        with get_redis_connection() as redis:
            redis.set(self._IGDB_TOKEN_CACHE_KEY, token, ex=expires_in)

    def __fetch_token(self) -> IGDBTokenResponse:
        response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": os.environ.get("TWITCH_CLIENT_ID"),
                "client_secret": os.environ.get("TWITCH_CLIENT_SECRET"),
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        now = datetime.now()
        print(f"Fetched new IGDB token at {now}")
        return IGDBTokenResponse(**response.json())

    def get_token(self) -> str:
        token = self._get_token_from_store()
        if token is None:
            token_response = self.__fetch_token()
            token = token_response.access_token
            self._set_token_to_store(token)

        return token
