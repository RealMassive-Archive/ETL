#!/bin/bash
export REALMASSIVE_USER="rm-svc-sdk-test@realmassive.com" &&
export REALMASSIVE_ENDPOINT="https://realmassive-staging.appspot.com" &&
export AUTH_ENDPOINT="https://auth-staging.realmassive.com" &&
export REALMASSIVE_PASSWORD="foobar" &&
python -c "from realmassive import RealMassive;from etl_script import *;old = RealMassive();new = RealMassive('http://127.0.0.1:5000');media_service = RealMassive('http://127.0.0.1:8088');endeavor_oi = 'ahVzfnJlYWxtYXNzaXZlLXN0YWdpbmdyGQsSDE9yZ2FuaXphdGlvbhiAgIDQiIzDCQw';colliers_austin = 'ahVzfnJlYWxtYXNzaXZlLXN0YWdpbmdyGQsSDE9yZ2FuaXphdGlvbhiAgIC2haWZCQw';convert_organization_to_new_system(old, new, media_service, endeavor_oi);convert_organization_to_new_system(old, new, media_service, colliers_austin)"
