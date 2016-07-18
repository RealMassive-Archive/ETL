
import requests
import unicodecsv as csv


class KeyMap(object):

    def __init__(self):
        self.keymap = {}
        self.rows = []

    def insert(self, v1_key, v1_type, v1_urlsafe, v2_key, v2_type):
        self.rows.append((v1_key, v1_type, v1_urlsafe, v2_key, v2_type))
        self.keymap[(v1_type, v2_type, v1_key)] = v2_key

    def get_new(self, v1_type, v2_type, v1_key):
        return self.keymap.get((v1_type, v2_type, v1_key))

    def dump(self, out_file_path):
        with open(out_file_path, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(('v1_key', 'v1_type', 'v1_urlsafe', 'v2_key', 'v2_type'))
            writer.writerows(self.rows)


class RemoteKeyMap(object):
    """ Like KeyMap, but hits a remote server.
    """
    def __init__(self, location="https://key-mapper-staging.realmassive.com"):
        self.location = location

    def insert(self, v1_key, v1_type, v1_urlsafe, v2_key, v2_type):
        raise NotImplementedError("No dumps for you.")

    def get_new(self, v1_type, v2_type, v1_key):
        r = requests.get(self.location + "/{}/{}".format(v1_type, v1_key))
        r.raise_for_status()
        data = r.json()
        for mapping in data["results"]:
            if mapping["v2_type"] == v2_type:
                return mapping["v2_key"]
        return None

    def dump(self, out_file_path):
        raise NotImplementedError("No dumps for you.")

