import pygame
import os
import sys

from simulator.environment import Environment
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
clock = pygame.time.Clock()

road_width = 200
roads_config = [
    Street(
        name="Lygon Street",
        x=screen_width//2-(road_width//2), y=0,
        width=road_width,
        length=screen_height//2-(road_width//2),
        divider_width=20,
        approach_direction="south",
        approach_lanes=[
            Lane(True, 'left'), Lane(True, 'through'), Lane(True, 'right')
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
            Lane(True, 'left'), Lane(True, 'through'), Lane(True, 'right')
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
            Lane(True, 'left'), Lane(True, 'through'), Lane(True, 'right')
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
            Lane(True, 'left'), Lane(True, 'through'), Lane(True, 'right')
        ],
        exit_lanes=[Lane(False, 'through')],
    ),
]

cars_config = [{
    "num_cars": 1000,
}]


def main():
    running = True
    print('Rendering traffic conjunction...')
    environment = Environment(screen, roads_config)
    traffic = Traffic(1, clock, roads_config, 1000)
    while running:
        clock.tick(FPS)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        environment.draw()
        traffic.next_tick()
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
