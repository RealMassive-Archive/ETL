
from ._utils import area, clean_up_shit_nulls, daterange, deletable, intrange, price, rate, timestamp


def asset(space):
    """ Transform v1 Space to v2 asset.
    """
    # Heading conversion
    data = {
        "floor_number": space.get("floor_number"),
        "max_contiguous": area(
            value=space.get("max_contiguous"),
            units=space.get("space_available_units")
        ),
        "min_divisible": area(
            value=space.get("min_divisible"),
            units=space.get("space_available_units")
        ),
        "office_percentage": space.get("office_finish_percentage"),
        "space_size": area(
            value=space.get("space_available"),
            units=space.get("space_available_units")
        ),
        "unit_number": space.get("unit_number")
    }
    data.update(timestamp(space))
    data.update(deletable(space))

    # Value conversion
    if not data["max_contiguous"]:
        data["max_contiguous"] = data["space_size"]

    if not data["min_divisible"]:
        data["min_divisible"] = data["space_size"]

    if data["floor_number"] is not None:
        data["floor_number"] = str(data["floor_number"])

    return clean_up_shit_nulls(data)


def lease(space):
    """ Transform v1 Space into v2 lease contract.
    """
    data = {
        "archived": True if space.get("status") == "Archive" else False,
        "available_date": space.get("availability_date"),
        "price": price(
            value=space.get("rate"),
            units="usd"
        ),
        "rate": rate(
            frequency=space.get("rate_frequency"),
            type_=space.get("rate_type")
        ),
        "lease_term": intrange(
            space.get("lease_term"),
            units="months"
        ),
        "tenant_improvement": space.get("ti")
    }
    data.update(timestamp(space))
    data.update(deletable(space))
    return clean_up_shit_nulls(data)


def sublease(space):
    """ Transform v1 Space into v2 sublease contract.
    """
    data = {
        "archived": True if space.get("status") == "Archive" else False,
        "price": price(
            value=space.get("rate"),
            units="usd"
        ),
        "rate": rate(
            frequency=space.get("rate_frequency"),
            type_=space.get("rate_type")
        ),
        "sublease_availability": daterange(space.get("expiration_date"))
    }
    data.update(timestamp(space))
    data.update(deletable(space))
    return clean_up_shit_nulls(data)

