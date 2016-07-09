from . import building
from . import media
from . import organization
from . import space
from . import user


def get_entities(model_type, cursor=None):
    serializers = {
        "Building": building.building,
        "Media": media.media,
        "Organization": organization.organization,
        "Space": space.space,
        "User": user.user,
    }
    limit = 500
    more = True
    while more:
        results, cursor, more = model_type.query().fetch_page(limit, start_cursor=cursor)
        results = map(serializers[model_type.__name__], results)
        yield results

