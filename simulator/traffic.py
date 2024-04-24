from pygame import time
from simulator.car import Car
from simulator.street import Street
import random


class Traffic:
    turn_directions = {
        ('north', 'south'): 'through',
        ('north', 'east'): 'left',
        ('north', 'west'): 'right',
        ('south', 'north'): 'through',
        ('south', 'east'): 'right',
        ('south', 'west'): 'left',
        ('east', 'west'): 'through',
        ('east', 'north'): 'left',
        ('east', 'south'): 'right',
        ('west', 'east'): 'through',
        ('west', 'north'): 'right',
        ('west', 'south'): 'left'
    }

    def __init__(self, time_scale: int, clock: time.Clock, streets: list[Street], num_cars=100) -> None:
        self.clock = clock
        self.time_scale = time_scale
        self.streets = streets
        self.num_cars = num_cars
        self.all_cars: list[Car] = []
        self._spawn_car()

    def _spawn_car(self):
        num_new_cars = 5
        # spawn cars on a random street and start at the beginning of the street
        num_car_generated = 0
        while num_car_generated < num_new_cars:
            street = random.choice(self.streets)
            # random choose to_street from the rest of the streets
            # TODO: check street approach lanes and filter out the lanes that are not possible to go to for to_street
            to_street = random.choice(
                [st for st in self.streets if st != street])

            turn = (street.approach_direction, to_street.approach_direction)
            if turn not in Traffic.turn_directions:
                # skip if the turn is not possible
                continue

            current_lane = random.choice(
                [lane for lane in street.approach_lanes if lane.to_direction ==
                    Traffic.turn_directions[turn]]
            )

            car = Car(street, current_lane, to_street)
            self.all_cars.append(car)
            current_lane.cars.append(car)
            num_car_generated += 1

    def next_tick(self):
        # don't know what this func is doing yet
        clock_ms = time.get_ticks()
        for car in self.all_cars:
            recycle_car = car.next_tick()
            if recycle_car:
                self.all_cars.remove(car)
        return clock_ms
