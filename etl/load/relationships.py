
from ._utils import get_new_from_key_map, load_resource, relate_child_to_parent, relationship_resource, resource


def entity_permission(v1_type, v2_type, entity, permission="admin"):
    """ Create the appropriate permission between a team and entity.
        Works for:
            * Building
            * Space
                * Lease
                * Sublease
            * Organization
    """
    old_entity_id = entity["id"]

    new_entity_id = get_new_from_key_map(v1_type, v2_type, old_entity_id)
    if not new_entity_id:
        return

    entity_class = entity.get("class")
    if entity_class == "Organization":
        # entity is an Organization, use its id
        old_organization_id = old_entity_id
    elif entity_class == "Space":
        # get old organization through v1 attribute (this attribute was manually added during extract phase)
        old_organization_id = entity.get("organization")
    elif entity_class == "Building":
        old_organization_id = entity["manager"]
    if not old_organization_id:
        return

    new_team_id = get_new_from_key_map("organizations", "teams", old_organization_id)
    if not new_team_id:
        return

    permission_attrs = relationship_resource(
        {"data": {"type": "teams", "id": new_team_id}},
        {"data": {"type": v2_type, "id": new_entity_id}},
        permission=permission
    )
    return load_resource("permissions", resource("permissions", **permission_attrs))


def building_space(space):
    old_space_id = space["id"]

    new_space_id = get_new_from_key_map("spaces", "spaces", old_space_id)
    if not new_space_id:
        return

    old_building_id = space.get("building")
    if not old_building_id:
        return

    new_building_id = get_new_from_key_map("buildings", "buildings", old_building_id)
    relate_child_to_parent("buildings", new_building_id, "spaces", {"data": {"type": "spaces", "id": new_space_id}})


def listing_contacts(space):
    space_type = space.get("space_type")
    if space_type not in ["lease", "sublease"]:
        return
    space_type = space_type + "s"

    old_space_id = space["id"]
    if not old_space_id:
        return

    new_listing_id = get_new_from_key_map("spaces", space_type, old_space_id)
    if not new_listing_id:
        return

    old_organization_id = space.get("organization")
    if old_organization_id:
        new_team_id = get_new_from_key_map("organizations", "teams", old_organization_id)
    else:
        new_team_id = None

    for i, old_user_id in enumerate(space.get("contacts")):
        if not old_user_id:
            continue

        new_card_id = get_new_from_key_map("users", "cards", old_user_id)
        if not new_card_id:
            continue

        contact_attrs = relationship_resource(
            {"data": {"type": "cards", "id": new_card_id}},
            {"data": {"type": space_type, "id": new_listing_id}},
            precedence=float(i)
        )
        contact = load_resource("contacts", resource("contacts", **contact_attrs))

        if new_team_id:
            # Permission
            permission_attrs = relationship_resource(
                {"data": {"type": "teams", "id": new_team_id}},
                {"data": {"type": "contacts", "id": contact["data"]["id"]}},
                permission="admin"
            )
            load_resource("permissions", resource("permissions", **permission_attrs))


def listing_organization(space):
    space_type = space.get("space_type")
    if space_type not in ["lease", "sublease"]:
        return
    space_type = space_type + "s"

    old_space_id = space["id"]
    if not old_space_id:
        return

    new_listing_id = get_new_from_key_map("spaces", space_type, old_space_id)
    if not new_listing_id:
        return

    old_organization_id = space.get("organization")
    if not old_organization_id:
        return

    new_organization_id = get_new_from_key_map("organizations", "organizations", old_organization_id)
    if not new_organization_id:
        return

    relate_child_to_parent(space_type, new_listing_id, "organizations", {"data": {"type": "organizations", "id": new_organization_id}})


def membership(user):
    old_user_id = user["id"]

    new_user_id = get_new_from_key_map("users", "users", old_user_id)
    if not new_user_id:
        return

    for i, old_organization_id in enumerate(user.get("organizations", [])):
        if not old_organization_id:
            continue

        new_team_id = get_new_from_key_map("organizations", "teams", old_organization_id)
        if not new_team_id:
            continue

        membership_attrs = relationship_resource(
            {"data": {"type": "teams", "id": new_team_id}},
            {"data": {"type": "users", "id": new_user_id}},
            default=True if i == 0 else False,
            membership="accepted"
        )
        membership = load_resource("memberships", resource("memberships", **membership_attrs))

        # Permission (Membership)
        membership_permission_attrs = relationship_resource(
            {"data": {"type": "teams", "id": new_team_id}},
            {"data": {"type": "memberships", "id": membership["data"]["id"]}},
            permission="admin"
        )
        load_resource("permissions", resource("permissions", **membership_permission_attrs))

        # Permission (User) READ ONLY
        user_permission_attrs =  relationship_resource(
            {"data": {"type": "teams", "id": new_team_id}},
            {"data": {"type": "users", "id": new_user_id}},
            permission="read"
        )
        load_resource("permissions", resource("permissions", **user_permission_attrs))

        # Permission (Card)
        new_card_id = get_new_from_key_map("users", "cards", old_user_id)
        if not new_card_id:
            continue

        card_permission_attrs =  relationship_resource(
            {"data": {"type": "teams", "id": new_team_id}},
            {"data": {"type": "cards", "id": new_card_id}},
            permission="admin"
        )
        load_resource("permissions", resource("permissions", **card_permission_attrs))


