import pygame
import os
import sys

from simulator.environment import Environment
from simulator.lights_control.static import StaticPhase, StaticLightsControl
from simulator.lights_control.light import lit_north_left, lit_north_through, lit_north_right, lit_south_left, lit_south_through, lit_south_right, lit_west_left, lit_west_through, lit_west_right, lit_east_left, lit_east_through, lit_east_right
from simulator.traffic import Traffic
from simulator.config import screen_width, screen_height, streets, game_config, cars_config

pygame.init()

# put the window in the top left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
pygame.display.set_caption('Traffic Intersection Simulation')
screen = pygame.display.set_mode((screen_width, screen_height))

# game variables
clock = pygame.time.Clock()

# traffic lights phases
lights_phases_config = [
    StaticPhase([lit_north_right, lit_south_right], 5),
    StaticPhase([lit_north_through, lit_north_left,
                 lit_south_through, lit_south_left], 10),
    StaticPhase([lit_west_right, lit_east_right], 5),
    StaticPhase([lit_west_through, lit_west_left,
                lit_east_through, lit_east_left], 10),
]


def main():
    running = True
    print('Rendering traffic conjunction...')
    lights_control = StaticLightsControl(lights_phases_config)
    traffic = Traffic(1, streets, cars_config, game_config)
    environment = Environment(screen, streets)
    while running:
        clock.tick(game_config["FPS"])

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        phase_remain_s = lights_control.next_tick()
        traffic.next_tick()
        environment.next_tick()

        environment.draw_countdown(str(int(phase_remain_s)))

        # exit
        if traffic.num_spawned_cars > 0 and len(traffic.all_cars) <= 0:
            environment.draw_dialog("All cars left")

        pygame.display.update()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
