# ETL
## Instructions
1) Extract
To extract data (retrieve all entities and dump to \n delimited json):
```python
# iPython shell in to the desired server you wish to extract from
import json

from etl import extract


for model in [Building, Space, Organization, User, Media]:
    model_name = model.__class__.__name__
    all_ents = []
    for ents in extract.get_entities(model):
        all_ents.extend(ents)
    with open("{}.json".format(model_name), "w") as f:
        f.write("\n".join(map(json.dumps, all_ents)))
```


2) Load
```
1) Run the following services: realmassive (for shell), V1V2KeyMapping and apiv2
2) Edit config.py with appropriate endpoints from step 1
```

```python
from etl import load

# Lists of entities from pickle
all_buildings = map(json.loads, open("buildings.json").read().splitlines())
all_spaces = map(json.loads, open("spaces.json").read().splitlines())
all_organizations = map(json.loads, open("organizations.json").read().splitlines())
all_users = map(json.loads, open("users.json").read().splitlines())

# Base entities
load.building.run(all_buildings)  # Loads all building assets
load.space.run(all_spaces)  # Loads all space assets, leases and subleases
load.organization.run(all_organization)  # Loads all organizations and teams
load.user.run(all_users)  # Loads all users and cards
load.media.run(all_media)  # Loads all media and metadata

# Create memberships and membership permissions
for user in all_users:
    load.relationships.membership(user)

# Relate space assets to buildings
for space in all_spaces:
    load.relationships.building_space(spaces)

# =============
# Untested land
# =============

# Relate contacts to listings
for space in all_spaces:
    load.relationships.listing_contacts(space)

# Relate organizations to listings
for space in all_spaces:
    load.relationships.listing_organization(space)

# Relate card to organization
for organization in all_organizations:
    load.relationships.organization_card(organization)

# Spaces/listings Permissions
for space in all_spaces:
    load.relationships.entity_permission("spaces", "spaces", space, permission="admin")
    if space.space_type == "lease":
        load.relationships.entity_permission("spaces", "leases", space, permission="admin")
    elif space.space_type == "sublease":
        load.relationships.entity_permission("spaces", "subleases", space, permission="admin")

# Building Permissions
for building in all_buildings:
    load.relationships.entity_permission("buildings", "buildings", building, permission="admin")

# Organization Permissions
for organization in all_organizations:
    load.relationships.entity_permission("organizations", "organizations", organization, permission="admin")

# Attachments
for entity in all_buildings + all_spaces + all_organizations + all_users:
    load.relationships.entity_attachments(entity)
```
