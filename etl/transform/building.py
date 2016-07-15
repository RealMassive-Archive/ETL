
from ._utils import area, clean_up_shit_nulls, deletable, length, timestamp, price
from .address import address


def asset(building):
    """ Transform v1 Building to v2 building asset.
    """
    # Heading conversion
    data = {
        "address": address(building.get("address")),
        "air_conditioned": building.get("ac"),
        "build_status": building.get("build_status"),
        "building_class": building.get("building_class"),
        "building_size": area(
            value=building.get("size"),
            units=building.get("size_units")
        ),
        "building_subtype": None,  # NOTE: Depends on `building_type` (see below)
        "building_type": building.get("type"),
        "clear_height": length(
            value=building.get("clear_height"),
            units="ft"
        ),
        "description": building.get("description"),
        "floor_count": building.get("floor_count"),
        "leed_rating": building.get("leed"),
        "opex": price(building.get("operating_expenses")),
        "signage": building.get("signage"),
        "sprinkler": building.get("sprinkler"),
        "tenancy": building.get("tenancy"),
        "title": building.get("title"),
        "year_built": building.get("year_built"),
        "year_renovated": building.get("year_renovated"),
        "zoning": building.get("zoning"),
    }
    data.update(timestamp(building))
    data.update(deletable(building))

    # Value conversions
    if data["build_status"]:
        data["build_status"] = data["build_status"].lower()
        if "plan" in data["build_status"]:
            data["build_status"] = "planned"
        elif "devel" in data["build_status"]:
            data["build_status"] = "in_development"
        else:
            data["build_status"] = "existing"

    if data["building_type"]:
        data["building_type"] = data["building_type"].lower()
        # building_subtype
        if "medical" in data["building_type"]:
            data["building_type"] = "office"
            data["building_subtype"] = "medical"
        elif "flex" in data["building_type"]:
            data["building_type"] = "industrial"
            data["building_subtype"] = "flex"

    if data["leed_rating"]:
        data["leed_rating"] = data["leed_rating"].lower()

    if data["tenancy"]:
        if "sin" in data["tenancy"].lower():
            data["tenancy"] = "single"
        elif "mult" in data["tenancy"].lower():
            data["tenancy"] = "multiple"

    return clean_up_shit_nulls(data)

