from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Elevator, Building
from .serializers import ElevatorSerializer, BuildingSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from elevator.utilities import (validate_and_get_building,
                                validate_num_elevators,
                                validate_floor_requests,
                                validate_request_queue,
                                initialize_response_keys)
import copy

class ElevatorViewSet(viewsets.ModelViewSet):
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer

    def create(self, request):
        context = initialize_response_keys()
        num_elevators = request.data.get('num_elevators')
        building_id = request.data.get('building_id')

        # Validate and get the building object
        building = validate_and_get_building(building_id)

        # Validate and get the number of elevators
        num_elevators = validate_num_elevators(num_elevators)

        # Create elevators with validated inputs
        existing_elevator_names = set(Elevator.objects.filter(building=building).values_list('name', flat=True))
        created_elevators = []

        for i in range(num_elevators):
            name = f'Elevator {i + 1}'
            while name in existing_elevator_names:
                i += 1
                name = f'Elevator {i + 1}'

            elevator = Elevator(name=name, building=building)
            created_elevators.append(elevator)
            existing_elevator_names.add(name)

        elevators_obj = Elevator.objects.bulk_create(created_elevators, batch_size=100)
        if elevators_obj:
            context["flag"] = True
            context["message"] = f'{num_elevators} elevators initialized.'
            context["data"] = self.get_serializer(elevators_obj, many=True).data

        return Response(context, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'])
    def process_request(self, request, pk=None):
        """
        Process elevator requests for each elevator in the system.

        This function takes elevator requests, active floors, building_id, request_queue, and current_lift_positions, and processes them to efficiently
        allocate elevators to fulfill the requests.

        Parameters:
            request (HttpRequest): The HTTP request object.
            pk (int, optional): The primary key of the elevator (not used in this context).

        Returns:
            Response: A JSON response containing the elevator system response with information about each elevator's status and processed requests.
        """
        context = initialize_response_keys()
        floor_requests = request.data.get('floor_requests')
        building_id = request.data.get('building_id')
        request_queue =  request.data.get('request_queue')
        current_lift_positions = request.data.get('current_lift_positions')

        if not validate_floor_requests(floor_requests):
            return Response({'flag': False, 'error': 'Invalid floor requests'}, status=status.HTTP_400_BAD_REQUEST)

        building = validate_and_get_building(building_id)
        if not validate_request_queue(request_queue):
            return Response({'flag': False, 'error': 'Invalid request queue'}, status=status.HTTP_400_BAD_REQUEST)
        elevators = Elevator.objects.filter(building=building)
        if elevators.count() != len(current_lift_positions):
            current_lift_positions = [0] * elevators.count()

        elevator_response = self.initialize_elevator_response(elevators, current_lift_positions)
        floor_requests.sort()

        # process each floor, select the closest elevator for that floor
        for queue_counter, floor in enumerate(floor_requests):
            distance = []
            # find optimal lift for each floor
            for elevator in elevators:
                # if it is not already selected
                if not elevator.is_selected:
                    distance.append(abs(elevator.current_floor - floor))
                else:
                    distance.append(999)
            queue_counter = queue_counter % len(request_queue)
            # find the selected lift
            selected_lift = distance.index(min(distance))
            elevator_selected = elevators[selected_lift]
            # assign service queue
            elevator_selected.requests = [floor] + request_queue[queue_counter]
            # set direction
            elevator_selected.direction = "Up" if elevator_selected.current_floor <= floor else "Down"
            # mark as selected
            elevator_selected.is_selected = True
            elevator_selected.save()
            elevator_response[elevator_selected.id]["direction"] = elevator_selected.direction

        # process request for each elevator
        for elevator in elevators:
            elevator_response[elevator.id]["requests"] = self.process_requests_for_elevator(elevator)

        final_response = list(elevator_response.values())
        if final_response:
            context["message"] = 'Successfully fetched response'
            context['data'] = final_response


        return Response(context, status=status.HTTP_200_OK)


    def process_requests_for_elevator(self, elevator):
        if elevator.is_selected:
            processed_requests = self.process_elevator_request(elevator)
            return copy.deepcopy(processed_requests)
        else:
            elevator.is_operational = False
            elevator.save()
            return []


    def initialize_elevator_response(self, elevators, current_lift_positions):
        elevator_response = {}
        count = 0
        for elevator in elevators:
            elevator_response[elevator.id] = {
                "elevator_id": elevator.id,
                "elevator_name": elevator.name,
                "building_id": elevator.building.id,
                "building_name": elevator.building.name,
                "current_floor":  current_lift_positions[count],
                "is_operational": elevator.is_operational
            }
            elevator.current_floor = current_lift_positions[count]
            elevator.save()
            count += 1
        return elevator_response


    def current_status(self, elevator, is_door_opened):
        current_status_dict = {
                "lift_number": elevator.id, "current_floor": elevator.current_floor, "current_direction": elevator.direction, "is_operational": elevator.is_operational
            }
        if is_door_opened == None:
            return current_status_dict
        else:
            if is_door_opened:
                current_status_dict["is_door_opened"] = True
            else:
                current_status_dict["is_door_closed"] = True
            return current_status_dict


    def process_elevator_request(self, elevator):
        """
        Process elevator requests.

        Parameters:
            elevator (Elevator): The elevator object to process requests.

        Returns:
            List: A list of dictionaries containing elevator status at each step.
        """
        self.current_response_list = []

        # Process the elevator requests one by one
        while elevator.requests:
            current_floor = elevator.current_floor

            # Step 1: Find the closest floor from the remaining requests
            closest_floor = min(elevator.requests, key=lambda floor: abs(floor - current_floor))

            # Step 2: Move the elevator towards the closest floor
            self.move_towards_floor(elevator, closest_floor)

            # Step 3: Elevator has reached the closest floor, open and close the door
            self.current_response_list.append(self.current_status(elevator, True))
            self.current_response_list.append(self.current_status(elevator, False))

            # Step 4: Remove the current floor from the requests as it has been serviced
            elevator.requests.remove(elevator.current_floor)

            # Append the current status to the response list
            self.current_response_list.append(self.current_status(elevator, None))

        # All requests have been serviced, reset the elevator parameters
        self.reset_elevator_params(elevator)

        # Return the list of elevator status at each step
        return self.current_response_list


    def move_towards_floor(self, elevator, target_floor):
        """
        Move the elevator towards the target floor.

        Parameters:
            elevator (Elevator): The elevator object.
            target_floor (int): The floor to which the elevator needs to move.

        Returns:
            None
        """
        # Set the elevator direction based on the target floor
        elevator.direction = "Up" if target_floor > elevator.current_floor else "Down"

        # Continue moving until the elevator reaches the target floor
        while elevator.current_floor != target_floor:
            # Move the elevator one step in the appropriate direction
            self.move_one_step(elevator)

            # Append the current status to the response list at each step
            self.current_response_list.append(self.current_status(elevator, None))


    def move_one_step(self, elevator):
        """
        move_one_step : moves lift one step up or down based on direction
        elevator.current_floor = elevator.current_floor + self.direction
        direction can have value of 1 or -1
        raises Exception if lift is not operational
        """
        try:
            if elevator.is_operational:
                elevator.current_floor += 1 if elevator.direction == "Up" else -1
            else:
                raise Exception("Lift is not operational")

        except Exception as e:
            print(e)
            return e


    def reset_elevator_params(self, elevator):
        # when request finishes reset the direction
        elevator.direction = "Up"
        elevator.is_operational = True
        elevator.is_selected = False
        elevator.requests = []
        elevator.save()


    @action(detail=True, methods=['post'])
    def open_elevator_door(self, request, pk=None):
        elevator = get_object_or_404(Elevator, pk=pk)
        # Open the door of the elevator
        elevator.is_door_open = True
        elevator.save()
        return Response({'flag': True, 'message': 'Door opened.'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def close_elevator_door(self, request, pk=None):
        elevator = get_object_or_404(Elevator, pk=pk)
        # Close the door of the elevator
        elevator.is_door_open = False
        elevator.save()
        return Response({'flag': True, 'message': 'Door closed.'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def mark_not_working(self, request, pk=None):
        elevator = get_object_or_404(Elevator, pk=pk)
        # Mark the elevator as not working or in maintenance
        elevator.is_operational = False
        elevator.save()
        return Response({'flag': True, 'message': 'Elevator marked as not working.'}, status=status.HTTP_200_OK)


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        context = initialize_response_keys()
        context["flag"] = True
        context["message"] = f'Building created successfully'
        context['data'] = serializer.data
        
        return Response(context, status=status.HTTP_201_CREATED)