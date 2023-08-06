# elevator-system

# Elevator System Project

This is a Django-based Elevator System project that simulates the working of an elevator system in a building. The project uses Django REST framework to handle API requests.

- An elevator system, which can be initialized with `n` elevator.
- Each elevator has below capabilites :
    -  Move Up and Down
    -  Open and Close Door
    -  Start and Stop Running
    -  Display Current Status
    -  Decide weather to move up or down, given a list of request


- Elevator System takes care of :

  -   Creation of system with an array of objects of elevator.
  -   Decides which lift to associate which floor.
  -   Marks which elevator is available or busy.
  -   Can mark which elevator is operational and which is not.


# ASSUMPTION:

- Elevator System has got only one button  per elevator outside the elevator.

- So if there are a total of 5 elevators, there will be 5 buttons.

- Note that, this dosent not mimic real world, when you would have a total of 10 buttons for 5 elevators ( one for up and one for down)

- Once the elevator reaches its called point, then based on what floor is requested, it moves either up or down.

## Prerequisites & Setup

Before running the project, make sure you have the following installed on your system:

1. PostgreSQL: Version 14 or higher
   - Install PostgreSQL using Homebrew (for macOS users):
     ```
     brew update
     brew install postgresql@14
     brew services start postgresql
     ```
   - Create a database and a user:
     ```
     psql postgres
     CREATE ROLE root WITH LOGIN PASSWORD 'root';
     ALTER ROLE root CREATEDB;
     CREATE DATABASE elevator_db;
     ```

2. Python and pip
   - Install Python 3 if not already installed: [Python Downloads](https://www.python.org/downloads/)
   - Install pip (should be installed with Python 3)

3. Redis
   - Install Redis:
     ```
     brew install redis
     brew services start redis
     ```

## Setup

1. Create a virtual environment and activate it:
     ```
     python3 -m venv venv
     ource venv/bin/activate
     ```

2. Clone the project repository:
     ```
     git clone https://github.com/shashank-1995/elevator-system.git
     cd elevator-system
     ```


3. Install the required dependencies:
     ```
     pip install -r requirements.txt
     ```


4. Configure the database settings:
    - Open the `config/settings.py` file.
    - Change the database name to the newly created database (`elevator_db`).

5. Apply database migrations:
     ```
     ./manage.py makemigrations
     ./manage.py migrate
     ```

6. Run the development server on required port:
     ```
     ./manage.py runserver 8000
     ```

## Import Postman Collection

To test the API endpoints, you can import the Postman collection provided in the project. The collection contains all the API requests and can be used to interact with the Elevator System.

## Project Structure

The project is organized into the following main directories:

- `elevator_system`: The Django project directory containing project-level settings and configurations.
- `elevator`: The Django app directory containing the core application code.

## API Endpoints

The API endpoints can be accessed at `http://localhost:8000/api/`. The available endpoints are as follows:
    a.first create an building using building collection.
    b.add elevators using 'initialize n elevators' api
        - provide building_id and num_elevators in body
    c. now can run process request api's
        - provide
            a. floors_requests : floors on which button outside elevator was pressed.
            b. building_id : building_id
            c. request_queue : -  request made in each elevator
            d. lift_positions :  - Current elevator postions
## Note

The project is a simulation and does not control any physical elevators. It is designed to demonstrate the working of an elevator system using Django and Django REST framework.



