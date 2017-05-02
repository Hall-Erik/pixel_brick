# This will handle output to the 8x8 LED grid.

from sense_hat import SenseHat
import model

sense = SenseHat()

#colours
g = [0,100,0] # Green
b = [0,0,100] # Blue
y = [100,80,0] # Yellow
o = [100,50,0] # Orange
r = [100,0,0] # Red
e = [0,0,0] # Empty
w = [90,90,100]

# Empty grid
grid = [
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e,
e,e,e,e,e,e,e,e
]

class BlockView(object):
    def __init__(self, bus, weather, solar):
        global grid, sense
        self.bus = bus
        self.weather = weather
        self.solar = solar
        self.draw()

    def refresh(self):
        self.show_bus()
        self.show_uv()
        if self.updated:
            print(self.bus)
            print(self.weather)
            print(self.solar)
            self.draw()

    def draw(self):
        sense.set_pixels(grid)
        self.updated = False

    def set_pixel(self, pos, val):
        global grid
        if grid[pos] != val:
            grid[pos] = val
            self.updated = True

    # Sets a pixel and the pixel under it
    def set_column(self, pos, val):
        self.set_pixel(pos,val)
        self.set_pixel(pos+8,val)

    def show_bus(self):
        progress_rate = self.bus.progress_rate
        rows = 0
        if progress_rate == 1:
            color = g
        elif progress_rate == 0 or progress_rate == 4:
            color = b
        elif progress_rate == 2 or progress_rate == 3:
            color = r
        if progress_rate == 1 or progress_rate == 4 or progress_rate == 3:
            rows = 4
        elif progress_rate == 0 or progress_rate == 2:
            rows = 2
        else:
            rows = 0
        for i in range(0,rows*8-7,8): # rows
            for j in range(0,4): # column
                self.set_pixel(i+j, color)

    def show_uv(self):
        offset = 52 # starting point in the grid
        uv = self.weather.uv
        if uv > 0 and uv <= 3:
            for i in range(0,1): self.set_column(pos=i+offset, val=g)
            for i in range(1,4): self.set_column(pos=i+offset, val=e)
        elif uv > 3 and uv <= 6:
            for i in range(0,2): self.set_column(pos=i+offset, val=y)
            for i in range(2,4): self.set_column(pos=i+offset, val=e)
        elif uv > 6 and uv <= 8:
            for i in range(0,3): self.set_column(pos=i+offset, val=o)
            self.set_column(pos=3+offset, val=e)
        elif uv > 8:
            for i in range(0,4): self.set_column(pos=i+offset, val=r)
        else:
            for i in range(0,4): self.set_column(pos=i+offset, val=e)
