
import logging

from .. import transform
from ._utils import get_new_from_key_map, load_resource, relate_child_to_parent, resource, send_to_key_map, timestamp


def run(all_users):
    for user in all_users:
        process_user(user)


def process_user(user):
    # User
    new_user = load_user(user)
    if not new_user:
        return
    old_user_id = user["id"]
    old_user_urlsafe = user["urlsafe"]
    send_to_key_map(
        v1_type="users",
        v1_key=old_user_id,
        v1_urlsafe=old_user_urlsafe,
        v2_type="users",
        v2_key=new_user["data"]["id"],
    )

    # Card
    card = load_card(user)
    if card:
        send_to_key_map(
            v1_type="users",
            v1_key=old_user_id,
            v1_urlsafe=old_user_urlsafe,
            v2_type="cards",
            v2_key=card["data"]["id"],
        )
        relate_child_to_parent("users", new_user["data"]["id"], "cards", card)


def load_user(user):
    attrs = transform.user.user(user)
    try:
        return load_resource("users", resource("users", **attrs))
    except Exception as e:
        logging.error("Failed to create user: {}".format(e))
        return None


def load_card(user):
    attrs = transform.user.card(user)
    email = attrs.get("email")
    if email and "@realmassive" in email:
        logging.warning("Skipping card for {}".format(email))
        return None
    return load_resource("cards", resource("cards", **attrs))


def load_photo(user):
    """ Loads user photos into apiv2 Media.
        To be run before any attachment steps
    """
    old_user_id = user["id"]

    new_card_id = get_new_from_key_map("users", "cards", old_user_id)
    if not new_card_id:
        # Only ingest user photo if there's a card to which it belongs
        return

    # Photo
    user_photo = user.get("photo")
    if user_photo and user_photo != "/static/img/default_profile.jpg":
        # Create media in apiv2
        media_attrs = {
	    "url": user_photo,
	}
	media_attrs.update(timestamp())
        media = load_resource("media", resource("media", **media_attrs))
        send_to_key_map(
            v1_type="media",
            v1_key=user_photo,
            v1_urlsafe=user_photo,
            v2_type="media",
            v2_key=media["data"]["id"],
        )

