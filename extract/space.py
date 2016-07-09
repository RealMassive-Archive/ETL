
from ._utils import date, identifiers, key, timestamp


def space(space):
    data = {
        "availability_date": date(getattr(space, "availability_date")),
        "building": key(getattr(space, "building")),
        "expiration_date": date(getattr(space, "expiration_date")),
        "floor_number": getattr(space, "floor_number"),
        "max_contiguous": getattr(space, "max_contiguous"),
        "min_divisible":  getattr(space, "min_divisible"),
        "office_finish_percentage": getattr(space, "office_finish_percentage"),
        "rate": getattr(space, "rate"),
        "rate_frequency": getattr(space, "rate_frequency"),
        "rate_type": getattr(space, "rate_type"),
        "space_available": getattr(space, "space_available"),
        "space_available_units": getattr(space, "space_available_units"),
        "space_type": getattr(space, "space_type"),
        "status": getattr(space, "status"),
        "unit_number": getattr(space, "unit_number"),
    }
    data.update(timestamp(space))
    data.update(identifiers(space))
    data.update({
        "attachments": map(lambda x: key(x), space.attachments)
    })
    data.update({
        "contacts": map(lambda x: key(x), space.contacts)
    })
    organization = space.get_organization()
    data["organization"] = key(organization.key) if organization else None

    return data

