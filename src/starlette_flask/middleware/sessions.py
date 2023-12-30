import typing
from hashlib import sha1

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SessionMiddleware:
    """Starlette middleware adopting Flask's cookie-based sessions."""
    def __init__(
        self,
        app: ASGIApp,
        secret_key: typing.Union[str, Secret],
        session_cookie: str = "session",
        max_age: typing.Optional[int] = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
        domain: typing.Optional[str] = None,
        salt: bytes = b"cookie-session",
        signer_kwargs: dict = {
            "key_derivation": "hmac",
            "digest_method": sha1,
        },
    ) -> None:
        self.app = app
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"
        if domain is not None:
            self.security_flags += f"; domain={domain}"
        self.serializer = URLSafeTimedSerializer(
            secret_key=secret_key if isinstance(secret_key, bytes) else secret_key.encode("utf-8"),
            salt=salt,
            signer_kwargs=signer_kwargs,
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        session_initial = {}

        if self.session_cookie in connection.cookies:
            data = connection.cookies[self.session_cookie].encode("utf-8")
            try:
                session = self.serializer.loads(data)
                session_initial = session.copy()
                scope["session"] = session
            except BadSignature:
                scope["session"] = {}
        else:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                if not scope["session"]:
                    print("Session is empty!")
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = (
                        "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                            session_cookie=self.session_cookie,
                            data="null",
                            path=self.path,
                            expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                            security_flags=self.security_flags,
                        )
                    )
                    headers.append("Set-Cookie", header_value)
                elif scope["session"] != session_initial:
                    print("Session is changed!")
                    # Session data is changed - We have session data to persist.
                    data = self.serializer.dumps(scope["session"])
                    headers = MutableHeaders(scope=message)
                    header_value = (
                        "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                            session_cookie=self.session_cookie,
                            data=data,
                            path=self.path,
                            max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                            security_flags=self.security_flags,
                        )
                    )
                    headers.append("Set-Cookie", header_value)
                else:
                    print("Session is not changed!")
            await send(message)

        await self.app(scope, receive, send_wrapper)
