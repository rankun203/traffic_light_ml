from random import randint
from typing import Optional
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
        self.length = random.randint(15, 25)  # car length
        self.drive_config = {
            "front": random.randint(8, 12),
        }

    def next_tick(self):
        if self.lane.light is not None and self.lane.light.color == "red" and self.travel_distance >= self.street.length:
            # stop criteria: lane is red, travel distance is greater than street length
            return

        # detect distance from the car in front
        front_car: Optional[Car] = None
        for i, car in enumerate(self.lane.get_cars()):
            if car == self:
                if i == 0:
                    front_car = None
                else:
                    front_car = self.lane.get_cars()[i - 1]

        # avoid collision
        if front_car:
            front_car_tail_pos = front_car.travel_distance - front_car.length
            distance_to_front_car = front_car_tail_pos - self.travel_distance
            if distance_to_front_car < self.drive_config["front"]:
                self.current_speed = 0
            else:
                self.current_speed = 1
        else:
            self.current_speed = 1

        # forwards
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
