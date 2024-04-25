import pygame
import os
import sys

from simulator.environment import Environment
from simulator.lights_control.static import Phase, StaticLightsControl
from simulator.lights_control.light import Light
from simulator.street import Lane, Street
from simulator.traffic import Traffic

pygame.init()

screen_width = 800
screen_height = 600
# put the window in the top left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
pygame.display.set_caption('Traffic Intersection Simulation')
screen = pygame.display.set_mode((screen_width, screen_height))


# game variables
FPS = 60
SIMULATE_DURATION = 60  # in seconds
clock = pygame.time.Clock()

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
    Phase([lit_north_through, lit_north_left,
          lit_south_through, lit_south_left], 10),
    Phase([lit_north_right, lit_south_right], 5),
    Phase([lit_west_through, lit_west_left, lit_east_through, lit_east_left], 10),
    Phase([lit_west_right, lit_east_right], 5)
]

roads_config = [
    Street(
        name="Lygon Street",
        x=screen_width//2-(road_width//2), y=0,
        width=road_width,
        length=screen_height//2-(road_width//2),
        divider_width=20,
        approach_direction="south",
        approach_lanes=[
            Lane(True, 'left', lit_south_left),
            Lane(True, 'through', lit_south_through),
            Lane(True, 'right', lit_south_right)
        ],
        exit_lanes=[Lane(False, 'through')]
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
            Lane(True, 'left', lit_east_left),
            Lane(True, 'through', lit_east_through),
            Lane(True, 'right', lit_east_right)
        ],
        exit_lanes=[Lane(False, 'through')],
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
            Lane(True, 'left', lit_west_left),
            Lane(True, 'through', lit_west_through),
            Lane(True, 'right', lit_west_right)
        ],
        exit_lanes=[Lane(False, 'through')],
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
            Lane(True, 'left', lit_north_left),
            Lane(True, 'through', lit_north_through),
            Lane(True, 'right', lit_north_right)
        ],
        exit_lanes=[Lane(False, 'through')],
    ),
]

cars_config = {
    "num_cars": 100,
}


def main():
    running = True
    print('Rendering traffic conjunction...')
    lights_control = StaticLightsControl(lights_phases_config)
    traffic = Traffic(1, roads_config, cars_config, SIMULATE_DURATION)
    environment = Environment(screen, roads_config)
    while running:
        clock.tick(FPS)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        lights_control.next_tick()
        traffic.next_tick()
        environment.draw()

        # dialog
        if traffic.num_spawned_cars > 0 and len(traffic.all_cars) <= 0:
            environment.draw_dialog("All cars left")

        # TODO: get next cars state
        # TODO: get next traffic lights state

        # TODO: calculate next cars state
        # TODO: RL, calculate next traffic lights state

        # TODO: update cars state
        # TODO: update traffic lights state
        pygame.display.update()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
