
from math import isnan

from ._utils import clean_up_shit_nulls


def address(address):
    """ Transform v1 address to v2.
    """
    if not address:
        return {}
    data = {
#        "address": None,  # TODO
        "city": address.get("city"),
        "county": address.get("county"),
#        "full_state": None,  # TODO
        "state": address.get("state"),
        "street": address.get("street"),
        "zipcode": address.get("zipcode"),
        "latitude": address.get("geo_lat"),
        "longitude": address.get("geo_lon")
    }
    return clean_up_shit_nulls(data)

