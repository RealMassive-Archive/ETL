
from ._utils import clean_up_shit_nulls, deletable, timestamp
from .social import social


def user(user_):
    data = {
        "email": user_.get("email")
    }
    data.update(timestamp(user_))
    data.update(deletable(user_))
    return clean_up_shit_nulls(data)


def card(user_):
    """ Transform v1 user_ to v2 Contact.
    """
    # Heading conversion
    data = {
        "bio": user_.get("bio"),
        "ccim_number": user_.get("ccim_number"),
        "license_number": user_.get("license_number"),
        "email": user_.get("email"),
        "first_name": user_.get("first_name"),
        "last_name": user_.get("last_name"),
        "mobile_phone": user_.get("mobile_phone"),
        "phone": user_.get("phone"),
        "sior_number": user_.get("sior_number"),
        "social": user_.get("social_links"),
        "title": user_.get("title")
    }
    data.update(timestamp(user_))
    data.update(deletable(user_))

    # Value conversion
    if data["ccim_number"]:
        data["ccim_member"] = True
    if data["sior_number"]:
        data["sior_member"] = True
    if data["social"]:
        data["social"] = social(data["social"])

    return clean_up_shit_nulls(data)

