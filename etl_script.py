from collections import defaultdict
import logging
import mimetypes

import requests
from requests.exceptions import HTTPError


def clean_up_shit_nulls(stuff, shit_nulls=None):
    if not shit_nulls:
        shit_nulls = ["", {}, None]

    clean_dict = {}
    for k, v in stuff.iteritems():
        if v in shit_nulls:
            continue
        elif isinstance(v, dict):
            v = clean_up_shit_nulls(v, shit_nulls=shit_nulls)
        clean_dict[k] = v
    return clean_dict


def _transform_address(address_info):
    """ Transform v1 address to v2.

        state = fields.String()
        county = fields.String()
        zipcode = fields.String()
        street = fields.String()
        address = fields.String()
        full_state = fields.String()
        geo_latitude = fields.Float()
        geo_longitude = fields.Float()
    """
    data = {
#        "address": None,
        "city": address_info.get("city"),
        "county": address_info.get("county"),
#        "full_state": None,
        "state": address_info.get("state"),
        "street": address_info.get("street"),
        "zipcode": address_info.get("zipcode")
    }
    geo = address_info.get("geo")
    if geo:
        data.update({
            "latitude": geo.get("latitude"),
            "longitude": geo.get("longitude")
        })
    return clean_up_shit_nulls(data)


def transform_media(media_info):
    """ Transform v1 media into v2 media.

        category = fields.String()
        title = fields.String()
        description = fields.String()
        url = fields.String()
        mime_type = fields.String()
        preview = fields.String()
        user_approved = fields.Boolean()
        ip_status = fields.String()
        height = fields.Integer()
        width = fields.Integer()
        video_tag = fields.String()
        file_size = fields.String()
    """
    data = {
        "category": media_info.get("category"),
        "description": media_info.get("description"),
        "title": media_info.get("title"),
        "url": media_info.get("url"),
        "mime_type": media_info.get("mimetype"),
#        "preview": fields.String()
        "user_approved": media_info.get("approved"),
        "ip_status": media_info.get("ip_status"),
        "height": media_info.get("height"),
        "width": media_info.get("width"),
#        "video_tag": media_info.get(""),
#        "file_size": fields.String("")
    }
    return clean_up_shit_nulls(data)


def _transform_social(social_info):
    """ Transform v1 social_links to v2 social.

        website = fields.String()
        linkedin = fields.String()
        twitter = fields.String()
    """
    data = {
        "website": social_info.get("webpage"),
        "linkedin": social_info.get("linkedin"),
        "twitter": social_info.get("twitter")
    }
    return clean_up_shit_nulls(data)


#######################################################################
## Spaces
#######################################################################

def transform_space_asset(space_info):
    """ Transform v1 Space to v2 asset.

        floor_number = fields.String()
        max_contiguous = fields.Nested(AreaSchema)
        min_divisible = fields.Nested(AreaSchema)
        office_percentage = fields.Integer()
        space_size = fields.Nested(AreaSchema)
        unit_number = fields.String()
    """
    # Heading conversion
    data = {
        "floor_number": space_info.get("floor_number"),
        "max_contiguous": space_info.get("max_contiguous"),
        "min_divisible": space_info.get("min_divisible"),
        "office_percentage": space_info.get("office_finish_percentage"),
        "space_size": space_info.get("space_available"),
        "unit_number": space_info.get("unit_number")
    }

    # Value conversion
    if data["space_size"]:
        units = space_info.get("space_available_units")
        if units:
            units = units.lower()
            if "sf" == units:
                units = "sqft"
        else:
            units = "sqft"
        data["space_size"] = {
            "value": data["space_size"],
            "units": units
        }
    # Max. contig (if not provided, default to space_size)
    if data["max_contiguous"]:
        data["max_contiguous"] = {
            "value": data["max_contiguous"],
            "units": "sqft"
        }
    elif data["space_size"]:
        data["max_contiguous"] = {
            "value": data["space_size"]["value"],
            "units": data["space_size"]["units"]
        }
    # Min. divis (if not provided, default to space_size)
    if data["min_divisible"]:
        data["min_divisible"] = {
            "value": data["min_divisible"],
            "units": "sqft"
        }
    elif data["space_size"]:
        data["min_divisible"] = {
            "value": data["space_size"]["value"],
            "units": data["space_size"]["units"]
        }
    return clean_up_shit_nulls(data)


