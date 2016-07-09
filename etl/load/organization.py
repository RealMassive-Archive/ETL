
from .. import transform
from ._utils import load_resource, resource, send_to_key_map


# TODO: multiprocess
def run(all_organizations):
    for organization in all_organizations:
        process_organization(organization)


def process_organization(organization):
    # Team
    team = load_team(organization)
    if team:
        send_to_key_map(
            v1_type="organizations",
            v1_key=organization["id"],
            v1_urlsafe=organization["urlsafe"],
            v2_type="teams",
            v2_key=team["data"]["id"],
        )

    # Organization
    if organization.get("name") or organization.get("logo"):
        # Orgs with no logo AND no name are considered v2 irrelevant.
        # The rest are potentially user-facing and too risky to ignore
        new_organization = load_organization(organization)
        if new_organization:
            send_to_key_map(
                v1_type="organizations",
                v1_key=organization["id"],
                v1_urlsafe=organization["urlsafe"],
                v2_type="organizations",
                v2_key=new_organization["data"]["id"],
            )


def load_team(organization):
    attrs = transform.organization.team(organization)
    if not attrs.get("name"):
        # Create default team name
        owner_email = organization.get("owner_email")
        if owner_email:
            attrs["name"] = "{} default team".format(owner_email.encode("ascii", "ignore").strip())
        else:
            attrs["name"] = "default team"
    return load_resource("teams", resource("teams", **attrs))


def load_organization(organization):
    attrs = transform.organization.organization(organization)
    return load_resource("organizations", resource("organizations", **attrs))

