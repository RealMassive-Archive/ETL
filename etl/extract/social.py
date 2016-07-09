
def social(social_):
    if not social_:
        return {}
    data = {
        "website": social_.get("webpage"),
        "linkedin": social_.get("linkedin"),
        "twitter": social_.get("twitter")
    }
    return data

