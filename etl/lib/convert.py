""" Helpers to convert apiv2 resources into their underlying csv format.
"""

csv_headers = {
    'attachments': ('category', 'id', 'precedence', 'deleted', 'created',
        'updated'),

    'buildings': ('id', '_address__address__address', '_address__address__city',
        '_address__address__county', '_address__address__full_state',
        '_address__address__latitude', '_address__address__longitude',
        '_address__address__state', '_address__address__street',
        '_address__address__zipcode', 'air_conditioned', 'build_status',
        'building_class', '_building_size__area__units',
        '_building_size__area__value', 'building_subtype', 'building_type',
        '_clear_height__length__units', '_clear_height__length__value',
        'description', 'floor_count', 'leed_rating', '_lot_size__area__units',
        '_lot_size__area__value', 'signage', 'sprinkler', 'tenancy', 'title',
        'year_built', 'year_renovated', 'zoning', 'deleted', 'created',
        'updated'),

    'cards': ('bio', 'ccim_member', 'ccim_number', 'email', 'first_name', 'id',
        'last_name', 'license_number', 'mobile_phone', 'phone', 'sior_member',
        'sior_number', '_social__social_links__linkedin',
        '_social__social_links__twitter', '_social__social_links__website',
        'title', 'deleted', 'created', 'updated'),

    'contacts': ('id', 'precedence', 'role', 'deleted', 'created', 'updated'),

    'land': ('_address__address__address', '_address__address__city',
        '_address__address__county', '_address__address__full_state',
        '_address__address__latitude', '_address__address__longitude',
        '_address__address__state', '_address__address__street',
        '_address__address__zipcode', 'description', 'id',
        '_land_size__area__units', '_land_size__area__value',
        'land_type', 'zoning', 'deleted', 'created', 'updated'),

    'leases': ('available_date', 'id', '_lease_term__integer_range__max',
        '_lease_term__integer_range__min', '_lease_term__integer_range__units',
        '_price__currency__units', '_price__currency__value',
        '_rate__rate__frequency', '_rate__rate__type', '_rate__rate__units',
        'tenant_improvement', 'deleted', 'archived', 'created', 'updated'),

    'media': ('description', 'file_size', 'height', 'id', 'ip_status',
        'mime_type', 'preview', 'title', 'url', 'user_approved',
        'video_tag', 'width', 'deleted', 'created', 'updated'),

    'memberships': ('default', 'id', 'membership', 'deleted', 'created',
        'updated'),

    'organizations': ('_address__address__address', '_address__address__city',
        '_address__address__county', '_address__address__full_state',
        '_address__address__latitude', '_address__address__longitude',
        '_address__address__state', '_address__address__street',
        '_address__address__zipcode','bio', 'email', 'id', 'name', 'phone',
        '_social__social_links__linkedin', '_social__social_links__twitter',
        '_social__social_links__website', 'deleted', 'created', 'updated'),

    'parcels': ('description', 'id', 'name', '_parcel_size__area__units',
        '_parcel_size__area__value', 'parcel_type', 'deleted',
        'created', 'updated'),

    'permissions': ('id', 'permission', 'deleted', 'created', 'updated'),

    'sales': ('cap_rate', 'id', 'occupancy', '_price__currency__units',
        '_price__currency__value', '_rate__rate__frequency',
        '_rate__rate__type', '_rate__rate__units', 'deleted',
        'archived', 'created', 'updated'),

    'spaces': ('id', 'description', 'floor_number',
        '_max_contiguous__area__units', '_max_contiguous__area__value',
        '_min_divisible__area__units', '_min_divisible__area__value',
        'office_percentage', '_space_size__area__units',
        '_space_size__area__value', 'space_subtype', 'space_type',
        'unit_number', 'deleted', 'created', 'updated'),

    'subleases': ('id', '_price__currency__units', '_price__currency__value',
        '_rate__rate__frequency', '_rate__rate__type', '_rate__rate__units',
        '_sublease_availability__date_range__end',
        '_sublease_availability__date_range__start',
        'deleted', 'archived', 'created', 'updated'),

    'teams': ('id', 'name', 'deleted', 'created', 'updated'),

    'users': ('email', 'id', 'superuser', 'tos_status', 'deleted', 'created',
        'updated')
}


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
    elif parent_key == 'social':
        return 'social_links'
    elif parent_key == 'max_contiguous':
        return 'area'
    elif parent_key == 'min_divisible':
        return 'area'


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
    """ flatten v2 resource into dictionary compatible with csv.DictWriter

        When used in conjunction with `csv_headers` above can be used to
        to serialize v2 resources to csv.
    """
    return _flatten(resource['attributes'])
