import sys
import typing
from hashlib import sha1
from typing import Union

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal


class FlaskSigner:
    def __init__(
        self,
        secret_key: Union[str, bytes],
        salt: bytes = b"cookie-session",
        signer_kwargs: dict = {
            "key_derivation": "hmac",
            "digest_method": sha1,
        },
    ) -> None:
        self.serializer = URLSafeTimedSerializer(
            secret_key=secret_key if isinstance(secret_key, bytes) else secret_key.encode("utf-8"),
            salt=salt,
            signer_kwargs=signer_kwargs,
        )

    def sign(
        self,
        value: Union[str, bytes],
    ) -> str:
        return self.serializer.dumps(value)

    def unsign(
        self,
        signed_value: Union[str, bytes],
    ):
        return self.serializer.loads(signed_value)


class FlaskSessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: typing.Union[str, Secret],
        session_cookie: str = "session",
        max_age: typing.Optional[int] = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
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
        self.serializer = URLSafeTimedSerializer(
            secret_key=secret_key if isinstance(secret_key, bytes) else secret_key.encode("utf-8"),
            salt=salt,
            signer_kwargs=signer_kwargs,
        )
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True
        session_initial = {}

        if self.session_cookie in connection.cookies:
            data = connection.cookies[self.session_cookie].encode("utf-8")
            try:
                session = self.serializer.loads(data)
                session_initial = session.copy()
                scope["session"] = session
                initial_session_was_empty = False
            except BadSignature:
                scope["session"] = {}
        else:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"] and scope["session"] == session_initial:
                    ...
                    # Session data is not changed.
                elif scope["session"] and scope["session"] != session_initial:
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
                elif not initial_session_was_empty:
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
            await send(message)

        await self.app(scope, receive, send_wrapper)