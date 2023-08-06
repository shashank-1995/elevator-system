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
