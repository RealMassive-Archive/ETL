from datadiff.tools import assert_equal

from convert import flatten_resource


def test_flatten_resource():
    resource = {
        'attributes': {
            'address': {
                'address': '1925 Airport Boulevard, Austin, TX, 78722', 
                'city': 'Austin', 
                'county': 'Travis County', 
                'full_state': 'TX', 
                'latitude': 30.283297, 
                'longitude': -97.703913, 
                'state': 'TX', 
                'street': '1925 Airport Boulevard', 
                'zipcode': '78722'
            }, 
            'build_status': 'Existing', 
            'building_class': 'A', 
            'building_size': {
                'units': 'sf', 
                'value': '12345.000000'
            }, 
            'building_type': 'Office', 
            'created': '2016-06-30T02:19:08.238321+00:00', 
            'title': 'Taco Bell', 
            'updated': '2016-06-30T02:19:08.238321+00:00'
        }, 
        'id': '1283734909424239705', 
        'type': 'buildings'
    }

    expected = {
        'build_status': 'Existing',
        'updated': '2016-06-30T02:19:08.238321+00:00',
        '_address__address__street': '1925 Airport Boulevard',
        '_address__address__county': 'Travis County',
        '_address__address__longitude': -97.703913,
        '_address__address__city': 'Austin',
        '_address__address__state': 'TX',
        'title': 'Taco Bell',
        '_address__address__latitude': 30.283297,
        'created': '2016-06-30T02:19:08.238321+00:00',
        '_address__address__zipcode': '78722',
        'building_type': 'Office',
        '_address__address__full_state': 'TX',
        '_building_size__area__units': 'sf',
        '_address__address__address': '1925 Airport Boulevard, Austin, TX, 78722',
        'building_class': 'A',
        '_building_size__area__value': '12345.000000'
    }

    actual = flatten_resource(resource)

    assert_equal(actual, expected)
