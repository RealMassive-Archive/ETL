
import json

from ._utils import clean_up_shit_nulls, deletable, timestamp


def media(media):
    """ Transform v1 media into v2 media.
    """
    data = {
        "description": media.get("description"),
        "file_size": media.get("size"),
        "height": media.get("height"),
        "ip_status": media.get("ip_status"),
        "mime_type": media.get("mime_type"),
        "preview": media.get("preview_info"),
        "title": media.get("title"),
        "user_approved": media.get("approved"),
        "video_tag": json.dumps(media.get("video_tags", [])),
        "width": media.get("width"),
    }
    data.update(timestamp(media))
    data.update(deletable(media))

    if data["file_size"] is not None:
        data["file_size"] = str(data["file_size"])

    if data["ip_status"] and data["ip_status"] == "UNVERIFIED":
        data["ip_status"] = "PENDING"

    return clean_up_shit_nulls(data)


def metadata(media):
    data = {
        "blobkey": media.get("blobkey"),
        "url": media.get("raw_url"),
        "uploaded_by": media.get("uploaded_by_email"),
        "filename": media.get("filename"),
        "mime_type": media.get("mime_type"),
        "height": media.get("height"),
        "width": media.get("width"),
        "file_size": media.get("size"),
        "legal_status": media.get("ip_status"),
        # "rm_api_id"  # TODO
    }
    if data["file_size"] is not None:
        data["file_size"] = str(data["file_size"])
    if data["legal_status"] and data["legal_status"] == "UNVERIFIED":
        data["legal_status"] = "PENDING"
    return clean_up_shit_nulls(data)
