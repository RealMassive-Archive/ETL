
from ._utils import identifiers, timestamp


def media(media):
    data = {
        "blobkey": getattr(media, "blobkey"),
        "category": getattr(media, "category"),
        "description": getattr(media, "description"),
        "file_size": getattr(media, "size"),
        "filename": getattr(media, "filename"),
        "height": getattr(media, "height"),
        "ip_status": getattr(media, "ip_status"),
        "mime_type": getattr(media, "mime_type"),
        "preview_info": getattr(media, "preview_info"),
        "raw_url": getattr(media, "raw_url"),
        "size": getattr(media, "size"),
        "title": getattr(media, "title"),
        "user_approved": getattr(media, "approved"),
        "width": getattr(media, "width"),
#        "video_tag": getattr(media, ""),  # TODO
    }
    data.update(timestamp(media))
    data.update(identifiers(media))

    # Added uploaded_by_email for metadata
    uploaded_by = media.uploaded_by and media.uploaded_by.get()
    data["uploaded_by_email"] = uploaded_by.email if uploaded_by else None

    if data["preview_info"]:
        data["preview_info"] = getattr(data["preview_info"], "url")

    if data["blobkey"]:
        data["blobkey"] = str(data["blobkey"])

    return data

