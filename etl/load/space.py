
from .. import transform
from ._utils import load_resource, relate_child_to_parent, resource, send_to_key_map


def run(all_spaces):
    for space in all_spaces:
        process_space(space)


def process_space(space):
    # Asset
    new_space = load_space_asset(space)
    send_to_key_map(
        v1_type="spaces",
        v1_key=space["id"],
        v1_urlsafe=space["urlsafe"],
        v2_type="spaces",
        v2_key=new_space["data"]["id"],
    )

    # Listing
    space_type = space.get("space_type")
    if space_type in ["lease", "sublease"]:
        space_type = space_type + "s"
        listing = load_space_listing(space_type, space)
        send_to_key_map(
            v1_type="spaces",
            v1_key=space["id"],
            v1_urlsafe=space["urlsafe"],
            v2_type=space_type,
            v2_key=listing["data"]["id"],
        )
        relate_listing_to_space(new_space["data"]["id"], listing)


def load_space_asset(space):
    attrs = transform.space.asset(space)
    return load_resource("spaces", resource("spaces", **attrs))


def load_space_listing(listing_type, space):
    attrs = getattr(transform.space, listing_type[:-1])(space)
    return load_resource(
        listing_type,
        resource(listing_type, **attrs)
    )


def relate_listing_to_space(new_space_id, listing):
    return relate_child_to_parent("spaces", new_space_id, listing["data"]["type"], listing)

