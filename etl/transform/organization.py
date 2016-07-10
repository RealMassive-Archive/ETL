
from ._utils import clean_up_shit_nulls, deletable, timestamp
from .address import address
from .social import social


def organization(organization_):
    """ Transform v1 Organization to v2 organization.
    """
    data = {
        "address": address(organization_.get("address")),
        "bio": organization_.get("bio"),
        "email": organization_.get("email"),
        "name": organization_.get("name"),
        "phone": organization_.get("phone"),
        "social": social(organization_.get("social_links")),
    }
    data.update(timestamp(organization_))
    data.update(deletable(organization_))
    return clean_up_shit_nulls(data)


def team(organization_):
    """ Transform v1 Organization to v2 Team.
    """
    data = {
        "name": organization_.get("name")
    }
    data.update(timestamp(organization_))
    data.update(deletable(organization_))
    return clean_up_shit_nulls(data)

