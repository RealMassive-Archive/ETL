import json
import tarfile
import logging

from etl import load
from etl.config import APIV2 as apiv2


# disable log messages
logging.basicConfig(level=logging.CRITICAL)


# load compressed data tar file
data = tarfile.open('/tmp/data.tar.gz', 'r:gz')

#TODO: created, updated, deleted, archived MUST be set for all resources

# load buildings
print 'dumping buildings...'
all_buildings = map(json.loads, data.extractfile('jsons/buildings.json').readlines())
load.building.run(all_buildings)  # loads all building assets
apiv2.dump_resource('buildings', '/tmp/building.csv')
print 'DONE'

# load spaces
print 'dumping spaces, leases, and subleases...'
all_spaces = map(json.loads, data.extractfile('jsons/spaces.json').readlines())
load.space.run(all_spaces)  # loads all space assets, leases and subleases
apiv2.dump_resource('spaces', '/tmp/space.csv')
apiv2.dump_resource('leases', '/tmp/lease.csv')
apiv2.dump_resource('subleases', '/tmp/sublease.csv')
print 'DONE'

# load organizations
print 'dumping organizations, and teams...'
all_organizations = map(json.loads, data.extractfile('jsons/organizations.json').readlines())
load.organization.run(all_organizations)  # loads all organizations and teams
apiv2.dump_resource('organizations', '/tmp/organization.csv')
apiv2.dump_resource('teams', '/tmp/team.csv')
print 'DONE'

# load users
print 'dumping users, and cards...'
all_users = map(json.loads, data.extractfile('jsons/users.json').readlines())
load.user.run(all_users)  # loads all users and cards
apiv2.dump_resource('users', '/tmp/user.csv')
apiv2.dump_resource('cards', '/tmp/card.csv')
apiv2.dump_relationship('card', 'user', '/tmp/card_user.csv')
print 'DONE'

# create memberships and membership permissions
print 'dumping memberships...'
for user in all_users:
    load.relationships.membership(user)
apiv2.dump_resource('memberships', '/tmp/membership.csv')
print 'DONE'

# relate spaces to buildings
print 'dumping building space relationships...'
for space in all_spaces:
    load.relationships.building_space(space)
apiv2.dump_relationship('building', 'space', '/tmp/building_space.csv')
print 'DONE'

# relate contacts to listings
print 'dumping contact to lease and sublease relationships...'
for space in all_spaces:
    load.relationships.listing_contacts(space)
apiv2.dump_resource('contacts', '/tmp/contact.csv')
apiv2.dump_relationship('card', 'contact', '/tmp/card_contact.csv')
apiv2.dump_relationship('contact', 'lease', '/tmp/contact_lease.csv')
apiv2.dump_relationship('contact', 'sublease', '/tmp/contact_sublease.csv')
print 'DONE'

# relate organizations to listings
print 'dumping organization to lease and sublease relationships...'
for space in all_spaces:
    load.relationships.listing_organization(space)
# TODO: MUST create these relationships. Would expect them to be populated
apiv2.dump_relationship('lease', 'organization', '/tmp/lease_organization.csv')
apiv2.dump_relationship('organization', 'sublease', '/tmp/organization_sublease.csv')
print 'DONE'

# relate card to organization
print 'dumping organization to card relationships...'
for organization in all_organizations:
    load.relationships.organization_card(organization)
apiv2.dump_relationship('card', 'organization', '/tmp/card_organization.csv')
print 'DONE'

## =============
## Untested land
## =============

## Spaces/listings Permissions
#for space in all_spaces:
    #load.relationships.entity_permission("spaces", "spaces", space, permission="admin")
    #if space.space_type == "lease":
        #load.relationships.entity_permission("spaces", "leases", space, permission="admin")
    #elif space.space_type == "sublease":
        #load.relationships.entity_permission("spaces", "subleases", space, permission="admin")

## Building Permissions
#for building in all_buildings:
    #load.relationships.entity_permission("buildings", "buildings", building, permission="admin")

## Organization Permissions
#for organization in all_organizations:
    #load.relationships.entity_permission("organizations", "organizations", organization, permission="admin")

## Media
# load.media.run(all_media)  # Loads all media and metadata

## Attachments
#for entity in all_buildings + all_spaces + all_organizations + all_users:
    #load.relationships.entity_attachments(entity)
