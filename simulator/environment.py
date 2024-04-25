import pygame
import math

from simulator.street import Lane, Street

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

    def _draw_lane_label(self, text, x, y, rotate, color=COLORS["WHITE"]):
        text_surface = self.lane_font.render(text, True, color)
        rotated_text_surface = pygame.transform.rotate(text_surface, rotate)
        if rotate == 0:
            x = x - rotated_text_surface.get_width()
        elif rotate == 270:
            y = y - rotated_text_surface.get_height()
        self.screen.blit(rotated_text_surface, (x, y))

    def _draw_cars_on_lane(self, lane: Lane, x, y, width, length, approach_direction):
        for car in lane.cars:
            # calculate car position
            if approach_direction == "north":
                car_x = x + width // 2 - 5
                car_y = y + length - car.travel_distance
                if not lane.is_approach:
                    car_y = y + car.travel_distance - car.length
                pygame.draw.rect(self.screen, car.color, (car_x,
                                 car_y, car.width, car.length))
            elif approach_direction == "south":
                car_x = x - width // 2 - 5
                car_y = y - length + car.travel_distance - car.length
                if not lane.is_approach:
                    car_y = y - car.travel_distance
                pygame.draw.rect(self.screen, car.color, (car_x,
                                 car_y, car.width, car.length))
            elif approach_direction == "east":
                car_x = x - length + car.travel_distance - car.length
                car_y = y + width // 2 - 5
                if not lane.is_approach:
                    car_x = x - car.travel_distance
                pygame.draw.rect(self.screen, car.color, (car_x,
                                 car_y, car.length, car.width))
            elif approach_direction == "west":
                car_x = x + length - car.travel_distance
                car_y = y - width // 2 - 5
                if not lane.is_approach:
                    car_x = x + car.travel_distance - car.length
                pygame.draw.rect(self.screen, car.color, (car_x,
                                 car_y, car.length, car.width))

    def _draw_lane(self, lane: Lane, x, y, width, length, approach_direction):
        text_offset = width // 2 - 10
        """Must choose the right origin for x, y"""
        if approach_direction == "north":
            # origin is top left
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"],
                             (x, y), (x, y + length))
            pygame.draw.line(self.screen, self.COLORS["LANE_LINE"], (x + width, y),
                             (x + width, y + length))
            lane.set_geo(int(x), int(y), int(x+width), int(y), width, length)
            self._draw_lane_label(lane.to_direction, x + text_offset, y +
                                  10, 90, self.COLORS["ROAD_ACCENT"])
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
            self._draw_lane_label(lane.to_direction, x - width + text_offset,
                                  y - 10, 270, self.COLORS["ROAD_ACCENT"])
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
            self._draw_lane_label(lane.to_direction, x - 10, y +
                                  text_offset, 0, self.COLORS["ROAD_ACCENT"])
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
            self._draw_lane_label(lane.to_direction, x + 10, y - width +
                                  text_offset, 180, self.COLORS["ROAD_ACCENT"])
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
                    elif lane.to_direction == 'right':
                        x, y = lane.right_x, to_lane.left_y
                        sa, ea = 90, 180
                        if lane.street.approach_direction == 'north':
                            x, y = lane.right_x, to_lane.left_y
                            sa, ea = 90, 180
                        elif lane.street.approach_direction == 'south':
                            x = to_lane.left_x - lane.right_x + to_lane.left_x
                            y = lane.right_y - to_lane.left_y + lane.right_y
                            sa, ea = 270, 0
                        elif lane.street.approach_direction == 'east':
                            x = lane.right_x - to_lane.left_x + lane.right_x
                            y = lane.right_y
                            sa, ea = 0, 90
                        elif lane.street.approach_direction == 'west':
                            x = to_lane.left_x
                            y = to_lane.left_y - lane.right_y + to_lane.left_y
                            sa, ea = 180, 270

                        # Define the bounding rectangle for the arc
                        arc_rect = pygame.Rect(
                            x, y,
                            abs(to_lane.left_x - lane.right_x) * 2,
                            abs(to_lane.left_y - lane.right_y) * 2
                        )
                        self.screen.set_at((x, y), self.COLORS["RED"])

                        start_angle = math.radians(sa)
                        end_angle = math.radians(ea)
                        pygame.draw.arc(
                            self.screen, self.COLORS["WHITE"], arc_rect, start_angle, end_angle)

                        # pygame.draw.line(self.screen, self.COLORS["WHITE"], (
                        #     lane.right_x, lane.right_y), (to_lane.left_x, to_lane.left_y))
                    print('intersection', lane, to_lane)

    def _draw_timer(self):
        # draw elapsed time
        clock_ms = pygame.time.get_ticks()
        self._draw_text(f"{clock_ms//1000}", 10, 2, 0, self.COLORS["WHITE"])

    def draw_dialog(self, text: str):
        width, height = self.screen.get_width(), self.screen.get_height()
        dialog_h = 100

        dialog_y = (height // 2) - (dialog_h // 2)
        print("Draw dialog", text, pygame.time.get_ticks())
        pygame.draw.rect(
            self.screen, self.COLORS["WHITE"], (0, dialog_y, width, dialog_h))
        self._draw_text(text, width // 2, dialog_y + dialog_h //
                        2, 0, self.COLORS["BLACK"], h_center=True, v_center=True)

    def next_tick(self):
        self.screen.fill(self.COLORS["BACKGROUND"])
        self._draw_streets()
        self._draw_intersections()
        self._draw_timer()
