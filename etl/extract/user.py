
from ._utils import identifiers, key, timestamp
from .social import social


def user(user_):
    data = {
        "bio": getattr(user_, "bio"),
        "ccim_number": getattr(user_, "ccim_number"),
        "email": getattr(user_, "email"),
        "first_name": getattr(user_, "first_name"),
        "last_name": getattr(user_, "last_name"),
        "license_number": getattr(user_, "license_number"),
        "mobile_phone": getattr(user_, "mobile_phone"),
        "phone": getattr(user_, "phone"),
        "photo": getattr(user_, "photo"),
        "sior_number": getattr(user_, "sior_number"),
        "social_links": social(getattr(user_, "social_links")),
        "title": getattr(user_, "title"),
    }
    data.update(timestamp(user_))
    data.update(identifiers(user_))
    data.update({
        "organizations": map(lambda x: key(x), getattr(user_, "organizations", []))
    })

    return data


