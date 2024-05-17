class Light:
    def __init__(self):
        self.color = "red"

    def set_green(self):
        self.color = "green"

    def set_yellow(self):
        self.color = "yellow"

    def set_red(self):
        self.color = "red"


# built in traffic lights, users can create more if needed
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
