from typing import Optional
from simulator.car import Car
from simulator.street import Street
from simulator.timer import clock
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
        self.cars_config = cars_config
        self.num_spawned_cars = 0
        self.game_config = game_config
        self.all_cars: list[Car] = []
        self.finished_cars: list[Car] = []
        self.last_spawn_ms = 0

        self.acc_cars_to_spawn = 0

    def reset(self, seed: Optional[int] = None):
        random.seed(seed)

        self.num_spawned_cars = 0
        self.all_cars = []
        self.finished_cars = []
        self.last_spawn_ms = 0
        for street in self.streets:
            street.reset()

    def _spawn_car(self):
        num_new_cars = 1
        # spawn cars on a random street and start at the beginning of the street
        num_car_generated = 0
        while num_car_generated < num_new_cars:
            street = random.choice(self.streets)
            # random choose to_street from the rest of the streets
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
            self.last_spawn_ms = clock().get_ticks()
        self.num_spawned_cars += num_car_generated

    def next_tick(self):
        clock_ms = clock().get_ticks()
        cars_per_min = self.cars_config["cars_per_min"]

        # calculate step in minutes
        step_min = self._get_step_ms() / 1000 / 60
        # calculate number of cars to spawn in this step
        cars_per_step = cars_per_min * step_min
        # if cars_per_step >= 1, spawn cars and reset acc_cars_to_spawn to acc%1
        num_cars_to_spawn = self.acc_cars_to_spawn + cars_per_step
        if num_cars_to_spawn >= 1:
            self.acc_cars_to_spawn = num_cars_to_spawn % 1
            num_cars_to_spawn = int(num_cars_to_spawn)
            for _ in range(num_cars_to_spawn):
                self._spawn_car()
        else:
            # delegate number of cars to spawn to next step until it reaches >= 1
            self.acc_cars_to_spawn += cars_per_step

        for car in self.all_cars:
            recycle_car = car.next_tick()
            if recycle_car:
                self.finished_cars.append(car)
                self.all_cars.remove(car)
        return clock_ms

    def _get_step_ms(self):
        clock_ms = clock().get_ticks()

        if 'last_clock_ms' not in self.__dict__:
            self.last_clock_ms = clock_ms

        step_ms = clock_ms - self.last_clock_ms
        self.last_clock_ms = clock_ms
        return step_ms

    def calc_waiting_time(self):
        """
        Calculate the updated total waiting time of all cars on all approaching lanes
        """
        total_waiting_ms = 0
        for street in self.streets:
            for lane in street.approach_lanes:
                for car in lane.cars:
                    total_waiting_ms += car.updated_waiting_ms

        return total_waiting_ms

    def calc_total_queue_length(self):
        """
        Calculate the total queue length of all approaching lanes
        """
        total_queue_length = 0
        for street in self.streets:
            for lane in street.approach_lanes:
                total_queue_length += lane.get_queue_length()

        return total_queue_length

    def calc_passed_cars(self):
        total_passed_cars = 0
        for street in self.streets:
            for lane in street.approach_lanes:
                total_passed_cars += len(lane.passed_cars)

        return total_passed_cars
