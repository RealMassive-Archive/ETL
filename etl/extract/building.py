
from .address import address
from _utils import identifiers, key, timestamp


def building(building):
    data = {
        "ac": getattr(building, "ac"),
        "address": address(getattr(building, "address")),
        "build_status": getattr(building, "build_status"),
        "building_class": getattr(building, "building_class"),
        "clear_height": getattr(building, "clear_height"),
        "description": getattr(building, "description"),
        "floor_count": getattr(building, "floor_count"),
        "leed": getattr(building, "leed"),
        "manager": key(getattr(building, "manager")),  # TODO
        "signage": getattr(building, "signage"),
        "size": getattr(building, "size"),
        "size_units": getattr(building, "size_units"),
        "sprinkler": getattr(building, "sprinkler"),
        "tenancy": getattr(building, "tenancy"),
        "title": getattr(building, "title"),
        "type": getattr(building, "type"),
        "year_built": getattr(building, "year_built"),
        "year_renovated": getattr(building, "year_renovated"),
        "zoning": getattr(building, "zoning"),
    }
    data.update(timestamp(building))
    data.update(identifiers(building))
    data.update({
        "attachments": map(lambda x: key(x), getattr(building, "attachments", []))
    })
    data.update({
        "contacts": map(lambda x: key(x), getattr(building, "contacts", []))
    })
    return data