def organization_card(organization):
    old_organization_id = organization["id"]

    new_organization_id = get_new_from_key_map("organizations", "organizations", old_organization_id)
    if not new_organization_id:
        return

    org_people = [organization.get("owner")] + organization.get("admins") + organization.get("members")
    for member_id in org_people:
        old_user_id = member_id
        if not old_user_id:
            continue

        new_card_id = get_new_from_key_map("users", "cards", old_user_id)
        if not new_card_id:
            continue

        relate_child_to_parent("organizations", new_organization_id, "cards", {"data": {"type": "cards", "id": new_card_id}})


def entity_attachments(entity):
    """ Create attachments for entities that
    """
    old_entity_id = entity["id"]
    # Get relevant information from old entity
    if entity.get("class") in "Building":
        new_entity_kind = "buildings"
        new_entity_id = get_new_from_key_map("buildings", new_entity_kind, old_entity_id)
        if entity.get("manager"):
            new_team_id = get_new_from_key_map("organizations", "teams", entity["manager"])
        else:
            new_team_id = None
        attachments = entity.get("attachments", [])
        category = None
    elif entity.get("class") in "Space":
        if entity.get("space_type") == "lease":
            new_entity_kind = "leases"
        elif entity.get("space_type") == "sublease":
            new_entity_kind = "subleases"
        else:
            return
        new_entity_id = get_new_from_key_map("spaces", new_entity_kind, old_entity_id)
        if entity.get("organization"):
            new_team_id = get_new_from_key_map("organizations", "teams", entity["organizaton"])
        else:
            new_team_id = None
        attachments = entity.get("attachments", [])
        category = None
    elif entity.get("class") == "Organization":
        new_entity_kind = "organizations"
        new_entity_id = get_new_from_key_map("organizations", new_entity_kind, old_entity_id)
        new_team_id = get_new_from_key_map("organizations", "teams", entity["id"])
        attachments = [entity.get("logo")]
        category = "logo"  # TODO: verify
    elif entity.get("class") == "User":
        new_entity_kind = "cards"
        new_entity_id = get_new_from_key_map("users", new_entity_kind, old_entity_id)
        new_team_id = [get_new_from_key_map("organizations", "teams", key) for key in entity.get("organizations", [])]
        attachments = [entity.photo]
        category = "profile_upload"  # TODO: verify

    # Process attachments list
    for old_media_id in attachments:
        if not attachment:
            continue

        new_media_id = get_new_from_key_map("media", "media", old_media_id)
        if not new_media_id:
            continue

        if not category:
            # Category override not provided, check keymap
            category = get_new_from_key_map("media", "category", old_media_id)

        # Attachment
        attachment_attrs = relationship_resource(
            {"data": {"type": "media", "id": new_media_id}},
            {"data": {"type": new_entity_kind, "id": new_entity_id}},
            category=category  # TODO: make sure category=None wont fail marshmallow
        )
        attachment = load_resource("attachments", resource("attachments", **attachment_attrs))

        # Permissions
        if isinstance(new_team_id, (str, int)):
            # Permission (Media)
            permission_attrs = relationship_resource(
                    {"data": {"type": "teams", "id": new_team_id}},
                    {"data": {"type": "media", "id": new_media_id}},
                    permission="admin"
            )
            load_resource("permissions", resource("permissions", **permission_attrs))

            # Permission (Attachment)
            permission_attrs = relationship_resource(
                    {"data": {"type": "teams", "id": new_team_id}},
                    {"data": {"type": "attachments", "id": attachment["data"]["id"]}},
                    permission="admin"
            )
            load_resource("permissions", resource("permissions", **permission_attrs))

        elif isinstance(new_team_id, list):
            for team_id in new_team_id:
                # Permission (Media)
                permission_attrs = relationship_resource(
                        {"data": {"type": "teams", "id": team_id}},
                        {"data": {"type": "media", "id": new_media_id}},
                        permission="admin"
                )
                load_resource("permissions", resource("permissions", **permission_attrs))

                # Permission (Attachment)
                permission_attrs = relationship_resource(
                        {"data": {"type": "teams", "id": team_id}},
                        {"data": {"type": "attachments", "id": attachment["data"]["id"]}},
                        permission="admin"
                )
                load_resource("permissions", resource("permissions", **permission_attrs))

