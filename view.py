# This will handle output to the 8x8 LED grid.

# from sense_hat import SenseHat
# from nonsensehat import NonsenseHat
import model

# sense = SenseHat()

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

class TransitView(object):
    def __init__(self, sense, bus):
        self.bus = bus
        self.sense = sense

    def refresh(self):
        self.draw()

    def draw(self):
        sense = self.sense
        progress_rate = self.bus.progress_rate
        if progress_rate == 1:
            sense.show_message(text_string="Bus on time", scroll_speed=0.04, text_colour=g)
        elif progress_rate == 0:
            sense.show_message(text_string="Bus 5-10 min early", scroll_speed=0.04, text_colour=y)
        elif progress_rate == 4:
            sense.show_message(text_string="Bus 10+ min early", scroll_speed=0.04, text_colour=y)
        elif progress_rate == 2:
            sense.show_message(text_string="Bus 5-10 min late", scroll_speed=0.04, text_colour=r)
        elif progress_rate == 3:
            sense.show_message(text_string="Bus on 10+ min late", scroll_speed=0.04, text_colour=r)
        else:
            sense.show_message(text_string="No bus data", scroll_speed=0.04, text_colour=b)

class WeatherView(object):
    def __init__(self, sense, weather):
        self.weather = weather
        self.sense = sense

    def refresh(self):
        self.draw()

    def draw(self):
        sense = self.sense
        temp = self.weather.temp
        hi = self.weather.hi_now
        pop = self.weather.pop
        snow = self.weather.snow
        uv = self.weather.uv
        if sense.show_message(text_string="Temp: %dF" % temp, scroll_speed=0.04, text_colour=b) == 1:
            return
        if sense.show_message(text_string="Hi: %dF" % hi, scroll_speed=0.04, text_colour=r) == 1:
            return
        color = b if snow else w
        if sense.show_message(text_string="POP: %d%%" % pop, scroll_speed=0.04, text_colour=color) == 1:
            return
        sense.show_message(text_string="UV: %d" % uv, scroll_speed=0.04, text_colour=y)


class SolarView(object):
    def __init__(self, sense, solar):
        self.solar = solar
        self.sense = sense

    def refresh(self):
        self.draw()

    def draw(self):
        sense = self.sense
        s = "Solar today: %dkWh this month: %dkWh" % (self.solar.kWh_today/1000, self.solar.kWh_month/1000)
        sense.show_message(text_string=s, scroll_speed=0.04, text_colour=y)

