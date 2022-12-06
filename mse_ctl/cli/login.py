"""Signup/Login subparser definition."""

import hashlib
import json
import secrets
import base64
import threading
import re
import webbrowser

from typing import Optional
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse, urlencode

import requests

from mse_ctl import (MSE_AUTH0_AUDIENCE, MSE_AUTH0_CLIENT_ID,
                     MSE_AUTH0_DOMAIN_NAME, MSE_CONSOLE_URL)
from mse_ctl.api.types import User
from mse_ctl.log import LOGGER as log
from mse_ctl.conf.user import UserConf
from mse_ctl.api.user import me as get_me

from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("login", help="Sign up or login a user")
    parser.add_argument('--whoami',
                        action='store_true',
                        help='Print who is currently logged in.')

    parser.set_defaults(func=run)


CODE: Optional[str] = None


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

            if 'code' not in parsed_query or 'state' not in parsed_query:
                self.send_response(400)
                return

            if state != parsed_query['state'][0]:
                self.send_response(400)
                return

            global CODE  # pylint: disable=global-statement
            CODE = parsed_query['code'][0]
            self.send_response(301)
            self.send_header("location", f"{MSE_CONSOLE_URL}/?origin=mse-ctl")
            self.end_headers()
            self.kill_server()

        def kill_server(self):
            """Stop the server."""
            assassin = threading.Thread(target=httpd.shutdown)
            assassin.daemon = True
            assassin.start()

    httpd = HTTPServer(('', port), LocalHTTPRequestHandler)
    # Open the browser on the authorize url to let the user login
    open_webbrowser(auth_url)
    log.info("Waiting for session... ")
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
            log.info("You are not logged in yet!")
            return

        log.info("Your are currently logged in as: %s", user_conf.email)

        try:
            me = get_user_info(user_conf)
        except NameError:
            log.info(
                "%sDon't forget to verify your email and "
                "complete your profile before going on%s", bcolors.WARNING,
                bcolors.ENDC)
        return

    log.info("You are now redirected to your browser to login...")

    code_verifier = gen_code_verifier()
    code_challenge = gen_code_challenge(code_verifier)
    state = gen_state()

    port = 5655
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
        "state": state
    }

    # Run the server, open the brower and query auth0 "authorized"
    code = run_server(port,
                      f"{MSE_AUTH0_DOMAIN_NAME}/authorize?" + urlencode(params),
                      state)

    # Get an access/refresh token
    r = requests.post(
        url=f"{MSE_AUTH0_DOMAIN_NAME}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": MSE_AUTH0_CLIENT_ID,
            "code_verifier": code_verifier,
            "code": code,
            "redirect_uri": redirect_uri
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=60)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    js = r.json()
    required_fields = ["access_token", "refresh_token", "id_token"]
    if not all(f in js for f in required_fields):
        raise Exception("Missing fields in authentication response")

    id_token = jwt_payload_decode(js["id_token"])

    user = UserConf(email=id_token["email"], refresh_token=js["refresh_token"])
    user.save()

    log.info("✅%s Successfully logged in as %s%s", bcolors.OKGREEN, user.email,
             bcolors.ENDC)

    log.info("Your refresh token is now saved into: %s", UserConf.path())

    try:
        me = get_user_info(user)
        log.info("Welcome back to Microservice Encryption %s", me.first_name)
    except NameError:
        log.info("\nWelcome to Microservice Encryption. ")
        log.info(
            "You can use the scaffold subcommand to initialize a new project.")
        log.info(
            "%sDon't forget to verify your email and "
            "complete your profile before going on%s", bcolors.WARNING,
            bcolors.ENDC)


def get_user_info(user: UserConf) -> User:
    """Get the user information from its token."""
    r: requests.Response = get_me(conn=user.get_connection())

    if not r.ok:
        raise NameError("Unknown or unconfigured account.")

    me = r.json()
    if not me:
        raise NameError("Unknown or unconfigured account.")

    return User.from_json_dict(me)


def gen_state() -> str:
    """Generate the state field."""
    return base64.b64encode(secrets.token_bytes(43)).decode('utf-8')


def gen_code_verifier() -> str:
    """Generate the code verifier."""
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(62)).decode('utf-8')
    return re.sub('[^a-zA-Z0-9]+', '', code_verifier)


def gen_code_challenge(code_verifier: str) -> str:
    """Generate the code challenge."""
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).decode('utf-8').replace(
        '=', '')


def open_webbrowser(address):
    """Open a browser at the given `address`."""
    try:
        webbrowser.open(url=address, new=1)
    except webbrowser.Error as e:
        raise Exception(f"Unable to open the web browser: {e}") from e


def _b64_decode(data):
    """Decode the data from base64 by adding the padding."""
    data += '=' * (4 - len(data) % 4)
    return base64.b64decode(data).decode('utf-8')


def jwt_payload_decode(jwt):
    """Decode a jwt payload."""
    _, payload, _ = jwt.split('.')
    return json.loads(_b64_decode(payload))
