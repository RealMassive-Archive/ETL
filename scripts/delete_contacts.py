import json
import requests

import authclient


API_EP = "https://api.realmassive.com"
CONTACTS_FILE = "./contacts_to_delete.json"
contacts_to_delete = json.load(open(CONTACTS_FILE))


token = lambda x: authclient.util.generate_service_token(x, superuser=True)
for contact_id in contacts_to_delete:
    # Make sure we arent deleting the ONLY contact for a sublease
    r = requests.get(API_EP + "/contacts/{}".format(contact_id))
    if r.status_code != 200:
        print("{} status: {}".format(contact_id, r.status_code))
        continue
    r2 = requests.get(API_EP + r.json()["data"]["relationships"]["subleases"]["links"]["related"])
    r3 = requests.get(API_EP + r2.json()["data"]["relationships"]["contacts"]["links"]["related"])
    if r3.json()["meta"]["count"] == 1:
        continue
    else:
        r4 = requests.delete(
            API_EP + "/contacts/{}".format(contact_id),
            headers={"Authorization": "Bearer {}".format(token("rm-svc-upload@realmassive.com"))}
        )
