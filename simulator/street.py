from simulator.car import Car


class Lane:
    def __init__(self, is_approach, to_direction):
        self.is_approach = is_approach
        # left, through, right
        self.to_direction = to_direction
        self.cars: list[Car] = []

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        if car not in self.cars:
            print('[Lane] lane:', self, 'lane cars:', self.cars, 'target', car)
        self.cars.remove(car)

    def get_cars(self):
        return self.cars


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
        self.approach_direction = approach_direction
        self.approach_lanes: list[Lane] = approach_lanes
        self.exit_lanes: list[Lane] = exit_lanes

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
