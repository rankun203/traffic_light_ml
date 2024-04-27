import pygame
import math
from simulator.car import Car

from simulator.street import Intersection, Lane, Street

# Initialize font
pygame.font.init()


class Environment:
    # colors
    COLORS = {
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "RED": (255, 0, 0),
        "GREEN": (0, 255, 0),
        "YELLOW": (255, 255, 0),
        "BACKGROUND": (68, 80, 99),
        "BACKGROUND_ACCENT": (41, 96, 92),
        "ROAD": (47, 52, 64),
        "ROAD_ACCENT": (98, 110, 129),
        "LANE_LINE": (255, 255, 255),
        "DIVIDER": (41, 96, 92),
    }

    signs = {
        "left_right": pygame.image.load('./icons/png/sign_left_right.png'),
        "left_through_right": pygame.image.load('./icons/png/sign_through_right.png'),
        "left_through": pygame.image.load('./icons/png/sign_left_through.png'),
        "left": pygame.image.load('./icons/png/sign_left.png'),
        "right": pygame.image.load('./icons/png/sign_right.png'),
        "through_right": pygame.image.load('./icons/png/sign_through_right.png'),
        "through": pygame.image.load('./icons/png/sign_through.png'),
    }

    font_size = 16
    font_path = "./fonts/Noto_Sans/NotoSans-VariableFont_wdth,wght.ttf"
    lane_font = pygame.font.Font(font_path, font_size)  # Using a default font

    approach_width_ratio = 0.6

    def __init__(self, screen: pygame.Surface, roads_config: list[Street]):
        self.screen = screen
        self.roads_config = roads_config

    def _draw_text(self, text, x, y, rotate, color=COLORS["WHITE"], h_center=False, v_center=False):
        text_surface = self.lane_font.render(text, True, color)
        rotated_text_surface = pygame.transform.rotate(text_surface, rotate)
        if h_center:
            x = x - rotated_text_surface.get_width() // 2
        if v_center:
            y = y - rotated_text_surface.get_height() // 2
        self.screen.blit(rotated_text_surface, (x, y))

    def _draw_lane_label(self, to_direction, x, y, rotate, color=COLORS["WHITE"]):
        text_surface = self.signs[to_direction]
        # self.screen.blit(self.signs["left"], (x, y))
        rotated_text_surface = pygame.transform.rotate(text_surface, rotate)
        # if rotate == 0:
        #     x = x - rotated_text_surface.get_width()
        # elif rotate == 270:
        #     y = y - rotated_text_surface.get_height()
        self.screen.blit(rotated_text_surface, (x, y))

    def _draw_car(self, car: Car):
        car_surface = pygame.Surface((car.width, car.length), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, car.color, car_surface.get_rect())
        rotated_car_surface = pygame.transform.rotate(car_surface, car.rotate)
        rotated_rect = rotated_car_surface.get_rect(center=(car.x, car.y))

        # Blit the rotated car surface onto the screen at the position of the rotated rect
        self.screen.blit(rotated_car_surface, rotated_rect.center)

    def _draw_cars_on_lane(self, lane: Lane, x, y, width, length, approach_direction):
        for car in lane.cars:
            # calculate car position
            if approach_direction == "north":
                car_x = x + width // 2 - 5
                car_y = y + length - car.travel_distance
                if not lane.is_approach:
                    car_y = y + car.travel_distance - car.length
                car.set_geo(car_x, car_y, 0)
            elif approach_direction == "south":
                car_x = x - width // 2 - 5
                car_y = y - length + car.travel_distance - car.length
                if not lane.is_approach:
                    car_y = y - car.travel_distance
                car.set_geo(car_x, car_y, 0)
            elif approach_direction == "east":
                car_x = x - length + car.travel_distance - car.length
                car_y = y + width // 2 - 5
                if not lane.is_approach:
                    car_x = x - car.travel_distance
                car.set_geo(car_x, car_y, 90)
            elif approach_direction == "west":
                car_x = x + length - car.travel_distance
                car_y = y - width // 2 - 5
                if not lane.is_approach:
                    car_x = x + car.travel_distance - car.length
                car.set_geo(car_x, car_y, 90)
            self._draw_car(car)

    def _draw_lane(self, lane: Lane, x, y, width, length, approach_direction):
        label_offset = width // 2 - 8
        """Must choose the right origin for x, y"""
        if approach_direction == "north":
            # origin is top left
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"],
                             (x, y), (x, y + length))
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"], (x + width, y),
                             (x + width, y + length))
            lane.set_geo(int(x), int(y), int(x+width), int(y), width, length)
            if lane.is_approach:
                self._draw_lane_label(lane.to_direction, x + label_offset, y +
                                      10, 0, self.COLORS["ROAD_ACCENT"])
            # self._draw_sign(approach_direction, lane.to_direction, x, y)
            # Draw traffic light
            if lane.is_approach and lane.light:
                lit_color = self.COLORS[lane.light.color.upper()]
                pygame.draw.rect(self.screen, lit_color, (x, y-5, width, 5))

            return (x + width, y)
        elif approach_direction == "south":
            # origin is bottom right
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"],
                             (x, y), (x, y - length))
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"], (x - width, y),
                             (x - width, y - length))
            lane.set_geo(int(x), int(y), int(x-width), int(y), width, length)
            if lane.is_approach:
                self._draw_lane_label(lane.to_direction, x - width + label_offset,
                                      y - 45, 180, self.COLORS["ROAD_ACCENT"])
            # self._draw_sign(approach_direction, lane.to_direction, x, y)
            # Draw traffic light
            if lane.is_approach and lane.light:
                lit_color = self.COLORS[lane.light.color.upper()]
                pygame.draw.rect(self.screen, lit_color,
                                 (x-width+1, y, width, 5))

            return (x - width, y)
        elif approach_direction == "east":
            # origin is top right
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"],
                             (x, y), (x-length, y))
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"], (x, y+width),
                             (x-length, y+width))
            lane.set_geo(int(x), int(y), int(x), int(y+width), width, length)
            if lane.is_approach:
                self._draw_lane_label(lane.to_direction, x - 45, y +
                                      label_offset, 270, self.COLORS["ROAD_ACCENT"])
            # self._draw_sign(approach_direction, lane.to_direction, x, y)
            # Draw traffic light
            if lane.is_approach and lane.light:
                lit_color = self.COLORS[lane.light.color.upper()]
                pygame.draw.rect(self.screen, lit_color, (x, y+1, 5, width))

            return (x, y+width)
        elif approach_direction == "west":
            # origin is bottom left
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"],
                             (x, y), (x+length, y))
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"], (x, y-width),
                             (x + length, y - width))
            lane.set_geo(int(x), int(y), int(x), int(y-width), width, length)
            if lane.is_approach:
                self._draw_lane_label(lane.to_direction, x + 10, y - width +
                                      label_offset, 90, self.COLORS["ROAD_ACCENT"])
            # self._draw_sign(approach_direction, lane.to_direction, x, y)
            # Draw traffic light
            if lane.is_approach and lane.light:
                lit_color = self.COLORS[lane.light.color.upper()]
                pygame.draw.rect(self.screen, lit_color,
                                 (x-5, y-width, 5, width))

            return (x, y-width)
        return (x, y)

    def _draw_lanes(self, st: Street):
        """
        draw approach and exit lanes with 2 lines for each lane
        """
        # Calculate the width of each lane based on the road width and the number of lanes
        approach_lane_width = (
            st.width - st.divider_width) * Environment.approach_width_ratio / len(st.approach_lanes)
        exit_lane_width = (st.width - st.divider_width) * \
            (1 - Environment.approach_width_ratio) / len(st.exit_lanes)

        start_x, start_y = st.x, st.y  # initialize origin

        def _draw_lanes_inner(start_x, start_y, width, lanes: list[Lane]):
            for lane in lanes:
                old_x, old_y = start_x, start_y
                start_x, start_y = self._draw_lane(
                    lane, start_x, start_y, width, st.length, st.approach_direction)
                if len(lane.cars) > 0:
                    self._draw_cars_on_lane(lane, old_x, old_y, width, st.length,
                                            st.approach_direction)
            return start_x, start_y

        if st.approach_direction == "north":
            # draw left to right
            start_x = st.x
            start_y = st.y
            # draw approaching lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.COLORS["DIVIDER"], (start_x + 1, start_y,
                             st.divider_width - 1, st.length))
            start_x += st.divider_width
            # draw exit lanes
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

        elif st.approach_direction == "south":
            # draw right to left
            start_x = st.x + st.width
            start_y = st.y + st.length
            # draw approaching lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.COLORS["DIVIDER"], (start_x -
                             st.divider_width, start_y - st.length, st.divider_width, st.length))
            start_x -= st.divider_width
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

        elif st.approach_direction == "east":
            # draw top to bottom
            start_x = st.x + st.length
            start_y = st.y
            # draw approaching lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.COLORS["DIVIDER"], (start_x - st.length, start_y + 1,
                                                                   st.length, st.divider_width - 1))
            start_y += st.divider_width
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

        elif st.approach_direction == "west":
            # draw bottom to top
            start_x = st.x
            start_y = st.y + st.width
            # draw approaching lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.COLORS["DIVIDER"], (start_x, start_y - st.divider_width + 1,
                                                                   st.length, st.divider_width - 1))
            start_y -= st.divider_width
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

    def _draw_streets(self):
        for st in self.roads_config:
            if st.approach_direction in ["north", "south"]:
                pygame.draw.rect(
                    self.screen, self.COLORS["ROAD"], (st.x, st.y, st.width, st.length))
            else:
                pygame.draw.rect(
                    self.screen, self.COLORS["ROAD"], (st.x, st.y, st.length, st.width))
            self._draw_lanes(st)

    def point_at_percentage(self, ax: int, ay: int, bx: int, by: int, t: float):
        return (ax + t * (bx - ax), ay + t * (by - ay))

    def _draw_intersections(self):
        for st in self.roads_config:
            for lane in st.approach_lanes:
                if lane.light and lane.light.color == 'red':
                    continue
                if lane.to_intsec is not None and lane.to_intsec.to_lane is not None:
                    to_lane = lane.to_intsec.to_lane
                    # draw a line from lane.x, lane.y to to_lane.x, to_lane.y
                    if lane.to_direction == 'left':
                        pass
                        # pygame.draw.line(self.screen, self.COLORS["BACKGROUND_ACCENT"], (
                        #     lane.right_x, lane.right_y), (to_lane.left_x, to_lane.left_y))
                    elif lane.to_direction == 'through':
                        pygame.draw.line(self.screen, self.COLORS["WHITE"], (
                            lane.right_x, lane.right_y), (to_lane.left_x, to_lane.left_y))
                        lane.to_intsec.set_length(int(math.sqrt(
                            (lane.right_x - to_lane.left_x)**2 + (lane.right_y - to_lane.left_y)**2)))
                        for car in lane.to_intsec.cars:
                            car_per = car.travel_distance / lane.to_intsec.length
                            x, y = self.point_at_percentage(
                                lane.right_x, lane.right_y, to_lane.left_x, to_lane.left_y, car_per)
                            di = lane.street.approach_direction
                            x_offset = 0
                            y_offset = 0
                            rot = 0
                            if di == 'north':
                                x_offset = -1 * \
                                    (lane.width // 2 + car.width // 2)
                                y_offset = -1 * car.length
                                rot = 0
                            elif di == 'west':
                                x_offset = -1 * car.length
                                y_offset = lane.width // 2 - car.width // 2
                                rot = 90
                            elif di == 'south':
                                x_offset = lane.width // 2 - car.width // 2
                                rot = 0
                            elif di == 'east':
                                y_offset = -1*(lane.width // 2 + car.width//2)
                                rot = 90

                            car.set_geo(x + x_offset, y + y_offset, rot)
                            self._draw_car(car)
                    elif lane.to_direction == 'right':
                        x, y = lane.right_x, to_lane.left_y
                        pygame.draw.line(self.screen, self.COLORS["WHITE"], (
                            lane.right_x, lane.right_y), (to_lane.left_x, to_lane.left_y))

                        length = int(math.sqrt(
                            (lane.right_x - to_lane.left_x)**2 + (lane.right_y - to_lane.left_y)**2))
                        lane.to_intsec.set_length(length)
                        for car in lane.to_intsec.cars:
                            car_pre = car.travel_distance / length
                            x, y = self.point_at_percentage(
                                lane.right_x, lane.right_y, to_lane.left_x, to_lane.left_y, car_pre)

                            di = lane.street.approach_direction
                            x_offset = 0
                            y_offset = 0
                            slope = abs(lane.right_x - to_lane.left_x) / \
                                abs(lane.right_y - to_lane.left_y)
                            rot = int(math.degrees(math.atan(slope)))
                            if di == 'north':
                                x_offset = -1 * \
                                    (lane.width // 2 + car.width // 2)
                                y_offset = -1 * car.length
                                rot = 180 - rot
                            elif di == 'west':
                                x_offset = -1 * (car.length + lane.width // 2)
                                y_offset = lane.width // 2 - car.length
                            elif di == 'south':
                                x_offset = lane.width // 2 - car.width // 2
                                rot = 180 - rot
                            elif di == 'east':
                                y_offset = -1*(lane.width // 2 + car.width//2)

                            car.set_geo(x+x_offset, y+y_offset, rot)
                            self._draw_car(car)

    def _draw_timer(self):
        # draw elapsed time
        clock_ms = pygame.time.get_ticks()
        self._draw_text(f"World time: {clock_ms//1000}s", 10, 8, 0, self.COLORS["WHITE"])

    def draw_countdown(self, count: str):
        width, height = self.screen.get_width(), self.screen.get_height()
        self._draw_text(f"Count down: {count}",
                        10, 40, 0, self.COLORS["WHITE"])

    def draw_dialog(self, text: str):
        width, height = self.screen.get_width(), self.screen.get_height()
        dialog_h = 100

        dialog_y = (height // 2) - (dialog_h // 2)
        print("Draw dialog", text, pygame.time.get_ticks()//1000)
        pygame.draw.rect(
            self.screen, self.COLORS["WHITE"], (0, dialog_y, width, dialog_h))
        self._draw_text(text, width // 2, dialog_y + dialog_h //
                        2, 0, self.COLORS["BLACK"], h_center=True, v_center=True)

    def next_tick(self):
        self.screen.fill(self.COLORS["BACKGROUND"])
        self._draw_streets()
        self._draw_intersections()
        self._draw_timer()
