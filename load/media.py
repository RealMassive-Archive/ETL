
import logging

from .. import transform
from ._utils import load_resource, media_sdk, resource, send_metadata, send_to_key_map


# TODO: multiprocess
def run(all_medias):
    for media in all_medias:
        process_media(media)


def process_media(media):
    # Create metadata object in media(upload) service
    metadata = load_metadata(media)
    metadata_id = metadata["id"]
    if not metadata_id:
        logging.warning("Failed to load metadata for: {}".format(media))
        return

    old_media_id = media["id"]
    old_media_urlsafe = media["urlsafe"]

    send_to_key_map(
        v1_type="media",
        v1_key=old_media_id,
        v1_urlsafe=old_media_urlsafe,
        v2_type="metadata",
        v2_key=metadata_id,
    )

    # Create media in apiv2
    new_media = load_media(media, str(media_sdk(metadata_id)))
    send_to_key_map(
        v1_type="media",
        v1_key=old_media_id,
        v1_urlsafe=old_media_urlsafe,
        v2_type="media",
        v2_key=new_media["data"]["id"],
    )
    if media.get("category"):
        # Store category in keymap for attachments
        send_to_key_map(
            v1_type="media",
            v1_key=old_media_id,
            v1_urlsafe=old_media_urlsafe,
            v2_type="category",
            v2_key=media["category"],
        )


def load_media(media, url):
    attrs = transform.media.media(media)
    return load_resource("media", resource("media", url=url, **attrs))


def load_metadata(media):
    attrs = transform.media.metadata(media)
    return send_metadata(**attrs)
