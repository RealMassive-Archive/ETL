def _infer_type(parent_key):
    if parent_key.endswith('size'):
        return 'area'
    elif parent_key == 'price':
        return 'currency'
    elif parent_key == 'clear_height':
        return 'length'
    elif parent_key == 'rate':
        return 'rate'
    elif parent_key == 'address':
        return 'address'
    elif parent_key == 'lease_term':
        return 'integer_range'
    elif parent_key == 'sublease_availability':
        return 'date_range'


def _format_key(parent_key, child_key):
    type_ = _infer_type(parent_key)
    return '_' + parent_key + '__' + type_ + '__' + child_key


def _flatten(d):
    new = {}
    for k, v in d.iteritems():
        if isinstance(v, dict):
            for ck, cv in v.iteritems():
                key = _format_key(k, ck)
                new[key] = cv
        else:
            new[k] = v
    return new


def flatten_resource(resource):
    return _flatten(resource['attributes'])
