
from ._utils import clean_up_shit_nulls


def social(social_):
    """ Transform v1 social_links to v2 social.
    """
    if not social_:
        return {}
    data = {
        "website": social_.get("webpage"),
        "linkedin": social_.get("linkedin"),
        "twitter": social_.get("twitter")
    }
    return clean_up_shit_nulls(data)

