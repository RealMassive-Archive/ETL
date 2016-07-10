
from datetime import datetime
import logging


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


def area(value=None, units="sqft"):
    if units and "sf" in units.lower():
        units = "sqft"
    elif units and "ac" in units.lower():
        units = "acre"
    else:
        # Default to sqft
        units = "sqft"

    try:
        return {
            "value": float(value),
            "units": units
        }
    except TypeError, ValueError:
        logging.warning("Failed to coerce area: {}".format(value))
        return {}


def daterange(value):
    # NOTE: currently only used for sublease_availability, a single timestamp
    return {
        "start": value,
        "end": None,
    }


def deletable(entity):
    return {"deleted": False}


def intrange(value, units="months"):
    # NOTE: currently only used for lease_term, a single integer
    if value is None:
        return None
    return {
        "min": value,
        "max": value,
        "units": units
    }


def length(value=None, units="ft"):
    if value is None:
        return {}
    try:
        return {
            "value": float(value),
            "units": units
        }
    except TypeError, ValueError:
        logging.warning("Failed to coerce length: {}".format(value))
        return {}


def price(value=None, units="usd"):
    try:
        return {
            "value": float(value),
            "units": units
        }
    except TypeError, ValueError:
        logging.warning("Failed to coerce price: {}".format(value))
        return {}


def rate(frequency=None, type_=None):
    try:
        frequency = frequency.lower()
        if type_ == "n/a":
            type_ = None
        return {
            "frequency": frequency,
            "type": type_
        }
    except AttributeError, ValueError:
        logging.warning("Failed to coerce rate:\n'frequency': {}\n'type': {}".format(frequency, type_))
        return {}


def timestamp(entity):
    return {
        "created": entity.get("created_at") or datetime.utcnow().isoformat(),
        "updated": entity.get("edited_at") or datetime.utcnow().isoformat()
    }