def _transform_space_rate(space_info):
    """ Transform v1 rate info into v2 rate.

        rate = fields.Nested(CurrencySchema)
        frequency = fields.String(); ["yearly", "monthly"]
        type = fields.String(); ["full_service_gross", "industrial_gross", "modified_gross", "single_net", "double_net", "triple_net", "other"]
    """
    # Heading conversion
    data = {
        "rate": {
            "value": space_info.get("rate"),
            "units": "usd"
        },
        "frequency": space_info.get("rate_frequency"),
        "type": space_info.get("rate_type")
    }

    # Value conversion
    if data["frequency"]:
        data["frequency"] = data["frequency"].lower()
    if data["type"]:
        if data["type"] == "n/a":
            data["type"] = None
    return data


def transform_space_lease(space_info):
    """ Transform v1 Space into v2 lease contract.

        available_date = fields.Date()
        rate = fields.Nested(RateSchema)
        #TODO: lease_term int4range not null
        tenant_improvement = fields.String()
    """
    return clean_up_shit_nulls({
        "available_date": space_info.get("availability_date"),
        "rate": _transform_space_rate(space_info),
#        "lease_term": space_info.get("lease_term"),  # TODO
        "tenant_improvement": space_info.get("ti")
    })


def transform_space_sublease(space_info):
    """ Transform v1 Space into v2 sublease contract.

        rate = fields.Nested(RateSchema)
        #TODO: sublease_availability tsrange not null
    """
    return {
        "rate": _transform_space_rate(space_info),
#        "sublease_availability": space_info.get("expiration_data")  # TODO
    }


#######################################################################
## Buildings
#######################################################################

def transform_building_asset(building_info):
    """ Transform v1 Building to v2 building asset.

        address = fields.Nested(AddressSchema)
        air_conditioned = fields.Boolean()
        building_size = fields.Nested(AreaSchema)
        build_status = fields.String(); ["existing", "planned", "in_development"]
        building_type = fields.String(); ["office", "retail", "flex", "industrial", "multifamily", "mixed"]
        building_class = fields.String(); ["A", "B", "C"]
        clear_height = fields.Nested(LengthSchema)
        description = fields.String()
        floor_count = fields.Integer()
        leed_rating = fields.String(); ["none", "certified", "gold", "silver", "platinum"]
        signage = fields.String()
        sprinkler = fields.Boolean()
        tenancy = fields.String(); ["multiple", "single"]
        title = fields.String()
        year_built = fields.Integer()
        year_renovated = fields.Integer()
    """
    # Heading conversion
    data = {
#        "attachments": building_data.get("attachments") or [],
        "address": _transform_address(building_info.get("address")),
        "air_conditioned": building_info.get("ac"),
        "build_status": building_info.get("build_status"),
        "building_class": building_info.get("building_class"),
        "building_size": building_info.get("size"),
        "building_type": building_info.get("type"),
        "clear_height": building_info.get("clear_height"),
        "description": building_info.get("description"),
        "floor_count": building_info.get("floor_count"),
        "leed_rating": building_info.get("leed"),
        "signage": building_info.get("signage"),
        "sprinkler": building_info.get("sprinkler"),
        "tenancy": building_info.get("tenancy"),
        "title": building_info.get("title"),
        "year_built": building_info.get("year_built"),
        "year_renovated": building_info.get("year_renovated"),
    }

    # Value conversion
    if data["build_status"]:
        if "plan" in data["build_status"].lower():
            data["build_status"] = "planned"
        elif "devel" in data["build_status"].lower():
            data["build_status"] = "in_development"
        data["build_status"] = data["build_status"].lower()
    if data["building_size"]:
        data["building_size"] = {
            "value": data["building_size"],
            "units": "sf"
        }
    if data["building_type"]:
        data["building_type"] = data["building_type"].lower()
    if data["clear_height"]:
        data["clear_height"] = {
            "value": data["clear_height"],
            "units": "sqft"  # TODO: ft? in?
        }
    if data["leed_rating"]:
        data["leed_rating"] = data["leed_rating"].lower()
    if data["sprinkler"]:
        if "es" in data["sprinkler"].lower():  # TODO: ESFR?
            data["sprinkler"] = True
        else:
            data["sprinkler"] = False
    if data["tenancy"]:
        if "sin" in data["tenancy"].lower():
            data["tenancy"] = "single"
        elif "mult" in data["tenancy"].lower():
            data["tenancy"] = "multiple"

    return clean_up_shit_nulls(data)


