from math import ceil
import math
from typing import Optional
from simulator.car import Car
from simulator.lights_control.light import Light


class Intersection:
    def __init__(self):
        self.cars: list[Car] = []
        self.length = 10

    def reset(self):
        self.cars = []

    def set_from_lane(self, from_lane):
        self.from_lane: Lane = from_lane

    def set_to_lane(self, to_lane):
        self.to_lane: Lane = to_lane

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        self.cars.remove(car)

    def set_length(self, length):
        self.length = length


class Lane:
    bin_size = 15

    def __init__(
            self,
            is_approach,
            to_direction,
            light: Optional[Light] = None,
            to_intsec: Optional[Intersection] = None,
            from_intsecs: list[Intersection] = [],
    ):
        # approaching the intersection or leaving intersection
        self.is_approach = is_approach
        # left, left_right, left_through_right, left_through, left, right, through_right, through
        self.to_direction = to_direction
        self.light = light
        self.cars: list[Car] = []
        self.passed_cars: list[Car] = []
        self.to_intsec = to_intsec
        self.from_intsecs = from_intsecs

        # connect lanes to intersection
        if to_intsec is not None:
            to_intsec.set_from_lane(self)
        if len(from_intsecs) > 0:
            for intsec in from_intsecs:
                intsec.set_to_lane(self)

    def reset(self):
        self.cars = []
        self.passed_cars = []

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        self.cars.remove(car)
        self.passed_cars.append(car)

    def get_cars(self):
        return self.cars

    def set_intersection(self, intersection: Intersection):
        self.intersection = intersection

    def set_street(self, street):
        self.street: Street = street

    def set_geo(self, left_x, left_y, right_x, right_y, width, length):
        self.left_x = left_x
        self.left_y = left_y
        self.right_x = right_x
        self.right_y = right_y
        self.width = width
        self.length = length

    def get_state_space(self):
        """
        Return the state definition for the lane: number of cells
        """
        # state strategy 2: queue length
        return 3  # max_queue_length(8)/4 + 1 =  3

        # # 37 bins
        # # 8 is the minimum distance unit, @see Car.drive_config
        # return ceil(self.length / self.bin_size)

    def get_state(self):
        """
        Return an array of each bin of the lane and whether it is occupied
        """
        ql = self.get_queue_length()
        # 0:0, 1-4:1, 5-8:2
        ql = math.ceil(ql / 4)
        avg_waiting = int(self.get_avg_waiting_time() / 1000)
        # 0:0, 1-10:1, 11-20:2, 21-30:3, 31-40:4
        avg_waiting = math.ceil(ql / 10)
        return ql
        # state = {i: 0 for i in range(self.get_state_space())}
        # for car in self.cars:
        #     dist_from_intsec = self.length - car.travel_distance
        #     bin = max(0, int(dist_from_intsec / self.bin_size))
        #     state[bin] = 1
        # return state

    def get_queue_length(self):
        """
        Get real-time queue length
        """
        queue_length = 0
        for car in self.cars:
            if car.current_speed < 1:
                queue_length += 1
        return queue_length

    def get_avg_waiting_time(self):
        total_waiting_ms = sum([car.updated_waiting_ms for car in self.cars])

        return total_waiting_ms / len(self.cars) if len(self.cars) > 0 else 0

        # total_speed = 0
        # num_cars = 0
        # for car in self.cars:
        #     total_speed += car.current_speed
        #     num_cars += 1
        # return total_speed / num_cars if num_cars > 0 else 0


class Street:
    STREET_ID_COUNTER = 0

    def __init__(self, name, x, y, width, length, divider_width, approach_direction, approach_lanes, exit_lanes):
        self.id = Street.STREET_ID_COUNTER
        Street.STREET_ID_COUNTER += 1
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.length = length
        self.divider_width = divider_width
        self.approach_direction = approach_direction  # north, south, east, west
        self.approach_lanes: list[Lane] = approach_lanes
        self.exit_lanes: list[Lane] = exit_lanes

        for l in self.approach_lanes:
            l.set_street(self)
        for l in self.exit_lanes:
            l.set_street(self)

    def reset(self):
        for l in self.approach_lanes:
            l.reset()
            l.to_intsec.reset() if l.to_intsec is not None else None
        for l in self.exit_lanes:
            l.reset()

    def __str__(self) -> str:
        return f"Street: {self.name} ({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Street: {self.name} ({self.x}, {self.y})"

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Street):
            return self.id == o.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
