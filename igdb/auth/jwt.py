from igdb.config import SingletonMeta, get_redis_connection, supertokens_init
from supertokens_python.recipe.jwt.syncio import create_jwt
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult

class JWTService(metaclass=SingletonMeta):
    _JWT_TOKEN_CACHE_KEY = "ms-jwt-token"
    _JWT_TOKEN_EXPIRE_TIME_SECONDS = 86400 # 24 hours

    def __init__(self):
        supertokens_init()

    def _get_token_from_store(self) -> str:
        with get_redis_connection() as redis:
            # While this returns an Awaitable, it runs synchronously here.
            token_on_store = redis.get(self._JWT_TOKEN_CACHE_KEY)
            if isinstance(token_on_store, bytes):
                return token_on_store.decode("utf-8")

            return token_on_store

    def _set_token_to_store(
            self, token: str
    ) -> None:
        with get_redis_connection() as redis:
            redis.set(self._JWT_TOKEN_CACHE_KEY, token, ex=self._JWT_TOKEN_EXPIRE_TIME_SECONDS)


    def _generate_jwt(self):
        jwt_response = create_jwt({
            "source": "microservice",
        })

        if isinstance(jwt_response, CreateJwtOkResult):
            jwt = jwt_response.jwt
            self._set_token_to_store(jwt)

            return jwt

        else:
            raise Exception("Unable to create JWT. Should never come here.")

    def get_jwt(self):
        token_in_store = self._get_token_from_store()

        if token_in_store is not None:
            return token_in_store

        return self._generate_jwt()