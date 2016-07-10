""" Mock the RealMassive's Upload ndb backend.
"""

from random import randint

import unicodecsv as csv


HEADERS = [
    "id",
    "blobkey",
    "url",
    "uploaded_by",
    "filename",
    "mime_type",
    "height",
    "width",
    "file_size",
    "legal_status",
    "rm_api_id",
]

ID_LENGTH = 16


class MediaService(object):
    def __init__(self):
        self.metadata = []

    def insert(self, **kwargs):
        id_ = randint(10**(ID_LENGTH - 1), 10**ID_LENGTH - 1)
        kwargs.update({"id": id_})
        self.metadata.append(kwargs)
        return kwargs

    def dump(self, filepath="/tmp/metadata.csv"):
        with open(filepath, "w") as f:
            writer = csv.DictWriter(f, HEADERS)
            writer.writeheader()
            writer.writerows(self.metadata)
