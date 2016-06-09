from collections import defaultdict
import functools
import logging
import mimetypes

import requests
from requests.exceptions import HTTPError
from retrying import retry

import transform


def log_exception_on_retry(exception):
    """ Logs an exception and returns True -- to be used by custom `retry` decorator.
    """
    logging.warning("Retrying: {}".format(exception))
    return True
log_and_retry = functools.partial(retry, retry_on_exception=log_exception_on_retry)


@log_and_retry()
def _remote_call(partial, params=None):
    if not params:
        params = {}
    return partial(params=params)


def _multi_api_call(partial_call, params=None):
    """ Return an entire API call by iterating over all the cursors.
    """
    results = []
    if not params:
        params = {}
    call = _remote_call(partial_call, params=params)
    results.extend(call["results"])
    while call.get("cursor"):
        params.update({"cursor": call["cursor"]})
        call = _remote_call(partial_call, params=params)
        results.extend(call["results"])
    return results


#######################################################################
#######################################################################
#######################################################################


def load_resource(new, resource_type, resource_attributes):
    """ Create a new resource.
    """
    return new(resource_type).POST(json={
        "data": {
            "type": resource_type,
            "attributes": resource_attributes
        }
    })


def relate_child_to_parent(new, parent_type, parent_id, child_type, child):
    """ Relate a resource to another resource.
    """
    return new(parent_type)(parent_id)(child_type).POST(json=child)


def upload_media(media_service, filename, url):
    """ Upload media to new hosting service and return its metadata.
    """
    # Fetch url
    fetch_resp = requests.get(url)
    fetch_resp.raise_for_status()
    # Upload file
    # NOTE: hack around handling of files in authclient
    upload_url = media_service._path[0]
    upload_resp = requests.post(upload_url, files={"file": (filename, fetch_resp.content)})
    # TODO: remove try/except once everyone is using new upload service
    try:
        new_url = str(media_service(upload_resp.json()["id"]))
    except:
        new_url = upload_resp.headers["location"]
    return new_url


#######################################################################
#######################################################################
#######################################################################

from collections import defaultdict

def get_users_from_organization(old, organization_payload):
    """ Return a dict of lists, containing v1 Users per email address.
    """
    owner = [organization_payload["owner"]["master_key"]]
    admins = [dude["master_key"] for dude in organization_payload.get("admins", [])]
    members = [dude["master_key"] for dude in organization_payload.get("members", [])]
    org_peeps = set(admins + members + owner)

    contacts = defaultdict(list)
    for master_key in org_peeps:
        user_info = old.api.v1.users(master_key).GET()
        email = user_info["email"]
        if "@realmassive" in email:
            continue
        contacts[email].append(user_info)
    return contacts


def get_buildings_from_organization(old, organization_keystring):
    """ Return list of Buildings for a particular organization.
    """
    params = {"manager.key": organization_keystring}
    return _multi_api_call(old.api.v1.buildings.GET, params=params)


def get_spaces_from_organization(old, organization_keystring):
    """ Return list of Spaces for a particular organization.

        Only return leases.
    """
    params = {
        "building.manager.key": organization_keystring,
        "space_type": "lease"
    }
    # First get the space keystrings
    results = _multi_api_call(old.api.v1.spaces.search.GET, params=params)
    space_keys = filter(None, [result.get("key") for result in results])

    # Now get each space individually
    spaces = []
    for key in space_keys:
        api_call = old.api.v1.spaces(key).GET()
        spaces.append(api_call)

    return spaces


def get_subleases_from_user(old, user):
    """ Return list of Spaces for a particular user that are subleases.

        Only return Public.
    """
    params = {
        "space_type": "sublease",
        "status": "Public"
    }
    return _multi_api_call(old.api.v1.spaces.GET, params=params)