class BlockView(object):
    def __init__(self, sense, bus, weather, solar):
        self.bus = bus
        self.weather = weather
        self.solar = solar
        self.sense = sense
        self.draw()

    def clear(self):
        global grid
        grid = [e for x in range(0,64)]
        self.draw()

    def refresh(self):
        sense = self.sense
        self.show_bus()
        self.show_uv()
        self.show_pop()
        self.show_his()
        self.show_curr()
        self.show_solar_summary()
        self.show_solar_month()
        if self.updated or sense.get_pixels() == [e for x in range(0,64)] and sense.get_pixels() != grid:
            self.draw()

    def draw(self):
        sense = self.sense
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

    def show_pop(self):
        offset = 36
        pop = self.weather.pop
        color = w if self.weather.snow else b

        if pop > 0 and pop <= 25:
            for i in range(0,1): self.set_column(pos=i+offset, val=color)
            for i in range(1,4): self.set_column(pos=i+offset, val=e)
        elif pop > 25 and pop <= 50:
            for i in range(0,2): self.set_column(pos=i+offset, val=color)
            for i in range(2,4): self.set_column(pos=i+offset, val=e)
        elif pop > 50 and pop <= 75:
            for i in range(0,3): self.set_column(pos=i+offset, val=color)
            for i in range(3,4): self.set_column(pos=i+offset, val=e)
        elif pop > 75:
            for i in range(0,4): self.set_column(pos=i+offset, val=color)
        else:
            for i in range(0,4): self.set_column(pos=i+offset, val=e)

    def show_his(self):
        offset = 48
        hi_now = self.weather.hi_now
        hi_tom = self.weather.hi_tom
        color = o if hi_tom > hi_now else b
        diff = abs(hi_now - hi_tom)

        if diff > 0 and diff <= 5:
            for i in range(0,1): self.set_column(pos=i+offset, val=color)
            for i in range(1,4): self.set_column(pos=i+offset, val=e)
        elif diff > 5 and diff <= 10:
            for i in range(0,2): self.set_column(pos=i+offset, val=color)
            for i in range(2,4): self.set_column(pos=i+offset, val=e)
        elif diff > 10 and diff <= 15:
            for i in range(0,3): self.set_column(pos=i+offset, val=color)
            for i in range(3,4): self.set_column(pos=i+offset, val=e)
        elif diff > 15:
            for i in range(0,4): self.set_column(pos=i+offset, val=color)
        else:
            for i in range(0,4): self.set_column(pos=i+offset, val=e)

    def show_curr(self):
        offset = 32
        temp = self.weather.temp
        temp_yes = self.weather.temp_yes
        color = o if temp > temp_yes else b
        diff = abs(temp - temp_yes)

        if diff > 0 and diff <= 5:
            for i in range(0,1): self.set_column(pos=i+offset, val=color)
            for i in range(1,4): self.set_column(pos=i+offset, val=e)
        elif diff > 5 and diff <= 10:
            for i in range(0,2): self.set_column(pos=i+offset, val=color)
            for i in range(2,4): self.set_column(pos=i+offset, val=e)
        elif diff > 10 and diff <= 15:
            for i in range(0,3): self.set_column(pos=i+offset, val=color)
            for i in range(3,4): self.set_column(pos=i+offset, val=e)
        elif diff > 15:
            for i in range(0,4): self.set_column(pos=i+offset, val=color)
        else:
            for i in range(0,4): self.set_column(pos=i+offset, val=e)

    def show_solar_summary(self):
        offset = 4
        kWh_today = self.solar.kWh_today
        daily_rcd = self.solar.daily_rcd
        perc = float(kWh_today) / float(daily_rcd) * 100
        color = y
        if perc > 0 and perc <= 25:
            for i in range(0,1): self.set_column(pos=i+offset, val=color)
            for i in range(1,4): self.set_column(pos=i+offset, val=e)
        elif perc > 25 and perc <= 50:
            for i in range(0,2): self.set_column(pos=i+offset, val=color)
            for i in range(2,4): self.set_column(pos=i+offset, val=e)
        elif perc > 50 and perc <= 75:
            for i in range(0,3): self.set_column(pos=i+offset, val=color)
            for i in range(3,4): self.set_column(pos=i+offset, val=e)
        elif perc > 75:
            for i in range(0,4): self.set_column(pos=i+offset, val=color)
        else:
            for i in range(0,4): self.set_column(pos=i+offset, val=e)

    def show_solar_month(self):
        offset = 20
        kWh_month = self.solar.kWh_month
        monthly_rcd = self.solar.monthly_rcd
        perc = float(kWh_month) / float(monthly_rcd) * 100
        color = y
        if perc > 0 and perc <= 25:
            for i in range(0,1): self.set_column(pos=i+offset, val=color)
            for i in range(1,4): self.set_column(pos=i+offset, val=e)
        elif perc > 25 and perc <= 50:
            for i in range(0,2): self.set_column(pos=i+offset, val=color)
            for i in range(2,4): self.set_column(pos=i+offset, val=e)
        elif perc > 50 and perc <= 75:
            for i in range(0,3): self.set_column(pos=i+offset, val=color)
            for i in range(3,4): self.set_column(pos=i+offset, val=e)
        elif perc > 75:
            for i in range(0,4): self.set_column(pos=i+offset, val=color)
        else:
            for i in range(0,4): self.set_column(pos=i+offset, val=e)
