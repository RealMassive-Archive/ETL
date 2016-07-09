
import os

from realmassive_sdk import AuthRequester, RealMassive


ENDPOINT = "http://localhost:5000"
USER = "rm-svc-sdk-test@realmassive.com"
PASSWORD = "foobar"
KEYMAP_ENDPOINT = "http://localhost:5001"
MEDIA_SERVICE_ENDPOINT = "http://localhost:9000/media"

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
