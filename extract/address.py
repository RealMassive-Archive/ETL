
from math import isnan


def address(address):
    if not address:
        return {}
    data = {
#        "address": None,  # TODO
        "city": getattr(address, "city"),
        "county": getattr(address, "county"),
#        "full_state": None,  # TODO
        "state": getattr(address, "state"),
        "street": getattr(address, "street"),
        "zipcode": getattr(address, "zipcode"),
        "geo_lat": getattr(address, "geo_lat"),
        "geo_lon": getattr(address, "geo_lon")
    }
    if isnan(data["geo_lat"]):
        data["geo_lat"] = None
    if isnan(data["geo_lon"]):
        data["geo_lon"] = None
    return data

