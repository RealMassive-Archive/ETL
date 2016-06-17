#!/bin/bash
export REALMASSIVE_USER="rm-svc-sdk-test@realmassive.com" &&
export REALMASSIVE_ENDPOINT="https://realmassive-staging.appspot.com" &&
export AUTH_ENDPOINT="https://auth-staging.realmassive.com" &&
export REALMASSIVE_PASSWORD="foobar" &&
export REALMASSIVE_V2_ENDPOINT="http://localhost:5000" &&
export REALMASSIVE_MEDIA_SERVICE="http://localhost:8088" &&
python -c "import os;from realmassive_sdk import RealMassive;from etl_script import *;old = RealMassive();new = RealMassive(os.environ['REALMASSIVE_V2_ENDPOINT']);media_service = RealMassive(os.environ['REALMASSIVE_MEDIA_SERVICE']);endeavor_oi = 'ahVzfnJlYWxtYXNzaXZlLXN0YWdpbmdyGQsSDE9yZ2FuaXphdGlvbhiAgIDQiIzDCQw';colliers_austin = 'ahVzfnJlYWxtYXNzaXZlLXN0YWdpbmdyGQsSDE9yZ2FuaXphdGlvbhiAgIC2haWZCQw';convert_organization_to_new_system(old, new, media_service, endeavor_oi);convert_organization_to_new_system(old, new, media_service, colliers_austin)"
