from typing import Optional
from pygame import time
from simulator.car import Car
from simulator.street import Street
import random


class Traffic:
    """
    This class creates traffic on the streets: spawning cars
    """
    turn_directions = {
        ('north', 'south'): 'through',
        ('north', 'east'): 'left',
        ('north', 'west'): 'right',
        ('south', 'north'): 'through',
        ('south', 'east'): 'right',
        ('south', 'west'): 'left',
        ('east', 'west'): 'through',
        ('east', 'north'): 'right',
        ('east', 'south'): 'left',
        ('west', 'east'): 'through',
        ('west', 'north'): 'left',
        ('west', 'south'): 'right'
    }

    def __init__(self, time_scale: int, streets: list[Street], cars_config, game_config) -> None:
        self.time_scale = time_scale
        self.streets = streets
        self.num_cars = cars_config["num_cars"]
        self.cars_config = cars_config
        self.num_spawned_cars = 0
        self.game_config = game_config
        self.all_cars: list[Car] = []
        self.finished_cars: list[Car] = []
        self.last_spawn_ms = 0

    def reset(self, seed: Optional[int] = None):
        random.seed(seed)

        self.num_spawned_cars = 0
        self.all_cars = []
        self.finished_cars = []
        self.last_spawn_ms = 0

    def _spawn_car(self):
        num_new_cars = 1
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
            to_intsec = current_lane.to_intsec

            car = Car(street, current_lane, to_street, to_intsec,
                      game_config=self.game_config, init_speed=self.cars_config["init_speed"])
            self.all_cars.append(car)
            current_lane.cars.append(car)
            num_car_generated += 1
            self.last_spawn_ms = time.get_ticks()
        self.num_spawned_cars += num_car_generated

    def next_tick(self):
        clock_ms = time.get_ticks()

        # check if we need to spawn new cars
        if self.num_spawned_cars < self.num_cars:
            spawn_interval_ms = (
                self.game_config["SIMULATE_DURATION"] * 1000 // self.num_cars)
            if clock_ms - self.last_spawn_ms >= spawn_interval_ms:
                self._spawn_car()

        for car in self.all_cars:
            recycle_car = car.next_tick()
            if recycle_car:
                self.finished_cars.append(car)
                self.all_cars.remove(car)
        return clock_ms
