import pygame
import os
import sys

from simulator.environment import Environment
from simulator.lights_control.static import Phase, StaticLightsControl
from simulator.lights_control.light import Light
from simulator.street import Intersection, Lane, Street
from simulator.traffic import Traffic

pygame.init()

screen_width = 800
screen_height = 600
# put the window in the top left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
pygame.display.set_caption('Traffic Intersection Simulation')
screen = pygame.display.set_mode((screen_width, screen_height))


# game variables
clock = pygame.time.Clock()
game_config = {
    "FPS": 60,  # frames per second
    "SIMULATE_DURATION": 60,  # in seconds
    "clock": clock,
}

cars_config = {
    "num_cars": 1000,
    # px per second, 1px = 0.1m, that's 120px/s = 12m/s = 43.2km/h
    "init_speed": 120,
}

road_width = 200

# traffic lights
lit_north_through = Light()
lit_north_left = lit_north_through
lit_north_right = Light()
lit_south_through = Light()
lit_south_left = lit_south_through
lit_south_right = Light()
lit_west_through = Light()
lit_west_left = lit_west_through
lit_west_right = Light()
lit_east_through = Light()
lit_east_left = lit_east_through
lit_east_right = Light()

# traffic lights phases
lights_phases_config = [
    Phase([lit_north_right, lit_south_right], 5),
    Phase([lit_west_through, lit_west_left, lit_east_through, lit_east_left], 10),
    Phase([lit_west_right, lit_east_right], 5),
    Phase([lit_north_through, lit_north_left, lit_south_through, lit_south_left], 10),
]


# intersections for each lane
intsec_north_left = Intersection()
intsec_north_through = Intersection()
intsec_north_right = Intersection()
intsec_south_left = Intersection()
intsec_south_through = Intersection()
intsec_south_right = Intersection()
intsec_west_left = Intersection()
intsec_west_through = Intersection()
intsec_west_right = Intersection()
intsec_east_left = Intersection()
intsec_east_through = Intersection()
intsec_east_right = Intersection()


roads_config = [
    Street(
        name="Lygon Street",
        x=screen_width//2-(road_width//2), y=0,
        width=road_width,
        length=screen_height//2-(road_width//2),
        divider_width=20,
        approach_direction="south",
        approach_lanes=[
            Lane(True, 'left', lit_south_left, to_intsec=intsec_south_left),
            Lane(True, 'through', lit_south_through,
                 to_intsec=intsec_south_through),
            Lane(True, 'right', lit_south_right, to_intsec=intsec_south_right)
        ],
        exit_lanes=[Lane(False, 'through', from_intsecs=[intsec_north_through, intsec_west_right]),
                    Lane(False, 'through', from_intsecs=[intsec_east_left])],
    ),
    Street(
        name="Victoria Street",
        x=0,
        y=screen_height//2-(road_width//2),
        width=road_width,
        length=screen_width//2-(road_width//2),
        divider_width=20,
        approach_direction="east",
        approach_lanes=[
            Lane(True, 'left', lit_east_left, to_intsec=intsec_east_left),
            Lane(True, 'through', lit_east_through,
                 to_intsec=intsec_east_through),
            Lane(True, 'right', lit_east_right, to_intsec=intsec_east_right)
        ],
        exit_lanes=[Lane(False, 'through', from_intsecs=[intsec_west_through, intsec_south_right]),
                    Lane(False, 'through', from_intsecs=[intsec_north_left])],
    ),
    Street(
        name="Victoria Street",
        x=screen_width//2+(road_width//2),
        y=screen_height//2-(road_width//2),
        width=road_width,
        length=screen_width//2-(road_width//2),
        divider_width=20,
        approach_direction="west",
        approach_lanes=[
            Lane(True, 'left', lit_west_left, to_intsec=intsec_west_left),
            Lane(True, 'through', lit_west_through,
                 to_intsec=intsec_west_through),
            Lane(True, 'right', lit_west_right, to_intsec=intsec_west_right)
        ],
        exit_lanes=[Lane(False, 'through', from_intsecs=[intsec_east_through, intsec_north_right]),
                    Lane(False, 'through', from_intsecs=[intsec_south_left])],
    ),
    Street(
        name="Russell Street",
        x=screen_width//2-(road_width//2),
        y=screen_height//2+(road_width//2),
        width=road_width,
        length=screen_height//2-(road_width//2),
        divider_width=20,
        approach_direction="north",
        approach_lanes=[
            Lane(True, 'left', lit_north_left, to_intsec=intsec_north_left),
            Lane(True, 'through', lit_north_through,
                 to_intsec=intsec_north_through),
            Lane(True, 'right', lit_north_right, to_intsec=intsec_north_right)
        ],
        exit_lanes=[Lane(False, 'through', from_intsecs=[intsec_south_through, intsec_east_right]),
                    Lane(False, 'through', from_intsecs=[intsec_west_left])],
    ),
]


def main():
    running = True
    print('Rendering traffic conjunction...')
    lights_control = StaticLightsControl(lights_phases_config)
    traffic = Traffic(1, roads_config, cars_config, game_config)
    environment = Environment(screen, roads_config)
    while running:
        clock.tick(game_config["FPS"])

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        lights_control.next_tick()
        traffic.next_tick()
        environment.next_tick()

        # dialog
        if traffic.num_spawned_cars > 0 and len(traffic.all_cars) <= 0:
            environment.draw_dialog("All cars left")

        pygame.display.update()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
