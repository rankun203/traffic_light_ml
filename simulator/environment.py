import pygame

from simulator.street import Lane, Street

# Initialize font
pygame.font.init()


class Environment:
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

    font_size = 16
    font_path = "./fonts/Noto_Sans/NotoSans-VariableFont_wdth,wght.ttf"
    lane_font = pygame.font.Font(font_path, font_size)  # Using a default font

    approach_width_ratio = 0.6

    def __init__(self, screen, roads_config: list[Street]):
        self._state = None
        self.screen = screen
        self.roads_config = roads_config

    def _draw_text(self, text, x, y, rotate, color=WHITE):
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
            pygame.draw.line(self.screen, self.LANE_LINE,
                             (x, y), (x, y + length))
            pygame.draw.line(self.screen, self.LANE_LINE, (x + width, y),
                             (x + width, y + length))
            self._draw_text(lane.to_direction, x + text_offset, y +
                            10, 90, self.ROAD_ACCENT)
            return (x + width, y)
        elif approach_direction == "south":
            # origin is bottom right
            pygame.draw.line(self.screen, self.LANE_LINE,
                             (x, y), (x, y - length))
            pygame.draw.line(self.screen, self.LANE_LINE, (x - width, y),
                             (x - width, y - length))
            self._draw_text(lane.to_direction, x - width + text_offset,
                            y - 10, 270, self.ROAD_ACCENT)
            return (x - width, y)
        elif approach_direction == "east":
            # origin is top right
            pygame.draw.line(self.screen, self.LANE_LINE,
                             (x, y), (x-length, y))
            pygame.draw.line(self.screen, self.LANE_LINE, (x, y+width),
                             (x-length, y+width))
            self._draw_text(lane.to_direction, x - 10, y +
                            text_offset, 0, self.ROAD_ACCENT)
            return (x, y+width)
        elif approach_direction == "west":
            # origin is bottom left
            pygame.draw.line(self.screen, self.LANE_LINE,
                             (x, y), (x+length, y))
            pygame.draw.line(self.screen, self.LANE_LINE, (x, y-width),
                             (x + length, y - width))
            self._draw_text(lane.to_direction, x + 10, y - width +
                            text_offset, 180, self.ROAD_ACCENT)
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
            # draw lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.DIVIDER, (start_x + 1, start_y,
                             st.divider_width - 1, st.length))
            start_x += st.divider_width
            # draw exit lanes
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

        elif st.approach_direction == "south":
            # draw right to left
            start_x = st.x + st.width
            start_y = st.y + st.length
            # draw lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.DIVIDER, (start_x -
                             st.divider_width, start_y - st.length, st.divider_width, st.length))
            start_x -= st.divider_width
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

        elif st.approach_direction == "east":
            # draw top to bottom
            start_x = st.x + st.length
            start_y = st.y
            # draw lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.DIVIDER, (start_x - st.length, start_y + 1,
                                                         st.length, st.divider_width - 1))
            start_y += st.divider_width
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

        elif st.approach_direction == "west":
            # draw bottom to top
            start_x = st.x
            start_y = st.y + st.width
            # draw lanes lines
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, approach_lane_width, st.approach_lanes)
            # draw divider
            pygame.draw.rect(self.screen, self.DIVIDER, (start_x, start_y - st.divider_width + 1,
                                                         st.length, st.divider_width - 1))
            start_y -= st.divider_width
            start_x, start_y = _draw_lanes_inner(
                start_x, start_y, exit_lane_width, st.exit_lanes)

    def _draw_streets(self):
        for st in self.roads_config:
            if st.approach_direction in ["north", "south"]:
                pygame.draw.rect(
                    self.screen, self.ROAD, (st.x, st.y, st.width, st.length))
            else:
                pygame.draw.rect(
                    self.screen, self.ROAD, (st.x, st.y, st.length, st.width))
            self._draw_lanes(st)

    def draw(self):
        self.screen.fill(self.BACKGROUND)
        self._draw_streets()