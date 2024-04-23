import pygame
import os
import sys

pygame.init()

screen_width=800
screen_height=600
# put the window in the top left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
pygame.display.set_caption('Traffic Conjunction')
screen = pygame.display.set_mode((screen_width, screen_height))

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BACKGROUND = (68, 80, 99)
ROAD = (47, 52, 64)

# game variables
FPS = 60
clock = pygame.time.Clock()

def draw_roads():
    road_width = 200
    roads = [{
        "x": screen_width//2-(road_width//2),
        "y": 0,
        "width": road_width,
        "height": screen_height
    }, {
        "x": 0,
        "y": screen_height//2-(road_width//2),
        "width": screen_width,
        "height": road_width
    }]
    for road in roads:
        pygame.draw.rect(screen, ROAD, (road["x"], road["y"], road["width"], road["height"]))

def draw_environment():
    screen.fill(BACKGROUND)
    draw_roads()

def main():
    running = True
    print('Rendering traffic conjunction...')
    while running:
        clock.tick(FPS)

        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_environment()
        pygame.display.update()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
