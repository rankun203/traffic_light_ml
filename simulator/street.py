from typing import Optional
from simulator.car import Car
from simulator.lights_control.light import Light


class Intersection:
    def __init__(self):
        pass

    def set_from_lane(self, from_lane):
        self.from_lane: Lane = from_lane

    def set_to_lane(self, to_lane):
        self.to_lane: Lane = to_lane


class Lane:
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
        # left, through, right
        self.to_direction = to_direction
        self.light = light
        self.cars: list[Car] = []
        self.to_intsec = to_intsec
        self.from_intsecs = from_intsecs

        # connect lanes to intersection
        if to_intsec is not None:
            to_intsec.set_from_lane(self)
        if len(from_intsecs) > 0:
            for intsec in from_intsecs:
                intsec.set_to_lane(self)

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        self.cars.remove(car)

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
