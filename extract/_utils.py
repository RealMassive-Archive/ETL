
import datetime
import logging


def date(value):
    """ Convert all things to datetimestamps.
    """
    if isinstance(value, datetime.date):
        return datetime.datetime.fromordinal(value.toordinal()).isoformat()
    elif isinstance(value, datetime.datetime):
        return value.isoformat()
    else:
        logging.warning("Failed to coerce date: {}".format(value))
        return None


def identifiers(entity):
    return {
        "id": key(entity.key),
        "urlsafe": urlsafe(entity.key),
        "class": entity.__class__.__name__
    }


def key(key_):
    if not key_:
        return None
    try:
        return int(key_.id())
    except ValueError:
        logging.warning("Failed to get id from key: {}".format(key_))
        return None


def timestamp(entity):
    data = {
        "created_at": getattr(entity, "created_at"),
        "edited_at": getattr(entity, "edited_at")
    }
    if data["created_at"]:
        data["created_at"] = data["created_at"].isoformat()
    if data["edited_at"]:
        data["edited_at"] = data["edited_at"].isoformat()
    return data


def urlsafe(key_):
    return key_.urlsafe()
