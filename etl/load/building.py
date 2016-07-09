
from .. import transform
from ._utils import load_resource, resource, send_to_key_map


# TODO: multiprocess
def run(all_buildings):
    for building in all_buildings:
        process_building(building)


def process_building(building):
    new_building = load_building_asset(building)
    send_to_key_map(
        v1_type="buildings",
        v1_key=building["id"],
        v1_urlsafe=building["urlsafe"],
        v2_type="buildings",
        v2_key=new_building["data"]["id"],
    )


def load_building_asset(building):
    attrs = transform.building.asset(building)
    return load_resource("buildings", resource("buildings", **attrs))

