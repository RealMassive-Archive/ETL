tables = [
    'building',
    'space',
    'organization',
    'lease',
    'team',
    'user',
    'card',
    'card_user',
    'sublease',
    'membership',
    'lease_space',
    'space_sublease',
    'building_space',
    'contact',
    'card_contact',
    'card_organization',
    'contact_lease',
    'contact_sublease',
    'membership_team',
    'membership_user',
    'lease_organization',
    'organization_sublease',
#    'media',
#    'attachment',
#    'attachment_building',
#    'attachment_card',
#    'attachment_lease',
#    'attachment_media',
#    'attachment_organization',
#    'attachment_space',
#    'attachment_sublease',
    'permission',
    'building_permission',
    'card_permission',
    'contact_permission',
    'lease_permission',
    'membership_permission',
#    'media_permission',
#    'attachment_permission',
    'organization_permission',
    'permission_space',
    'permission_sublease',
    'permission_team',
    'permission_user'
]

fmt = """COPY "{table}" FROM '/tmp/{table}.csv' DELIMITER ',' CSV HEADER;"""

def generate_sql():
    statements = []
    for table in tables:
        statements.append(fmt.format(table=table))
    return statements


if __name__ == '__main__':
    print '\n'.join(generate_sql())