def transform_building_lease(building_info):  # TODO
    """ Transform v1 Building to v2 lease contract.
    """


def transform_building_sale(building_info):  # TODO
    """ Transform v1 Building to v2 sale contract.
    """


#######################################################################
## Organizations
#######################################################################

def transform_organization_organization(firm_data):
    """ Transform v1 Organization to v2 Firm.

        address = fields.Nested(AddressSchema)
        bio = fields.String()
        email = fields.String()
        name = fields.String()
        phone = fields.String()
        social = fields.Nested(SocialLinksSchema)
    """
    # Heading conversion
    data = {
        "address": firm_data.get("address"),
        "bio": firm_data.get("bio"),
        "email": firm_data.get("email"),
        "name": firm_data.get("name"),
        "phone": firm_data.get("phone"),
        "social": firm_data.get("social_links"),
#        "logo": firm_data.get("logo"),
    }

    # Value conversion
    if data["address"]:
        data["address"] = _transform_address(data["address"])
    if data["social"]:
        data["social"] = _transform_social(data["social"])

    return clean_up_shit_nulls(data)


def transform_organization_team(firm_data):
    """ Transform v1 Organization to v2 Team.

        name
    """
    return {"name": firm_data.get("name")}


#######################################################################
## Users
#######################################################################

def transform_user(user_data):
    """ Transform v1 User to v2 Contact.

        bio = fields.String()
        ccim_number = fields.String()
        license_number = fields.String()
        sior_member = fields.Boolean()
        sior_number = fields.String()
        title = fields.String()
        email = fields.String()
        first_name = fields.String()
        last_name = fields.String()
        mobile_phone = fields.String()
        phone = fields.String()
        social = fields.nested(SocialLinksSchema)
    """
    # Heading conversion
    data = {
        "bio": user_data.get("bio"),
        "ccim_number": user_data.get("ccim_number"),
        "license_number": user_data.get("license_number"),
        "email": user_data.get("email"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "mobile_phone": user_data.get("mobile_phone"),
        "phone": user_data.get("phone"),
        "sior_number": user_data.get("sior_number"),
        "social": user_data.get("social_links"),
        "title": user_data.get("title")
#        "photo": user_data.get("photo")
    }

    # Value conversion
    if data["ccim_number"]:
        data["ccim_member"] = True
    if data["sior_number"]:
        data["sior_member"] = True
    if data["social"]:
        data["social"] = _transform_social(data["social"])

    return clean_up_shit_nulls(data)


#######################################################################
#######################################################################
#######################################################################

def load_building(new, building_info):
    """ Create a new RealMassive Building.
    """
    return new.buildings.POST(json={
        "data": {
            "type": "buildings",
            "attributes": building_info
        }
    })


def load_space(new, space_info):
    """ Create a new RealMassive Space.
    """
    return new.spaces.POST(json={
        "data": {
            "type": "spaces",
            "attributes": space_info
        }
    })


def load_team(new, team_info):
    """ Create a new Team with the specified name.
    """
    return new.teams.POST(json={
        "data": {
            "type": "teams",
            "attributes": team_info
        }
    })


def load_team_member(new, team_id, team_member, membership="accepted"):
    """ Add a team_member to a team (indicated by team_id).
    """
    return new.teams(team_id).members.POST(json={
        "data": {
            "type": "members",
            "attributes": {
                "membership": membership,
                "users": team_member
            }
        }
    })


def load_user(new, user_info):
    """ Create a new RealMassive User.
    """
    return new.users.POST(json={
        "data": {
            "type": "users",
            "attributes": user_info
        }
    })


def load_contact(new, contact_info):
    """ Create a new RealMassive Card.
    """
    return new.contacts.POST(json={
        "data": {
            "type": "contacts",
            "attributes": contact_info
        }
   })


def load_organization(new, organization_info):
    """ Create a new Organization.
    """
    return new.organizations.POST(json={
        "data": {
            "type": "organizations",
            "attributes": organization_info
        }
    })


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
    return upload_resp.headers["location"]


def load_media(new, media_info):
    """ Create a new Media.
    """
    return new.media.POST(json={
        "data": {
            "type": "media",
            "attributes": media_info
        }
    })


def load_attachment(new, target_collection, target_id, media, precedence=0.0):
    """ Add an media to a resource as an attachment.

    Arguments:
        target_resource: resource type of target
        target_id: ID of target
        media_info: data of media resource
    """
    return new(target_collection)(target_id)("attachments").POST(json={
        "data": {
            "type": "attachments",
            "attributes": {
                "precedence": precedence,
                "media": media
            }
        }
    })


def load_listing(new, listing_type, listing_info):
    """ Create a new RealMassive listing entity.

        LeaseSchema
        available_date = fields.Date()
        rate = fields.Nested(RateSchema)
        lease_term = fields.Nested(IntegerRangeSchema)
        tenant_improvement = fields.String()

        SubleaseSchema
        rate = fields.Nested(RateSchema)
        sublease_availability = fields.Nested(DateRangeSchema)
    """
    return new(listing_type).POST(json={
        "data": {
            "type": listing_type,
            "attributes": listing_info
        }
    })


def attach_listing(new, target_collection, target_id, listing_type, listing):
    """ Create a new RealMassive lease on Space (indicated by space_id).
    """
    return new(target_collection)(target_id)(listing_type).POST(json=listing)


#######################################################################
#######################################################################
#######################################################################

from collections import defaultdict


def get_all_organizations(old):
    """ Return a list of v1 organizations.
    """
    # Get keys first, since we can't do a GET on api/v1/organizations
    organization_keys = []
    params = {"fields": "[key]"}
    api_call = old.api.v1.organizations.search.GET(params=params)
    organization_keys.extend([thing["key"] for thing in api_call["results"]])
    while api_call.get("cursor"):
        params.update({"cursor": api_call["cursor"]})
        api_call = old.api.v1.organizations.search.GET(params=params)
        organization_keys.extend([thing["key"] for thing in api_call["results"]])

    # Use keys to do GETs on individual orgs
    organizations = []
    for org_key in organization_keys:
        org = old.api.v1.organizations(org_key).GET()
        organizations.append(org)

    return organizations


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
    buildings = []
    params = {"manager.key": organization_keystring}
    api_call = old.api.v1.buildings.GET(params=params)
    buildings.extend(api_call["results"])
    while api_call.get("cursor"):
        params.update({"cursor": api_call["cursor"]})
        api_call = old.api.v1.buildings.GET(params=params)
        buildings.extend(api_call["results"])
    return buildings


def get_spaces_from_organization(old, organization_keystring):
    """ Return list of Spaces for a particular organization.

        Only return leases.
    """
    space_keys = []
    params = {
        "building.manager.key": organization_keystring,
        "space_type": "lease"
    }
    # First get the space keystrings
    api_call = old.api.v1.spaces.search.GET(params=params)
    for result in api_call["results"]:
        key = result.get("key")
        if key:
            space_keys.append(key)
    while api_call.get("cursor"):
        params.update({"cursor": api_call["cursor"]})
        api_call = old.api.v1.spaces.search.GET(params=params)
        for result in api_call["results"]:
            key = result.get("key")
            if key:
                space_keys.append(key)

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
    spaces = []
    params = {
        "space_type": "sublease",
        "status": "Public"
    }
    api_call = old.api.v1.spaces.GET(params=params)
    spaces.extend(api_call["results"])
    while api_call.get("cursor"):
        params.update({"cursor": api_call["cursor"]})
        api_call = old.api.v1.spaces.GET(params=params)
        spaces.extend(api_call["results"])
    return spaces


def get_new_media_for_old(old, new, media_service, keystring):
    """ Returns a new media entity from an old keystring, or None if there is an issue.

        Handles uploading to the new upload service, naming, etc.
    """
    # Fetch old media, extract relevant information
    old_media = old.media(keystring).GET()
    # TODO: Remove once video upload is working
    if old_media["is_video"] == True:
        logging.warning("Skipping media since video is not yet handled: {}".format(keystring))
        return None
    filename = old_media["filename"]
    if not filename or "." not in filename:
        # Invalid filename, which is not required in upload service
        mimetype = old_media["mime_type"]
        ext = mimetypes.guess_extension(mimetype)
        if ext:
            filename = "photo" + ext
        else:
            logging.error("skipping media due to unknown file type: {}".format(keystring))
            return None
    # Transform to new schema
    media_info = transform_media(old_media)

    try:
        # Upload to new upload service, and update the url
        media_info["url"] = upload_media(media_service, filename, media_info["url"])
    except HTTPError:
        logging.warning("Skipping because image could not be fetched: {}".format(media_info["url"]))
        return None

    # Create apiv2 media entity and return
    media = load_media(new, media_info)
    return media


def convert_organization_to_new_system(old, new, media_service, organization_keystring):
    # Fetch organization payload
    organization_payload = old.api.v1.organizations(organization_keystring).GET()

    # Transform v1 to v2
    team = transform_organization_team(organization_payload)  # Authorization
    organization = transform_organization_organization(organization_payload)  # Information
    email_and_contacts = get_users_from_organization(old, organization_payload)  # Users & Contacts

    # Load v2 Team (Authorization)
    team = load_team(new, team)
    organization = load_organization(new, organization)
    # TODO: Organization attachment
    logo = organization_payload.get("logo")
    if logo:
        media = get_new_media_for_old(old, new, media_service, logo["key"])
        attachment = load_attachment(new, "organizations", organization["data"]["id"], media)

    # Load v2 Users & Contacts
    for email, contacts in email_and_contacts.iteritems():
        # NOTE: For now, 1:1 user:contact
        old_contact = contacts[0]
        user_info = transform_user(old_contact)

        # Create v2 User
        load_user(new, user_info)
        # NOTE: load_user does not return user id. Need to GET
        user = new.users.GET(params={"filter[email]": user_info["email"]})["data"][0]
        # Add User to Team
        team_member = load_team_member(new, team["data"]["id"], {"data": user})

        # Create v2 Contact
        contact = load_contact(new, user_info)
        # Associate contact with user
        new.users(user["id"]).contacts.POST(json=contact)
        # Contact attachment
        photo = old_contact.get("photo")
        if photo and "default_profile" not in photo:
            # NOTE: From API, we only have access to the URL, so cant use the convenience method
            filename = "photo.png"
            media_info = {
                "filename": filename,
                "ip_status": "APPROVED",
                "user_approved": True,
                "url": upload_media(media_service, filename, photo)
            }
            media = load_media(new, media_info)
            if not media:
                attachment = load_attachment(new, "contacts", contact["data"]["id"], media)

    # Load v2 Building assets
    old_building_asset_map = {}  # Map of old keystrings to new ids
    old_building_media_map = defaultdict(dict)  # {old_building_keystring: {old_att_keystring: new_att_id}}

    old_buildings = get_buildings_from_organization(old, organization_keystring)
    for building in old_buildings:
        new_building = transform_building_asset(building)
        new_building = load_building(new, new_building)
        old_building_asset_map[building["key"]] = new_building["data"]["id"]
        # TODO: permissions
        # TODO: building listing?
        # Building attachments
        attachments = building.get("attachments", [])
        for i, old_attachment in enumerate(attachments):
            media = get_new_media_for_old(old, new, media_service, old_attachment["key"])
            if media:
                attachment = load_attachment(new, "buildings", new_building["data"]["id"], media, precedence=float(i))
                old_building_media_map[building["key"]][old_attachment["key"]] = media["data"]["id"]

    # Load v2 Space/lease assets
    old_space_asset_map = {}

    old_spaces = get_spaces_from_organization(old, organization_keystring)
    for space in old_spaces:
        # Create v2 asset
        new_space_asset = transform_space_asset(space)
        new_space = load_space(new, new_space_asset)
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

        listing_info = transform_space_lease(space)
        listing = load_listing(new, listing_type, listing_info)
        space_listing = attach_listing(new, "spaces", space_id, listing_type, listing)

        # Attach media to space
        # TODO: i think this should be listing
        attachments = space.get("attachments", [])
        for i, old_attachment in enumerate(attachments):
            if new_building_id:
                # Ignore building attachments
                building_attachments = old_building_media_map.get(new_building_id)
                if building_attachments and old_attachment["key"] in building_attachments:
                    continue
            media = get_new_media_for_old(old, new, media_service, old_attachment["key"])
            if media:
                attachment = load_attachment(new, "spaces", new_space["data"]["id"], media, precedence=float(i))


#####################################################################
## TESTS
######################################################################
#
#import json
#
#
#building_info = json.load(open("./building.json", "r"))
#transformed_building = clean_up_shit_nulls(transform_building_asset(building_info))
#expected_building = {
#    "address": {
#        "city": u"Austin",
#        "county": u"Travis County",
#        "latitude": u"30.3967473",
#        "longitude": u"-97.743585",
#        "state": u"TX",
#        "street": u"10401 Research Blvd",
#        "zipcode": u"78759"
#    },
#    "build_status": u"existing",
#    "building_size": {
#        "units": "sf",
#        "value": u"152938"
#    },
#    "building_type": u"retail",
#    "title": u"10401 Research Blvd",
#    "year_built": u"2001"
#}
#assert transformed_building == expected_building
#
#
#space_info = json.load(open("./space.json", "r"))
#transformed_space = transform_space_asset(space_info)
#expected_space = {
#    "space_size": {
#        "units": "sqft",
#        "value": "878"
#    },
#    "unit_number": "1050"
#}
#assert transformed_space == expected_space
#
#
#transformed_space_lease = transform_space_lease(space_info)
#expected_space_lease = {
#    "rate": {
#        "frequency": "yearly",
#        "rate": {
#            "units": "usd",
#            "value": "38.0"
#        },
#        "type": "triple_net"
#    }
#}
#assert transformed_space_lease == expected_space_lease
#
#
#organization_info = json.load(open("./organization.json", "r"))
#transformed_firm = transform_organization_organization(organization_info)
#expected_firm = {
#    "address": {
#        "city": "Austin",
#        "county": "Travis",
#        "state": "TX",
#        "street": "1703 W. 5th Street, Suite 850",
#        "zipcode": "78703"
#    },
#    "bio": "This is a long ass bio for a firm",
#    "name": "JLL Austin",
#    "phone": "5122252700",
#    "social": {
#        "linkedin": "https://www.linkedin.com/company/jll",
#        "twitter": "https://twitter.com/jll",
#        "website": "http://www.jll.com/austin/en-us"
#    }
#}
#assert transformed_firm == expected_firm
#
#
#transformed_team = transform_organization_team(organization_info)
#expected_team = {"name": "JLL Austin"}
#assert transformed_team == expected_team
#
#
#user_info = json.load(open("./user.json", "r"))
#transformed_user = transform_user(user_info)
#expected_user = {
#    "email": "michael.musslewhite@realmassive.com",
#    "first_name": "Michael",
#    "last_name": "Musslewhite"
#}
#assert transformed_user == expected_user
