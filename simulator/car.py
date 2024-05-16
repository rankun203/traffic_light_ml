from random import randint
from typing import Optional
import random

from pygame import time
from pygame.time import Clock


class Car:
    # static Counter
    CAR_ID_COUNTER = 0
    start_delay_ms = 1000

    def __init__(self, street, lane, to_street, to_intsec, game_config, init_speed=1) -> None:
        self.id = Car.CAR_ID_COUNTER
        Car.CAR_ID_COUNTER += 1
        # assign a random color to each car
        self.color = (randint(100, 200), randint(100, 200), randint(100, 200))
        self.init_speed = init_speed
        self.current_speed = self.init_speed  # px per second
        self.street = street
        self.lane = lane
        self.to_street = to_street
        self.to_intsec = to_intsec
        self.in_intersection = False
        self.travel_distance = 0  # travel unit, px for now
        self.updated_waiting_s = 0
        self.width = 10  # car width
        self.length = random.randint(15, 25)  # car length
        self.drive_config = {
            "front": random.randint(8, 12),  # car to car gap
        }
        self.game_config = game_config

    def reset_travel_distance(self):
        self.travel_distance = 0

    def set_geo(self, x, y, rotate=0):
        self.x = x
        self.y = y
        self.rotate = rotate

    def _get_step_ms(self):
        clock_ms = time.get_ticks()

        if 'last_clock_ms' not in self.__dict__:
            self.last_clock_ms = clock_ms

        step_ms = clock_ms - self.last_clock_ms
        self.last_clock_ms = clock_ms
        return step_ms

    def next_tick(self) -> bool | None:
        """
        Returns True if the car is out of the simulation
        """
        if self.street is not None and not self.in_intersection:
            if self.lane.light is not None and self.lane.light.color == "red" and self.travel_distance >= self.street.length:
                # stop criteria: lane is red, travel distance is greater than street length
                self.stopped_at_ms = time.get_ticks()
                return

        # --- delay start for a little while
        # check if car is stopped
        if hasattr(self, "stopped_at_ms"):
            # switch to started, but do not moving yet.
            self.started_at_ms = time.get_ticks()
            delattr(self, "stopped_at_ms")
            return
        if hasattr(self, "started_at_ms"):
            if time.get_ticks() - self.started_at_ms < self.start_delay_ms:
                return
            else:
                delattr(self, "started_at_ms")
                # continue to move the car
        # --- finished delay start

        # detect car in front
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
                self.current_speed = self.init_speed
        else:
            self.current_speed = self.init_speed

        # forwards
        step_s = self._get_step_ms() / 1000
        self.travel_distance += self.current_speed * step_s

        # update car waiting time if car is not moving
        if self.current_speed < 1:
            self.updated_waiting_s += step_s
        else:
            self.updated_waiting_s = 0

        if self.in_intersection and self.travel_distance + self.length >= self.to_intsec.length:
            # leaving intersection
            if self.to_street is None:
                raise ValueError("Car should have to_street at this point")

            # check if car has left the intersection
            # 1. get the intersection total distance
            # 2. get travelled distance
            # 3. if travelled distance >= self.intersection.distance
            # 4. move car to next street

            self.in_intersection = False
            self.to_intsec.remove_car(self)

            # move car to next street
            self.street = self.to_street
            self.to_street = None  # leaves the simulation
            self.lane = self.to_intsec.to_lane
            self.lane.add_car(self)
            self.reset_travel_distance()

        if self.street is not None and self.travel_distance - self.length >= self.street.length:
            # leaving street
            self.lane.remove_car(self)

            if self.to_street is None:
                # this car is out of the simulation
                recycle_car = True
                return recycle_car

            # move to intersection
            self.in_intersection = True
            self.to_intsec.add_car(self)
            self.street = None
            self.reset_travel_distance()
