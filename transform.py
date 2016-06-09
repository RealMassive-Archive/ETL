from datetime import datetime


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


def address(address_info):
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


# TODO: timestamps?
def media(media_info):
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


def social(social_info):
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

################################
# Metadata resource transforms #
################################


def permission(resource, permission_level="admin"):
    """ Restructure a v2 Media resource into an attachment.
    """
    resource_type = resource["data"]["type"]
    resource["data"].pop("attributes")
    return {
        "data": {
            "type": "permissions",
            "attributes": {
                "permission": permission_level,
                resource_type: resource
            }
        }
    }


def attachment(media, precedence=0.0):
    """ Restructure a v2 Media resource into an attachment.
    """
    return {
        "data": {
            "type": "attachments",
            "attributes": {
                "precedence": precedence,
                "media": media
            }
        }
    }


def team_member(team_member, membership="accepted"):
    """ Restructure a v2 User resource into a team_member.
    """
    return {
        "data": {
            "type": "members",
            "attributes": {
                "membership": membership,
                "users": team_member
            }
        }
    }


#######################################################################
## Spaces
#######################################################################

def space_asset(space_info):
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


def space_rate(space_info):
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


def space_lease(space_info):
    """ Transform v1 Space into v2 lease contract.

        available_date = fields.Date()
        rate = fields.Nested(RateSchema)
        lease_term int4range not null
        tenant_improvement = fields.String()
    """
    data = {
        "available_date": space_info.get("availability_date"),
        "rate": space_rate(space_info),
#        "lease_term": space_info.get("lease_term"),  # TODO
        "tenant_improvement": space_info.get("ti")
    }

    if data["available_date"]:
        data["available_date"] = datetime.strptime(data["available_date"], "%Y-%m-%d").isoformat()
    return clean_up_shit_nulls(data)


def space_sublease(space_info):
    """ Transform v1 Space into v2 sublease contract.

        rate = fields.Nested(RateSchema)
        #TODO: sublease_availability tsrange not null
    """
    return {
        "rate": space_rate(space_info),
#        "sublease_availability": space_info.get("expiration_data")  # TODO
    }


#######################################################################
## Buildings
#######################################################################

def building_asset(building_info):
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
        "address": address(building_info.get("address")),
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
            "units": "ft"  # TODO: ft? in?
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


def building_lease(building_info):  # TODO
    """ Transform v1 Building to v2 lease contract.
    """


def building_sale(building_info):  # TODO
    """ Transform v1 Building to v2 sale contract.
    """


#######################################################################
## Organizations
#######################################################################

def organization_organization(firm_data):
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
        data["address"] = address(data["address"])
    if data["social"]:
        data["social"] = social(data["social"])

    return clean_up_shit_nulls(data)


def organization_team(firm_data):
    """ Transform v1 Organization to v2 Team.

        name
    """
    return {"name": firm_data.get("name")}


#######################################################################
## Users
#######################################################################

def user(user_data):
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
        data["social"] = social(data["social"])

    return clean_up_shit_nulls(data)


