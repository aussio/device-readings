from flask import request, make_response, Blueprint, jsonify
from marshmallow import Schema, fields, ValidationError
from .model import get_all_cache, get_cache, store_cache


device_reading_api = Blueprint("device_reading_api", __name__)


class ReadingSchema(Schema):
    timestamp = fields.DateTime(required=True)
    count = fields.Number(required=True)


class DeviceReadingSchema(Schema):
    id = fields.String(required=True)
    readings = fields.List(fields.Nested(ReadingSchema), required=True)


@device_reading_api.post("/reading")
def post_reading():
    """
    POST a new device reading
    """
    data = request.get_json()
    try:
        device_reading = DeviceReadingSchema().load(data)
    except ValidationError as err:
        print(err.valid_data)
        return make_response(err.messages, 400)

    store_cache(device_reading)

    return make_response(get_reading(device_reading["id"]), 201)


@device_reading_api.get("/reading")
def get_all_readings():
    """
    Return a list of all readings.

    Not in the prompt scope, but helpful for debugging.
    Not paginated or anything nice.
    """
    try:
        all_readings = get_all_cache()
        result = DeviceReadingSchema().dumps(all_readings, many=True)
    except (ValidationError, AttributeError) as err:
        # Hypothetically we never cached invalid data - but just in case!
        print(err.valid_data)
        print(err.messages)
        return make_response("Found some bad data. 🤕", 500)
    return make_response(result, 200)


@device_reading_api.get("/reading/<string:id>")
def get_reading(id):
    """
    GET a single device reading
    """
    device_readings = get_cache(id)
    if not device_readings:
        return make_response(jsonify(f"No reading found for id '{id}'"), 404)
    try:
        result = DeviceReadingSchema(only=["readings"]).dumps(device_readings)
    except (ValidationError, AttributeError) as err:
        # Hypothetically we should never cache invalid data - but just in case!
        if type(err) == ValidationError:
            print(err.valid_data)
            print(err.messages)
        else:
            print(err)
        return make_response("Found some bad data. 🤕", 500)
    return make_response(result, 200)
