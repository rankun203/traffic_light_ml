import pygame
import os
import sys

pygame.init()

screen_width = 800
screen_height = 600
# put the window in the top left corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
pygame.display.set_caption('Traffic Intersection Simulation')
screen = pygame.display.set_mode((screen_width, screen_height))

# Initialize font
pygame.font.init()
font_size = 16
font_path = "./fonts/Noto_Sans/NotoSans-VariableFont_wdth,wght.ttf"
lane_font = pygame.font.Font(font_path, font_size)  # Using a default font

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BACKGROUND = (68, 80, 99)
ROAD = (47, 52, 64)
ROAD_ACCENT = (98, 110, 129)
LANE_LINE = (255, 255, 255)
DIVIDER = (41, 96, 92)


# game variables
FPS = 60
clock = pygame.time.Clock()

road_width = 200
roads_config = [{
    "name": "Lygon Street",
    "x": screen_width//2-(road_width//2),
    "y": 0,
    "width": road_width,
    "length": screen_height//2-(road_width//2),
    "divider_width": 20,
    "approach_direction": "south",
    "approach_lanes": ['left', 'through', 'right'],
    "exit_lanes": ['through'],
}, {
    "name": "Victoria Street",
    "x": 0,
    "y": screen_height//2-(road_width//2),
    "width": road_width,
    "length": screen_width//2-(road_width//2),
    "divider_width": 20,
    "approach_direction": "east",
    "approach_lanes": ['left', 'through', 'right'],
    "exit_lanes": ['through'],
}, {
    "name": "Victoria Street",
    "x": screen_width//2+(road_width//2),
    "y": screen_height//2-(road_width//2),
    "width": road_width,
    "length": screen_width//2-(road_width//2),
    "divider_width": 20,
    "approach_direction": "west",
    "approach_lanes": ['left', 'through', 'right'],
    "exit_lanes": ['through'],
}, {
    "name": "Russell Street",
    "x": screen_width//2-(road_width//2),
    "y": screen_height//2+(road_width//2),
    "width": road_width,
    "length": screen_height//2-(road_width//2),
    "divider_width": 20,
    "approach_direction": "north",
    "approach_lanes": ['left', 'through', 'right'],
    "exit_lanes": ['through'],
}]


def draw_text(text, x, y, rotate, color=WHITE):
    text_surface = lane_font.render(text, True, color)
    rotated_text_surface = pygame.transform.rotate(text_surface, rotate)
    if rotate == 0:
        x = x - rotated_text_surface.get_width()
    elif rotate == 270:
        y = y - rotated_text_surface.get_height()
    screen.blit(rotated_text_surface, (x, y))


def draw_lanes(road):
    """
    draw approach and exit lanes with 2 lines for each lane
    """
    # Determine the maximum number of lanes for this road
    total_lanes = len(road["approach_lanes"]) + len(road["exit_lanes"])

    # Calculate the width of each lane based on the road width and the number of lanes
    lane_width = (road["width"] - road["divider_width"]) / total_lanes

    start_x, start_y = road["x"], road["y"]  # initialize origin

    def draw_lane(name, x, y, width, length, approach_direction):
        """Must choose the right origin for x, y"""
        if approach_direction == "north":
            # origin is top left
            pygame.draw.line(screen, LANE_LINE, (x, y), (x, y + length))
            pygame.draw.line(screen, LANE_LINE, (x + width, y),
                             (x + width, y + length))
            draw_text(name, x + 12, start_y + 10, 90, ROAD_ACCENT)
            return (x + width, y)
        elif approach_direction == "south":
            # origin is bottom right
            pygame.draw.line(screen, LANE_LINE, (x, y), (x, y - length))
            pygame.draw.line(screen, LANE_LINE, (x - width, y),
                             (x - width, y - length))
            draw_text(name, x - lane_width + 12,
                      start_y - 10, 270, ROAD_ACCENT)
            return (x - width, y)
        elif approach_direction == "east":
            # origin is top right
            pygame.draw.line(screen, LANE_LINE, (x, y), (x-length, y))
            pygame.draw.line(screen, LANE_LINE, (x, y+width),
                             (x-length, y+width))
            draw_text(name, x - 10, y + 12, 0, ROAD_ACCENT)
            return (x, y+width)
        elif approach_direction == "west":
            # origin is bottom left
            pygame.draw.line(screen, LANE_LINE, (x, y), (x+length, y))
            pygame.draw.line(screen, LANE_LINE, (x, y-width),
                             (x + length, y - width))
            draw_text(name, x + 10, y - lane_width + 12, 180, ROAD_ACCENT)
            return (x, y-width)
        return (x, y)

    def draw_lane_lines(start_x, start_y, lanes):
        for lane_name in lanes:
            start_x, start_y = draw_lane(
                lane_name, start_x, start_y, lane_width, road["length"], road["approach_direction"])
        return start_x, start_y

    if road["approach_direction"] == "north":
        # draw left to right
        start_x = road["x"]
        start_y = road["y"]
        # draw lanes lines
        print('before', start_x, start_y)
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["approach_lanes"])
        print('after', start_x, start_y)
        # draw divider
        pygame.draw.rect(screen, DIVIDER, (start_x + 1, start_y,
                         road["divider_width"] - 1, road["length"]))
        start_x += road["divider_width"]
        # draw exit lanes
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["exit_lanes"])

    elif road["approach_direction"] == "south":
        # draw right to left
        start_x = road["x"] + road["width"]
        start_y = road["y"] + road["length"]
        # draw lanes lines
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["approach_lanes"])
        # draw divider
        pygame.draw.rect(screen, DIVIDER, (start_x -
                         road["divider_width"], start_y - road["length"], road["divider_width"], road["length"]))
        start_x -= road["divider_width"]
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["exit_lanes"])

    elif road["approach_direction"] == "east":
        # draw top to bottom
        start_x = road["x"] + road["length"]
        start_y = road["y"]
        # draw lanes lines
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["approach_lanes"])
        # draw divider
        pygame.draw.rect(screen, DIVIDER, (start_x - road["length"], start_y + 1,
                                           road["length"], road["divider_width"] - 1))
        start_y += road["divider_width"]
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["exit_lanes"])

    elif road["approach_direction"] == "west":
        # draw bottom to top
        start_x = road["x"]
        start_y = road["y"] + road["width"]
        # draw lanes lines
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["approach_lanes"])
        # draw divider
        pygame.draw.rect(screen, DIVIDER, (start_x, start_y - road["divider_width"] + 1,
                                           road["length"], road["divider_width"] - 1))
        start_y -= road["divider_width"]
        start_x, start_y = draw_lane_lines(
            start_x, start_y, road["exit_lanes"])


def draw_streets():
    for road in roads_config:
        if road["approach_direction"] in ["north", "south"]:
            pygame.draw.rect(
                screen, ROAD, (road["x"], road["y"], road["width"], road["length"]))
        else:
            pygame.draw.rect(
                screen, ROAD, (road["x"], road["y"], road["length"], road["width"]))
        draw_lanes(road)


def draw_environment():
    screen.fill(BACKGROUND)
    draw_streets()


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
