
import authclient
import requests

from etl.lib.keymap import RemoteKeyMap
from etl.load._utils import relationship_resource, resource


KEYMAP = RemoteKeyMap(location="https://key-mapper-staging.realmassive.com")
REALMASSIVE_API_ENDPOINT = "https://api-staging.realmassive.com"


token = lambda: authclient.util.generate_service_token("rm-svc-upload@realmassive.com", superuser=True)


def get_new_from_key_map(v1_type, v2_type, v1_key):
    """ Modified version of get_new_from_key_map that his remote service.
    """
    return KEYMAP.get_new(v1_type, v2_type, v1_key)


def load_resource(resource_type, resource):
    r = requests.post(
        REALMASSIVE_API_ENDPOINT + "/{}".format(resource_type),
        headers={
            "content-type": "application/json",
            "Authorization": "Bearer {}".format(token())
        },
        data=json.dumps(resource)
    )
    r.raise_for_status()
    return r.json()


def create_brochure_attachment(entity):
    """ Returns a dictionary of all the pertinent information regarding a brochure attachment.
    """
    old_media_id = entity.get("brochure")
    if not old_media_id:
        return

    old_target_id = entity["id"]
    if not old_target_id:
        return

    if entity["class"] == "Building":
        old_target_type = "buildings"
        new_target_type = "buildings"
    elif entity["class"] == "Space":
        old_target_type = "spaces"
        space_type = entity.get("space_type")
        if space_type == "lease":
            new_target_type = "leases"
        elif space_type == "sublease":
            new_target_type = "subleases"
        else:
            return
    else:
        return

    new_target_id = get_new_from_key_map(old_target_type, new_target_type, old_target_id)
    if not new_target_id:
        return

    new_media_id = get_new_from_key_map("media", "media", old_media_id)
    if not new_media_id:
        return

    category = get_new_from_key_map("media", "category", old_media_id)
    if not category:
        category = "brochure"

    # Permissions
    if old_target_type == "buildings":
        if entity.get("manager"):
            new_team_id = get_new_from_key_map("organizations", "teams", entity["manager"])
        else:
            new_team_id = None
    elif old_target_type == "spaces":
        if entity.get("organization"):
            new_team_id = get_new_from_key_map("organizations", "teams", entity["organization"])
        else:
            new_team_id = None

    return {
        "teams": new_team_id,
        "media": new_media_id,
        "category": category,
        "target_type": new_target_type,
        "target_id": new_target_id,
    }


def ingest_brochure(brochure_data):
    team_id = brochure_data["teams"]
    new_media_id = brochure_data["media"]
    category = brochure_data["category"]
    new_entity_kind = brochure_data["target_type"]
    new_entity_id = brochure_data["target_id"]

    # Create attachment
    attachment_attrs = relationship_resource(
        {"data": {"type": "media", "id": new_media_id}},
        {"data": {"type": new_entity_kind, "id": new_entity_id}},
        category=category
    )
    try:
        attachment = load_resource("attachments", resource("attachments", **attachment_attrs))
    except Exception as e:
        print("Failed to ingest: {} {}".format(e, brochure_data))
        return

    if team_id:
        # Permission (Media)
        permission_attrs = relationship_resource(
                {"data": {"type": "teams", "id": team_id}},
                {"data": {"type": "media", "id": new_media_id}},
                permission="admin"
        )
        try:
            load_resource("permissions", resource("permissions", **permission_attrs))
        except Exception as e:
            print("Failed to ingest perssion: {} {}".format(e, permission_attrs))
            return

        # Permission (Attachment)
        permission_attrs = relationship_resource(
                {"data": {"type": "teams", "id": team_id}},
                {"data": {"type": "attachments", "id": attachment["data"]["id"]}},
                permission="admin"
        )
        try:
            load_resource("permissions", resource("permissions", **permission_attrs))
        except Exception as e:
            print ("Failed to ingest permission: {} {}".format(e, permission_attrs))
            return

