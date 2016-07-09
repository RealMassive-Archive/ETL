
import json
import requests
from urlparse import urljoin

from ..config import KEYMAP_ENDPOINT, media_sdk, sdk


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
    return sdk(resource_type).POST(json=resource)


def relate_child_to_parent(parent_type, parent_id, child_type, child):
    """ Relate a resource to another resource.
    """
    return sdk(parent_type)(parent_id)(child_type).POST(json=child)


def send_to_key_map(**kwargs):
    """ Send old:new key mapping to service.
    """
    requests.post(
        KEYMAP_ENDPOINT,
        headers={"content-type": "application/json"},
        data=json.dumps(dict(**kwargs)),
        verify=False
    )


def get_new_from_key_map(v1_type, v2_type, key):
    """ Return new, v2 key from old.
    """
    response = requests.get(
        urljoin(KEYMAP_ENDPOINT + "/", "{}/{}".format(v1_type, key))
    )
    results = response.json()["results"]
    if not results:
        return None

    for res in results:
        if res["v2_type"] == v2_type:
            return res["v2_key"]

    return None


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
    return attributes

