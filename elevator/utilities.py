from rest_framework.exceptions import ValidationError
from elevator.models import Building


def validate_and_get_building(building_id):
    if building_id is None:
        raise ValidationError("Both 'num_elevators' and 'building_id' are required.")

    try:
        building_id = int(building_id)
    except ValueError:
        raise ValidationError("'building_id' must be a valid integer.")

    if building_id <= 0:
        raise ValidationError("'building_id' must be greater than zero.")

    # Check if the building exists
    building = Building.objects.filter(pk=building_id).first()
    if not building:
        raise ValidationError("Invalid 'building_id'. Building does not exist.")

    return building

def validate_num_elevators(num_elevators):
    try:
        num_elevators = int(num_elevators)
    except ValueError:
        raise ValidationError("'num_elevators' must be a valid integer.")

    if num_elevators <= 0:
        raise ValidationError("'num_elevators' must be greater than zero.")

    return num_elevators

def validate_list_of_int(payload_object):
    if not isinstance(payload_object, list) or not all(isinstance(floor, int) for floor in payload_object):
        return False
    return True

def validate_request_queue(request_queue):
    if not isinstance(request_queue, list) or not all(isinstance(queue, list) and all(isinstance(floor, int) for floor in queue) for queue in request_queue):
        return False
    return True

def validate_current_lift_positions(current_lift_positions, elevators_count):
    if not isinstance(current_lift_positions, list) or len(current_lift_positions) != elevators_count or not all(isinstance(pos, int) for pos in current_lift_positions):
        return False
    return True

def initialize_response_keys():
    return {"flag":False,"message": "Unable to fetch response", "error":"nil"}

def update_response_keys(flag, message, error, result):
    return {"flag":flag,"message": message, "error":error, 'data':result}