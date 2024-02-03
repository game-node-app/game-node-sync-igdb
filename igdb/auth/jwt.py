from config import get_redis_connection, SingletonMeta
from supertokens_python.recipe.jwt import syncio as jwt
from supertokens_python.recipe.jwt.interfaces import CreateJwtOkResult


class JwtService(metaclass=SingletonMeta):
    """
    This class is responsible for creating and refreshing JWT tokens.
    Ideally, it's work should only happen at app/script startup, since Supertokens microservice JWTs have infinite lifetime.
    """

    __JWT_CACHE_KEY = "jwt-token"

    def _get_jwt_from_cache(self):
        with get_redis_connection() as redis:
            jwt_token = redis.get(self.__JWT_CACHE_KEY)
            if isinstance(jwt_token, bytes):
                return jwt_token.decode("utf-8")

            return jwt_token

    def _set_jwt_to_cache(self, token: str):
        with get_redis_connection() as redis:
            redis.set(self.__JWT_CACHE_KEY, token)

    def _refresh_jwt(self):
        jwt_response = jwt.create_jwt(
            {"source": "microservice"},
        )
        if isinstance(jwt_response, CreateJwtOkResult):
            self._set_jwt_to_cache(jwt_response.jwt)
            return jwt_response.jwt
        else:
            raise Exception(
                "Failed to create JWT. Check env variables for possible issues."
            )

    def get_jwt(self):
        token = self._get_jwt_from_cache()
        if token is None:
            print("token is none")
            token = self._refresh_jwt()
        print(token)
        return token
