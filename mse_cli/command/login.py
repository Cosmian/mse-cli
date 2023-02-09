"""mse_cli.command.login module."""

import base64
import hashlib
import json
import re
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from mse_cli import (
    MSE_AUTH0_AUDIENCE,
    MSE_AUTH0_CLIENT_ID,
    MSE_AUTH0_DOMAIN_NAME,
    MSE_CONSOLE_URL,
)
from mse_cli.api.types import User
from mse_cli.api.user import me as get_me
from mse_cli.conf.user import UserConf
from mse_cli.log import LOGGER as LOG

CODE: Optional[str] = None


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "login", help="sign up or login to console.cosmian.com"
    )
    parser.add_argument(
        "--whoami", action="store_true", help="display user currently logged in"
    )

    parser.set_defaults(func=run)


def run_server(port, auth_url, state) -> str:
    """Run the server to interact with auth0."""

    class LocalHTTPRequestHandler(BaseHTTPRequestHandler):
        """Local server designed to receive the access and refresh token."""

        def log_message(self, *args):
            """Remove default logs."""
            return

        def do_GET(self) -> None:
            """GET /."""
            if not self.path.startswith("/?"):
                self.send_response(404)
                return

            query = urlparse(self.path).query
            parsed_query = parse_qs(query)

            if "code" not in parsed_query or "state" not in parsed_query:
                self.send_response(400)
                return

            if state != parsed_query["state"][0]:
                self.send_response(400)
                return

            global CODE  # pylint: disable=global-statement
            CODE = parsed_query["code"][0]
            self.send_response(301)
            self.send_header("location", f"{MSE_CONSOLE_URL}/?origin=ctl")
            self.end_headers()
            self.kill_server()

        def kill_server(self):
            """Stop the server."""
            assassin = threading.Thread(target=httpd.shutdown)
            assassin.daemon = True
            assassin.start()

    httpd = HTTPServer(("", port), LocalHTTPRequestHandler)
    # Open the browser on the authorization url to let the user login
    open_webbrowser(auth_url)
    LOG.info("Waiting for session... ")
    # Wait for the code from Auth0
    httpd.serve_forever()

    if not CODE:
        raise Exception("Authentication timeout.")

    return CODE


def run(args) -> None:
    """Run the subcommand."""
    if args.whoami:
        try:
            user_conf = UserConf.from_toml()
        except FileNotFoundError:
            LOG.error("You are not logged in yet!")
            return

        LOG.info("You are currently logged in as: %s", user_conf.email)

        try:
            me = get_user_info(user_conf)
        except NameError:
            LOG.warning(
                "Don't forget to verify your email and "
                "complete your profile before going on"
            )
        return

    # Before processing the login, let's check if the user is already logged in
    if UserConf.path().exists():
        user_conf = UserConf.from_toml()
        try:
            _ = get_user_info(user_conf)
        except NameError:
            LOG.warning(
                "Don't forget to verify your email and "
                "complete your profile before going on"
            )
        LOG.info("You are already logged in as: %s", user_conf.email)
        return

    # Otherwise, start the login process
    LOG.info("The browser will open-up to login through Cosmian website...")

    code_verifier = gen_code_verifier()
    code_challenge = gen_code_challenge(code_verifier)
    state = gen_state()

    port = 5355
    redirect_uri = f"http://localhost:{port}/"

    params = {
        "response_type": "code",
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "client_id": MSE_AUTH0_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "openid profile email read:current_user "
        "update:current_user_metadata offline_access",
        "audience": MSE_AUTH0_AUDIENCE,
        "state": state,
    }

    # Run the server, open the browser and query auth0 "authorize"
    code = run_server(
        port, f"{MSE_AUTH0_DOMAIN_NAME}/authorize?" + urlencode(params), state
    )

    # Get an access/refresh token
    r = requests.post(
        url=f"{MSE_AUTH0_DOMAIN_NAME}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": MSE_AUTH0_CLIENT_ID,
            "code_verifier": code_verifier,
            "code": code,
            "redirect_uri": redirect_uri,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )

    if not r.ok:
        raise Exception(r.text)

    js = r.json()
    required_fields = ["access_token", "refresh_token", "id_token"]
    if not all(f in js for f in required_fields):
        raise Exception("Missing fields in authentication response")

    id_token = jwt_payload_decode(js["id_token"])

    user = UserConf(email=id_token["email"], refresh_token=js["refresh_token"])
    user.save()

    LOG.success("Successfully logged in as %s", user.email)  # type: ignore

    LOG.info("Your refresh token is now saved into: %s", UserConf.path())

    try:
        me = get_user_info(user)
        LOG.info("Welcome back to Microservice Encryption %s", me.first_name)
    except NameError:
        LOG.info("\nWelcome to Microservice Encryption.")
        LOG.advice(  # type: ignore
            "You can use `mse scaffold <app_name>` to initialize a new application."
        )
        LOG.warning(
            "Don't forget to verify your email and "
            "complete your profile before going on"
        )


def get_user_info(user: UserConf) -> User:
    """Get the user information from its token."""
    r: requests.Response = get_me(conn=user.get_connection())

    if not r.ok:
        raise NameError("Unknown or unconfigured account.")

    me = r.json()
    if not me:
        raise NameError("Unknown or unconfigured account.")

    return User.from_dict(me)


def gen_state() -> str:
    """Generate the state field."""
    return base64.b64encode(secrets.token_bytes(43)).decode("utf-8")


def gen_code_verifier() -> str:
    """Generate the code verifier."""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(62)).decode("utf-8")
    return re.sub("[^a-zA-Z0-9]+", "", code_verifier)


def gen_code_challenge(code_verifier: str) -> str:
    """Generate the code challenge."""
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")


def open_webbrowser(address):
    """Open a browser at the given `address`."""
    try:
        webbrowser.open(url=address, new=1)
    except webbrowser.Error as e:
        raise Exception(f"Unable to open the web browser: {e}") from e


def _b64_decode(data):
    """Decode the data from base64 by adding the padding."""
    data += "=" * (4 - len(data) % 4)
    return base64.b64decode(data).decode("utf-8")


def jwt_payload_decode(jwt):
    """Decode a jwt payload."""
    _, payload, _ = jwt.split(".")
    return json.loads(_b64_decode(payload))
