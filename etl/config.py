
import os

from lib.keymap import KeyMap
from lib.convert import ApiV2

from realmassive_sdk import AuthRequester, RealMassive


APIV2 = ApiV2()
KEYMAP = KeyMap()
ENDPOINT = "http://localhost:5000"
USER = "rm-svc-sdk-test@realmassive.com"
PASSWORD = "foobar"
MEDIA_SERVICE_ENDPOINT = "http://localhost:8080/media"


class AuthConfig(object):
    ENDPOINT = "http://localhost:5003"
    AUTH_ISSUER = "issuer"
    AUTH_SECRET = "secret"

requester = AuthRequester(
    user=USER,
    password=PASSWORD,
    config=AuthConfig
)
sdk = RealMassive(domain=ENDPOINT, requester=requester)
media_sdk = RealMassive(domain=MEDIA_SERVICE_ENDPOINT, requester=requester)
