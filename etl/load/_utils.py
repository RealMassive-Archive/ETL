
from datetime import datetime

from ..config import APIV2, KEYMAP, media_sdk, sdk


def deletable():
    return {"deleted": False}


def timestamp():
    now = datetime.utcnow().isoformat()
    return {
        "created": now,
        "updated": now
    }


def get_resource(resource_type, id_):
    """ GETs a v2 resource.
    """
    return sdk(resource_type)(id_).GET()


def send_metadata(**attributes):
    if "blobkey" in attributes:
        attributes["blobkey"] = str(attributes["blobkey"])
    return media_sdk("meta").POST(json=dict(attributes))


def load_resource(resource_type, resource):
    """ POSTs a v2 resource.
    """
    # return sdk(resource_type).POST(json=resource)
    id_ = APIV2.create_resource(resource['data'])
    return {'data': {'id': id_, 'type': resource['data']['type']}}


def relate_child_to_parent(parent_type, parent_id, child_type, child):
    """ Relate a resource to another resource.
    """
    # return sdk(parent_type)(parent_id)(child_type).POST(json=child)
    child_id = int(child['data']['id'])
    id_ = APIV2.create_relationship(parent_type, parent_id, child_type, child_id)
    return id_


def send_to_key_map(**kwargs):
    """ Send old:new key mapping to service.
    """
    KEYMAP.insert(**kwargs)


def get_new_from_key_map(v1_type, v2_type, key):
    """ Return new, v2 key from old.
    """
    return KEYMAP.get_new(v1_type, v2_type, key)


def resource(resource_type, **resource_attributes):
    """ Structure attributes and type to payload expected by v2 api.
    """
    return {
        "data": {
            "type": resource_type,
            "attributes": resource_attributes
        }
    }


def relationship_resource(resource1, resource2, **kwargs):
    """ Structure two resources into a payload expected by a v2 api relationship resource.

        Example:
            passing in a `card` and a `lease` will return attributes payload for a `contact`.
            This can then be passed into resource("contacts", **) to get the payload required
            for posting the contact.
    """
    resource1 = {k:v for k,v in resource1.iteritems()}
    resource1["data"].pop("attributes", None)
    resource2 = {k:v for k,v in resource2.iteritems()}
    resource2["data"].pop("attributes", None)

    attributes = {
        resource1["data"]["type"]: resource1,
        resource2["data"]["type"]: resource2,
    }
    attributes.update(kwargs)
    attributes.update(deletable())
    attributes.update(timestamp())
    return attributes