@log_and_retry()
def get_old_media_entity(old, keystring):
    """ Return old media info.
    """
    old_media = _remote_call(old.media(keystring).GET)
    filename = old_media["filename"]
    if not filename or "." not in filename:
        # Invalid filename, which is required in upload service
        mimetype = old_media["mime_type"]
        ext = mimetypes.guess_extension(mimetype)
        if ext:
            old_media["filename"] = "photo" + ext
        else:
            logging.error("skipping media due to unknown file type: {}".format(keystring))
            return None

    return old_media


def get_new_media_for_old(old, new, media_service, keystring):
    """ Returns a new media entity from an old keystring, or None if there is an issue.

        Handles uploading to the new upload service, naming, etc.
    """
    # Fetch old media, extract relevant information
    old_media = get_old_media_entity(old, keystring)
    if not old_media:
        return None
    # Transform to new schema
    media = transform.media(old_media)

    if old_media["is_video"] == True:
        pass
    else:
        if media.get("preview"):
            try:
                media["preview"] = upload_media(media_service, "preview.jpe", media["preview"])
            except:
                logging.warning("Skipping because image could not be fetched: {}".format(media["preview"]))
        try:
            # Upload to new upload service, and update the url
            media["url"] = upload_media(media_service, old_media["filename"], media["url"])
        except HTTPError:
            logging.warning("Skipping because image could not be fetched: {}".format(media["url"]))
            return None
    return load_resource(new, "media", media)


