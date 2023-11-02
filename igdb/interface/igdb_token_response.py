class IGDBTokenResponse:
    def __init__(self, access_token: bytes, expires_in: int, token_type: str):
        self.access_token = access_token
        self.expires_in = expires_in
        self.token_type = token_type
