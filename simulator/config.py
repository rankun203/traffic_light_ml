# intersections for each lane
from simulator.street import Intersection, Lane, Street
from simulator.lights_control.light import lit_north_left, lit_north_through, lit_north_right, lit_south_left, lit_south_through, lit_south_right, lit_west_left, lit_west_through, lit_west_right, lit_east_left, lit_east_through, lit_east_right

screen_width = 800
screen_height = 600

game_config = {
    "FPS": 60,  # frames per second
    "SIMULATE_DURATION": 60,  # in seconds, cars are distributed over this time
    "screen_width": 800,
    "screen_height": 600,
}

cars_config = {
    "num_cars": 200,
    # px per second, 1px = 0.1m, that's 120px/s = 12m/s = 43.2km/h
    "init_speed": 120,
}

# Layout: street width in pixels
street_width = 200

# Intersection instances
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


# Streets instances, 4 streets are connected to the intersection
roads_config = [
    Street(
        name="Lygon Street",
        x=screen_width//2-(street_width//2), y=0,
        width=street_width,
        length=screen_height//2-(street_width//2),
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
        y=screen_height//2-(street_width//2),
        width=street_width,
        length=screen_width//2-(street_width//2),
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
        x=screen_width//2+(street_width//2),
        y=screen_height//2-(street_width//2),
        width=street_width,
        length=screen_width//2-(street_width//2),
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
        x=screen_width//2-(street_width//2),
        y=screen_height//2+(street_width//2),
        width=street_width,
        length=screen_height//2-(street_width//2),
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