def convert_organization_to_new_system(old, new, media_service, organization_keystring):
    # Fetch organization payload
    organization_payload = old.api.v1.organizations(organization_keystring).GET()

    # Load v2 Team (Authorization)
    team_info = transform.organization_team(organization_payload)
    team = load_resource(new, "teams", team_info)

    # Load v2 Organization (Information)
    organization_info = transform.organization_organization(organization_payload)
    organization = load_resource(new, "organizations", organization_info)
    relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/organizations", transform.permission(organization))  # Permission: organization
    # Organization attachment
    logo = organization_payload.get("logo")
    if logo:
        media = get_new_media_for_old(old, new, media_service, logo["key"])
        if media:
            relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/media", transform.permission(media))  # Permission: media
            attachment = transform.attachment(media)
            # TODO: metadata resource permission
            relate_child_to_parent(new, "organizations", organization["data"]["id"], "attachments", attachment)

    # Load v2 Users & Contacts
    email_and_contacts = get_users_from_organization(old, organization_payload)
    for email, contacts in email_and_contacts.iteritems():
        # NOTE: For now, 1:1 user:contact
        old_contact = contacts[0]

        # Create v2 User
        user_info = transform.user(old_contact)
        load_resource(new, "users", user_info)
        # NOTE: load_user does not return user id. Need to GET
        user = {"data": new.users.GET(params={"filter[where][email]": user_info["email"]})["data"][0]}
        # Add User to Team
        team_member = transform.team_member(user)
        # TODO: metadata resource permission
        relate_child_to_parent(new, "teams", team["data"]["id"], "members", team_member)

        # Create v2 Contact; Associate with User and Organization
        contact = load_resource(new, "contacts", user_info)
        relate_child_to_parent(new, "users", user["data"]["id"], "contacts", contact)
        relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/contacts", transform.permission(contact))  # Permission: contact
        relate_child_to_parent(new, "organizations", organization["data"]["id"], "contacts", contact)
        # Contact attachment
        photo = old_contact.get("photo")
        if photo and "default_profile" not in photo:
            # NOTE: From API, we only have access to the URL, so cant use the convenience method
            filename = "photo.png"
            media_info = {
                "filename": filename,
                "ip_status": "APPROVED",
                "mime_type": "image/png",
                "url": upload_media(media_service, filename, photo),
                "user_approved": True,
            }
            media = load_resource(new, "media", media_info)

            if media:
                relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/media", transform.permission(media))  # Permission: media
                attachment = transform.attachment(media)
                # TODO: metadata resource permission
                relate_child_to_parent(new, "contacts", contact["data"]["id"], "attachments", attachment)

    # Load v2 Building assets
    old_building_asset_map = {}  # Map of old keystrings to new ids
    old_building_media_map = defaultdict(dict)  # {old_building_keystring: {old_att_keystring: new_att_id}}

    old_buildings = get_buildings_from_organization(old, organization_keystring)
    for building in old_buildings:
        new_building = transform.building_asset(building)
        new_building = load_resource(new, "buildings", new_building)
        relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/buildings", transform.permission(new_building))  # Permission: building asset
        old_building_asset_map[building["key"]] = new_building["data"]["id"]
        # TODO: building listing?
        # TODO: building listing contacts?
        # Building attachments
        attachments = building.get("attachments", [])
        for i, old_attachment in enumerate(attachments):
            media = get_new_media_for_old(old, new, media_service, old_attachment["key"])
            if media:
                relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/media", transform.permission(media))  # Permission: media
                attachment = transform.attachment(media, precedence=float(i))
                # TODO: metadata resource permission
                relate_child_to_parent(new, "buildings", new_building["data"]["id"], "attachments", attachment)
                old_building_media_map[building["key"]][old_attachment["key"]] = media["data"]["id"]

    # Load v2 Space/lease assets
    old_space_asset_map = {}

    old_spaces = get_spaces_from_organization(old, organization_keystring)
    for space in old_spaces:
        # Create v2 asset
        new_space_asset = transform.space_asset(space)
        new_space = load_resource(new, "spaces", new_space_asset)
        relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/spaces", transform.permission(new_space))  # Permission: space asset
        space_id = new_space["data"]["id"]
        old_space_asset_map[space["key"]] = space_id

        # Link to v2 building
        old_building = space.get("building")
        if old_building:
            new_building_id = old_building_asset_map[old_building["key"]]
            new.buildings(new_building_id).spaces.POST(json=new_space)
        else:
            new_building_id = None

        # Create v2 listing
        listing_type = space.get("space_type")
        listing_type += "s"  # pluralize
        if listing_type == "subleases":
            # TODO: subleases
            logging.warning("Skipping sublease listing for space: {}".format(space_id))
            continue
        elif listing_type != "leases":
            logging.warning("Unknown listing_type {} for space {}".format(listing_type, space["key"]))
            continue

        listing_info = transform.space_lease(space)
        listing = load_resource(new, listing_type, listing_info)
        space_listing = relate_child_to_parent(new, "spaces", space_id, listing_type, listing)
        relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/{}".format(listing_type), transform.permission(listing))  # Permission: space listing
        # Relate organization to listing
        relate_child_to_parent(new, listing_type, listing["data"]["id"], "organizations", organization)
        # Relate contacts to listing
        for contact in space.get("contacts", []):
            key = contact.get("master_key")
            if key:
                # Get user from old for email
                user = _remote_call(old.api.v1.users(key).GET)
                email = user.get("email")
                if email:
                    contacts = new.contacts.GET(params={"filter[where][email]": email})
                    data = contacts.get("data")
                    if data:
                        contact = {"data": data[0]}
                        contact["data"].pop("relationships")  # NOTE: will barf if sees relationships
                        relate_child_to_parent(new, listing_type, listing["data"]["id"], "contacts", contact)

        # Attach media to space
        attachments = space.get("attachments", [])
        for i, old_attachment in enumerate(attachments):
            if new_building_id:
                # Ignore building attachments
                building_attachments = old_building_media_map.get(new_building_id)
                if building_attachments and old_attachment["key"] in building_attachments:
                    continue
            media = get_new_media_for_old(old, new, media_service, old_attachment["key"])
            if media:
                relate_child_to_parent(new, "teams", team["data"]["id"], "permissions/media", transform.permission(media))  # Permission: media
                attachment = transform.attachment(media, precedence=float(i))
                # TODO: metadata resource permission
                relate_child_to_parent(new, listing_type, listing["data"]["id"], "attachments", attachment)

