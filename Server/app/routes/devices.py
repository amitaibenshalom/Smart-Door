from flask import Blueprint, jsonify, request

from app.errors import ApiError, error_response
from app.schemas.validation import int_field, require_json, string_field, validate_status
from app.serializers import door_event_to_dict, door_to_dict
from app.services.doors import update_door_status

devices_bp = Blueprint("devices", __name__)


@devices_bp.errorhandler(ApiError)
def handle_api_error(error):
    return error_response(error.message, error.status_code, error.code)


@devices_bp.post("/door-status")
def door_status():
    data = require_json(request)
    token = string_field(data, "token", min_length=16, max_length=255)
    status = validate_status(string_field(data, "status", max_length=16))
    battery_mv = int_field(data, "battery_mv", required=False, min_value=0)
    device_name = string_field(data, "device", required=False, max_length=120)

    door, event, status_changed = update_door_status(
        token=token,
        status=status,
        battery_mv=battery_mv,
        device_name=device_name,
    )
    return jsonify(
        {
            "door": door_to_dict(door),
            "event": door_event_to_dict(event),
            "status_changed": status_changed,
        }
    )
