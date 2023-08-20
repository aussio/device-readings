#
# I didn't end up needing the actual Python objects for anything. Our "Model" is so simple that
# a flat dictionary worked really nicely.
#
# @dataclass
# class Reading:
#     timestamp: datetime
#     count: int
#
# @dataclass
# class DeviceReading:
#     id: UUID
#     readings: Reading


"""
Global cache, kept between requests.

Kept in a more lookup-friendly dictionary format with key names removed, like following:
{
    "36d5658a-6908-479e-887e-a949ec199272": {
        "2021-09-29T16:08:15+01:00": 2,
        "2021-09-29T16:09:15+01:00": 15,
    },
}
"""
cache = {}


def store_cache(device_reading):
    """Should be passed a pre-validated device_reading dictionary.

    Devices that already have readings in the cache have duplicate timestamps dropped, not overwritten.
    """
    entry = get_cache(device_reading["id"])

    # Convert readings into cache format
    new_readings_dict = {}
    for r in device_reading["readings"]:
        new_readings_dict[r["timestamp"]] = r["count"]

    cached_readings_dict = {}
    for r in entry.get("readings", []):
        cached_readings_dict[r["timestamp"]] = r["count"]

    # Merge cached with new, keeping the cached in favor of new.
    if cached_readings_dict:
        new_readings_dict.update(cached_readings_dict)

    cache[device_reading["id"]] = new_readings_dict


def get_cache(id):
    """Should be passed a pre-validated device_reading id.

    Reconstructs the cache-format into a dictionary with keys for the DeviceReadingSchema.
    Returns an empty dictionary if the id is not found in the cache.
    """
    entry = cache.get(id)

    # Supports a device being registered with no readings.
    if entry is None:
        return {}

    readings = []
    for timestamp, count in entry.items():
        readings.append({"timestamp": timestamp, "count": count})

    return {"id": id, "readings": readings}


# Not in the prompt scope, but helpful for debugging
def get_all_cache():
    return [get_cache(id) for id in cache.keys()]
