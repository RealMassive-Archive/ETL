import csv


class KeyMap(object):

    def __init__(self):
        self.keymap = {}
        self.rows = []

    def insert(self, v1_key, v1_type, v1_urlsafe, v2_key, v2_type):
        self.rows.append((v1_key, v1_type, v1_urlsafe, v2_key, v2_type))
        self.keymap[(v1_type, v1_key)] = v2_key

    def get_new(self, v1_type, v2_type, v1_key):
        return self.keymap.get((v1_type, v1_key))

    def dump(self, out_file_path):
        with open(out_file_path, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(('v1_key', 'v1_type', 'v1_urlsafe', 'v2_key', 'v2_type'))
            for row in self.rows:
                writer.writerow(row)
