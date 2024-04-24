from random import randint
from pygame import time
import random


class Car:
    # static Counter
    CAR_ID_COUNTER = 0

    def __init__(self, street, lane, to_street) -> None:
        self.id = Car.CAR_ID_COUNTER
        Car.CAR_ID_COUNTER += 1
        # assign a random color to each car
        self.color = (randint(100, 200), randint(100, 200), randint(100, 200))
        self.init_tick_ms = time.get_ticks()
        self.current_speed = 1  # px per second
        self.street = street
        self.lane = lane
        self.to_street = to_street
        self.travel_distance = 0  # travel unit, px for now
        self.width = 10  # car width
        self.length = 20  # car length

    def next_tick(self):
        self.travel_distance += self.current_speed
        if self.travel_distance - self.length >= self.street.length:
            self.lane.remove_car(self)

            if self.to_street is None:
                # this car is out of the simulation
                recycle_car = True
                return recycle_car

            self.street = self.to_street
            self.to_street = None  # leaves the simulation
            self.lane = random.choice(self.street.exit_lanes)
            self.lane.add_car(self)
            self.travel_distance = 0
