"""mse_ctl.api.auth module."""

import calendar
from datetime import datetime, timezone
from importlib.metadata import version

import jwt
import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from requests.sessions import Session
from urllib3.util import Retry


class AccessTokenAuth(AuthBase):
    """AccessTokenAuth class derived from AuthBase."""

    def __init__(self, access_token: str):
        """Init constructor of AccessTokenAuth."""
        self.access_token: str = access_token
        self.exp: int = int(
            jwt.decode(self.access_token,
                       options={"verify_signature": False})["exp"])
        self.version = version("cosmian_secure_computation_client")

    def __call__(self, r):
        """Call used by `Session.request()` method."""
        r.headers["Authorization"] = f"Bearer {self.access_token}"
        r.headers["User-Agent"] = f"cscc-python/{self.version}"

        return r


class Connection(Session):
    """Connection class derived from Session.

    Encapsulate URL and access token for all type of requests.

    Parameters
    ----------------
    base_url : str
        Base URL of the connection.
    refresh_token : str
        Refresh Token used to get an Access Token.

    Attributes
    -----------
    base_url : str
        Base URL of the connection.
    refresh_token : str
        Refresh Token used to get an Access Token.
    auth : AccessTokenAuth
        Class to auto include authorization bearer.

    """

    class AccessToken:
        """AccessToken subclass."""

        @staticmethod
        def auto_refresh(func):
            """Refresh access token depending on expiration time."""

            def wrapper(obj, *args, **kwargs):
                """Wrap `func` method."""
                current_unix_timestamp: int = calendar.timegm(
                    datetime.now(tz=timezone.utc).timetuple())
                if current_unix_timestamp >= obj.auth.exp - 1000:
                    obj.refresh()

                return func(obj, *args, **kwargs)

            return wrapper

    def __init__(self, base_url: str, refresh_token: str) -> None:
        """Init constructor of Connection."""
        self.base_url: str = base_url
        self.refresh_token: str = refresh_token

        assert self.base_url, "URL must be provided!"
        assert self.refresh_token, "Refresh token must be provided!"

        super().__init__()

        access_token: str = get_access_token(self.base_url, self.refresh_token)
        self.auth: AccessTokenAuth = AccessTokenAuth(access_token)
        retry = Retry(
            total=5,
            read=5,
            connect=5,
            backoff_factor=0.3,
            status_forcelist=(
                502, 503),  # BadGateway from Nginx / Temporary unavailable
            allowed_methods=None,
            raise_on_status=False,
            raise_on_redirect=False)
        adapter = HTTPAdapter(max_retries=retry)
        self.mount("http://", adapter)
        self.mount("https://", adapter)

    def refresh(self) -> None:
        """Fetch new access token."""
        assert self.auth, "No auth found in session, can't connect!"

        self.auth.access_token = get_access_token(self.base_url,
                                                  self.refresh_token)

    @AccessToken.auto_refresh
    def get(self, url: str, **kwargs) -> Response:
        """Override method of `Session`."""
        kwargs.setdefault("allow_redirects", True)
        return self.request("GET",
                            f"{self.base_url}{url}",
                            auth=self.auth,
                            **kwargs)

    @AccessToken.auto_refresh
    def options(self, url: str, **kwargs) -> Response:
        """Override method of `Session`."""
        kwargs.setdefault("allow_redirects", True)
        return self.request("OPTIONS",
                            f"{self.base_url}{url}",
                            auth=self.auth,
                            **kwargs)

    @AccessToken.auto_refresh
    def head(self, url: str, **kwargs) -> Response:
        """Override method of `Session`."""
        kwargs.setdefault("allow_redirects", False)
        return self.request("HEAD",
                            f"{self.base_url}{url}",
                            auth=self.auth,
                            **kwargs)

    @AccessToken.auto_refresh
    def post(self, url: str, data=None, json=None, **kwargs) -> Response:
        """Override method of `Session`."""
        return self.request("POST",
                            f"{self.base_url}{url}",
                            data=data,
                            json=json,
                            auth=self.auth,
                            **kwargs)

    @AccessToken.auto_refresh
    def put(self, url: str, data=None, **kwargs) -> Response:
        """Override method of `Session`."""
        return self.request("PUT",
                            f"{self.base_url}{url}",
                            data=data,
                            auth=self.auth,
                            **kwargs)

    @AccessToken.auto_refresh
    def patch(self, url: str, data=None, **kwargs) -> Response:
        """Override method of `Session`."""
        return self.request("PATCH",
                            f"{self.base_url}{url}",
                            data=data,
                            auth=self.auth,
                            **kwargs)

    @AccessToken.auto_refresh
    def delete(self, url: str, **kwargs) -> Response:
        """Override method of `Session`."""
        return self.request("DELETE",
                            f"{self.base_url}{url}",
                            auth=self.auth,
                            **kwargs)


def get_access_token(url: str, refresh_token: str) -> str:
    """Fetch new access token from `refresh_token`."""
    r: Response = requests.post(url=f"{url}/oauth/token",
                                json={
                                    "type": "refresh_token",
                                    "refresh_token": refresh_token,
                                },
                                timeout=30)

    if not r.ok:
        raise Exception(
            f"Can't get access token! Status {r.status_code}: {r.content!r}")

    return r.json()["access_token"]
