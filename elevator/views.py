from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Elevator, Building
from .serializers import ElevatorSerializer, BuildingSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from elevator.utilities import validate_and_get_building, validate_num_elevators
class ElevatorViewSet(viewsets.ModelViewSet):
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer
    
    def create(self, request):
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

        Elevator.objects.bulk_create(created_elevators, batch_size=100)

        return Response({'message': f'{num_elevators} elevators initialized.'}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def process_request(self, request, pk=None):
        """
    Process elevator requests for each elevator in the system.

    This function takes elevator requests, active floors, building_id, request_queue, and lift_positions, and processes them to efficiently
    allocate elevators to fulfill the requests.

    Parameters:
        request (HttpRequest): The HTTP request object.
        pk (int, optional): The primary key of the elevator (not used in this context).

    Returns:
        Response: A JSON response containing the elevator system response with information about each elevator's status and processed requests.
    """
        active_floors = request.data.get('floor_requests')
        building_id = request.data.get('building_id')
        request_queue =  request.data.get('request_queue')
        lift_positions = request.data.get('lift_positions')
        
        elevators = Elevator.objects.filter(building=building_id)
        
        if len(lift_positions) < 0:
            lift_positions = [0] * elevators.count()
        
        count = 0
        for elevator in elevators:
            elevator.current_floor = lift_positions[count]
            elevator.save()
            count += 1
        
        if elevators.count() == len(lift_positions):
            for each in range(0, elevators.count()):
                elevators[each].current_floor = lift_positions[each]
                elevators[each].save()
        active_floors.sort()

        elevator_response = {}

        # process each floor, select the closest elevator for that floor
        for queue_counter, floor in enumerate(active_floors):
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
            

            # print information on screen
            elevator_response[elevator_selected.id] = {
                "current_floor":  elevator_selected.current_floor,
                "is_operational": elevator_selected.is_operational,
                "requests": elevator_selected.requests,
                "direction": elevator_selected.direction,
                "processed_requests": [],
                "error": None
            }
            elevator_selected.save()
        

        # process request for each elevator
        for elevator in elevators:
            if elevator.is_selected:
                processed_requests = self.process_elevator_request(elevator)
                elevator_response[elevator.id]["processed_requests"] = processed_requests
            else:
                # Mark unselected elevators as not operational
                elevator.is_operational = False
                elevator.save()

        return Response({'elevators': elevator_response}, status=status.HTTP_200_OK)

    
    def current_status(self, elevator):
        return {
            "lift_number": elevator.id, "current_floor": elevator.current_floor, "is_operational": elevator.is_operational
        }

    def calculate_service_in_directions(self, elevator):
        """
        Calculates the service lists for the up and down directions.
        Returns two lists: service_in_up_direction and service_in_down_direction.
        """
        elevator.requests = sorted(elevator.requests)  # Sort the requests in ascending order
        current_floor = elevator.current_floor

        # Separate the requests into two lists based on their direction
        service_in_up_direction = [floor for floor in elevator.requests if floor > current_floor]
        service_in_down_direction = [floor for floor in elevator.requests if floor < current_floor]

        # Reverse the down direction list to prioritize lower floors first
        service_in_down_direction = service_in_down_direction[::-1]

        return service_in_up_direction, service_in_down_direction


    def process_elevator_request(self, elevator):
        """
        Process elevator requests.
        """

        self.current_response_list = []

        # Go to requested floor
        print("Need To Process => ", elevator.requests)

        if elevator.requests[0] != elevator.current_floor:
            self.current_response_list.append(self.current_status(elevator))
            self.execute_request(elevator.requests[0:1], elevator)
        else:
            self.current_response_list.append(self.current_status(elevator))
            elevator.is_door_open = True
            elevator.is_door_open = False

        # User presses the buttons, lift decides automatically
        elevator.requests = elevator.requests[1:]
        service_in_up_direction, service_in_down_direction = self.calculate_service_in_directions(elevator)

        # Nothing to service in up direction, go down
        if len(service_in_up_direction) == 0:
            elevator.direction = "Down"
        # Nothing to service in down direction, go up
        elif len(service_in_down_direction) == 0:
            elevator.direction = "Up"
        # Calculate cost and then decide direction
        else:
            # Effort_up = distance between first up floor and current floor
            effort_up = abs(service_in_up_direction[0] - elevator.current_floor)
            # Effort_down = distance between first down floor and current floor
            effort_down = abs(service_in_down_direction[0] - elevator.current_floor)

            # Choose direction
            if effort_up <= effort_down:
                elevator.direction = "Up"
            else:
                elevator.direction = "Down"

        # Define the directions in a list
        directions = ["Down", "Up"]

        # Execute the request for up and down directions
        for direction in directions:
            if elevator.direction == direction:
                self.execute_request(service_in_down_direction, elevator)
            else:
                self.execute_request(service_in_up_direction, elevator)

            # Reverse the direction
            elevator.direction = directions[(directions.index(elevator.direction) + 1) % len(directions)]

        # Set params to denote that it is available
        self.reset_lift_params(elevator)
        return self.current_response_list

    
    def execute_request(self, request_list, elevator):
        """
        Execute a request for the elevator.

        Parameters:
            request_list (list): The list of floors to be serviced by the elevator.
            elevator (Elevator): The elevator object to execute the requests.

        Returns:
            None
        """
        # Continue running until all requests in the list are finished
        while True:
            # Set is_operational to True, indicating that the elevator is in operation
            elevator.is_operational = True

            # Check if the elevator is currently on a floor that is in the request list
            if elevator.current_floor in request_list:
                # Remove the processed floor from the request list
                while request_list.count(elevator.current_floor) > 0:
                    request_list.remove(elevator.current_floor)

                # Stop the elevator, as it has reached one of its destinations
                elevator.is_operational = False

                # Add the current status to the response list
                self.current_response_list.append(self.current_status(elevator))

                # Open and close the elevator door
                elevator.is_door_open = True
                elevator.is_door_open = False

            # If we have processed all the requests in the list, break the loop
            if len(request_list) == 0:
                break

            # Add the current status to the response list and move the elevator one step
            self.current_response_list.append(self.current_status(elevator))
            self.move_one_step(elevator)

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

    def reset_lift_params(self, elevator):
        # when request finishes reset the direction
        elevator.direction = "Up"
        elevator.is_operational = False
        elevator.is_selected = False
        elevator.requests = []
        elevator.save()
    
    @action(detail=True, methods=['post'])
    def open_elevator_door(self, request, pk=None):
        elevator = get_object_or_404(Elevator, pk=pk)
        # Open the door of the elevator
        elevator.is_door_open = True
        elevator.save()
        return Response({'message': 'Door opened.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close_elevator_door(self, request, pk=None):
        elevator = get_object_or_404(Elevator, pk=pk)
        # Close the door of the elevator
        elevator.is_door_open = False
        elevator.save()
        return Response({'message': 'Door closed.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_not_working(self, request, pk=None):
        elevator = get_object_or_404(Elevator, pk=pk)
        # Mark the elevator as not working or in maintenance
        elevator.is_operational = False
        elevator.save()
        return Response({'message': 'Elevator marked as not working.'}, status=status.HTTP_200_OK)
class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer