from fastmcp.server.auth import AccessToken, TokenVerifier


class SharedSecretVerifier(TokenVerifier):
    """Accepts a single static bearer token, shared out-of-band with trusted callers."""

    def __init__(self, token: str) -> None:
        super().__init__()
        self._token = token

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != self._token:
            return None
        return AccessToken(token=token, client_id="shared-secret", scopes=[])
