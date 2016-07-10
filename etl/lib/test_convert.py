import os

from datadiff.tools import assert_equal

from convert import ApiV2


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
    'type': 'buildings'
}


def test_flatten_resource():
    apiv2 = ApiV2()

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

    actual = apiv2._flatten_resource(resource, resource_id=0)

    assert_equal(actual, expected)


def test_apiv2():
    apiv2 = ApiV2()
    apiv2.create_resource(resource)
    apiv2.create_resource(resource)
    outfile = '/tmp/building.csv'
    apiv2.dump_resource('buildings', outfile)
    assert os.path.exists(outfile)

    apiv2.create_relationship('building', 10, 'spaces', 15)
    outfile2 = '/tmp/building_space.csv'
    apiv2.dump_relationship('building', 'space', outfile2)
    assert os.path.exists(outfile2)
