
from ._utils import identifiers, key, timestamp
from .address import address
from .social import social


def organization(organization_):
    data = {
        "address": address(getattr(organization_, "address")),
        "bio": getattr(organization_, "bio"),
        "email": getattr(organization_, "email"),
        "name": getattr(organization_, "name"),
        "phone": getattr(organization_, "phone"),
        "social_links": social(getattr(organization_, "social_links")),
    }
    data.update(timestamp(organization_))
    data.update(identifiers(organization_))
    if organization_.logo:
        data.update({"logo": key(organization_.logo)})

    owner = organization_.owner and organization_.owner.get()
    data["owner_email"] = owner.email if owner else None
    data["owner"] = key(owner.key) if owner else None
    data.update({
        "admins": map(lambda x: key(x), getattr(organization_, "admins", []))
    })
    data.update({
        "members": map(lambda x: key(x), getattr(organization_, "members", []))
    })
    return data

