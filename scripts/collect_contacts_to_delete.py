from collections import defaultdict
import json

import requests

SPACES_FILE = "./spaces.json"
BUILDINGS_FILE = "./buildings.json"
KEYMAP = "https://key-mapper.realmassive.com"
REALMASSIVE_API_ENDPOINT = "https://api.realmassive.com"


all_spaces = map(json.loads, open(SPACES_FILE))
all_subleases = [s for s in all_spaces if s.get("space_type") == "sublease"]
all_buildings = map(json.loads, open(BUILDINGS_FILE))
sublease_buildings = {s.get("building") for s in all_subleases if s.get("building")}
sublease_buildings = [b for b in all_buildings if b["id"] in sublease_buildings]

# Collect building contacts
building_contacts = defaultdict(set)
for b in sublease_buildings:
    b_id = b["id"]
    contacts = b.get("contacts", [])
    building_contacts[b_id].update(contacts)

# Find the cards belonging to contacts that need to be removed
to_remove = []
for s in all_subleases:
    s_id = s["id"]
    b_id = s["building"]
    if b_id and b_id in building_contacts:
        s_contacts = set(s.get("contacts", []))
        b_contacts = building_contacts[b_id]
        if len(s_contacts - b_contacts) != 0:
            for c in b_contacts:
                to_remove.append({
                    "space": s_id,
                    "user": c
                })

# Use keymap service to convert the appropriate keys
def get_v2_key(v1_type, v1_key, v2_type):
    r = requests.get(KEYMAP + "/{}".format(v1_type) + "/{}".format(v1_key))
    data = r.json()
    for result in data["results"]:
        if result["v2_type"] == v2_type:
            return result["v2_key"]
    return None

contact_attributes = []
for thing in to_remove:
    card_id = get_v2_key("users", thing["user"], "cards")
    sublease_id = get_v2_key("spaces", thing["space"], "subleases")
    if card_id and sublease_id:
        contact_attributes.append({
            "cards": card_id,
            "subleases": sublease_id
        })

contacts_to_delete = []
for attrs in contact_attributes:
    r = requests.get(
        REALMASSIVE_API_ENDPOINT + "/contacts?filter[where][cards.id]={cards}&filter[where][subleases.id]={subleases}".format(**attrs))
    if r.status_code == 200:
        data = r.json()["data"]
        if data:
            contacts_to_delete.append(r.json()["data"][0]["id"])
            continue
    print("Failed to get contacts with attrs: {}".format(attrs))
with open("contacts_to_delete.json", "w") as f:
    json.dump(contacts_to_delete, f)
