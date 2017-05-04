from sense_hat import SenseHat
from time import sleep, strftime, localtime
import model
import view
import thread
import os
import traceback
import datetime

sense = SenseHat()

# Initialize models
weather = model.WeatherModel()
bus = model.BusModel()
solar = model.SolarModel()

bView = view.BlockView(bus,weather,solar)

#If true show default pixel display
show_blocks = True

#colours
g = [0,100,0] # Green
b = [0,0,100] # Blue
y = [100,80,0] # Yellow
o = [100,50,0] # Orange
r = [100,0,0] # Red
e = [0,0,0] # Empty
w = [90,90,100]
#
# def show_bus(progress_rate):
#     if progress_rate == 1: # On time
#         color = g
#         rows = 4
#     elif progress_rate == 0: # 5-10 min early
#         color = b
#         rows = 2
#     elif progress_rate == 4: # 10+ min early
#         color = b
#         rows = 4
#     elif progress_rate == 2: # 5-10 min late
#         color = r
#         rows = 2
#     elif progress_rate == 3: # 10+ min late
#         color = r
#         rows = 4
#     else:
#         rows = 0
#     while rows > 0:
#         rows -= 1
#         for x in range(4):
#             sense.set_pixel(x, rows, color)
#
# def show_uv(uv):
#     cols = 0
#     color = g
#     if uv > 0 and uv <= 3:
#         color = g
#         cols = 1
#     elif uv > 3 and uv <= 6:
#         color = y
#         cols = 2
#     elif uv > 6 and uv <= 8:
#         color = o
#         cols = 3
#     elif uv > 8:
#         color = r
#         cols = 4
#     while cols > 0:
#         cols -= 1
#         sense.set_pixel(4+cols,6,color)
#         sense.set_pixel(4+cols,7,color)
#
# def show_pop(pop, snow):
#     cols = 0
#     if snow:
#         color = w
#     else:
#         color = b
#
#     if pop > 0 and pop <= 25:
#         cols = 1
#     elif pop > 25 and pop <= 50:
#         cols = 2
#     elif pop > 50 and pop <= 75:
#         cols = 3
#     elif pop > 75:
#         cols = 4
#     while cols > 0:
#         cols -= 1
#         sense.set_pixel(4+cols,4,color)
#         sense.set_pixel(4+cols,5,color)
#
# def show_his(hi_now, hi_tom):
#     cols = 0
#     if hi_tom > hi_now:
#         color = o
#     else:
#         color = b
#     diff = abs(hi_now - hi_tom)
#     if diff > 0 and diff <= 5:
#         cols = 1
#     elif diff > 5 and diff <= 10:
#         cols = 2
#     elif diff > 10 and diff <= 15:
#         cols = 3
#     elif diff > 15:
#         cols = 4
#     while cols > 0:
#         cols -= 1
#         sense.set_pixel(0+cols,6,color)
#         sense.set_pixel(0+cols,7,color)
#
# def show_curr(temp, temp_yes):
#     cols = 0
#     if temp > temp_yes:
#         color = o
#     else:
#         color = b
#     diff = abs(temp - temp_yes)
#     if diff > 0 and diff <= 5:
#         cols = 1
#     elif diff > 5 and diff <= 10:
#         cols = 2
#     elif diff > 10 and diff <= 15:
#         cols = 3
#     elif diff > 15:
#         cols = 4
#     while cols > 0:
#         cols -= 1
#         sense.set_pixel(0+cols,4,color)
#         sense.set_pixel(0+cols,5,color)

def show_solar_summary(kWh_today, daily_rcd):
    cols = 0
    color = y
    diff = float(kWh_today) / float(daily_rcd) * 100
    if diff > 0 and diff <= 25:
        cols = 1
    elif diff > 25 and diff <= 50:
        cols = 2
    elif diff > 50 and diff <= 75:
        cols = 3
    elif diff > 75:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(4+cols,0,color)
        sense.set_pixel(4+cols,1,color)

def show_solar_month(kWh_month, monthly_rcd):
    cols = 0
    color = y
    diff = float(kWh_month) / float(monthly_rcd) * 100
    if diff > 0 and diff <= 25:
        cols = 1
    elif diff > 25 and diff <= 50:
        cols = 2
    elif diff > 50 and diff <= 75:
        cols = 3
    elif diff > 75:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(4+cols,2,color)
        sense.set_pixel(4+cols,3,color)

# Show default pixel display
def show_blocks(refresh_rate):
    while True:
        if show_blocks:
            sense.clear()
            if bus.updated:
                show_bus(bus.progress_rate)
                print(bus)
                bus.updated = False
            if weather.updated:
                show_uv(weather.uv)
                show_pop(weather.pop, weather.snow)
                show_his(weather.hi_now, weather.hi_tom)
                show_curr(weather.temp, weather.temp_yes)
                print(weather)
                weather.updated = False
            if solar.updated:
                show_solar_summary(solar.kWh_today, solar.daily_rcd)
                show_solar_month(solar.kWh_month, solar.monthly_rcd)
                print(solar)
                solar.updated = False
            sleep(refresh_rate)
        sleep(0.1)

# Tells XModel object to pull fresh data from its API
def x_thread(obj, delay):
    while True:
        obj.update()
        sleep(delay)

def joystick(delay):
    global show_blocks
    while True:
        for event in sense.stick.get_events():
            if event.action == "released" and event.direction == "middle":
                show_blocks = not show_blocks
                if show_blocks:
                    bView.draw()
                else:
                    sense.clear()

try:
    # Services
    thread.start_new_thread( x_thread, (bus, 60*15) )
    thread.start_new_thread( x_thread, (weather, 60*15) )
    thread.start_new_thread( x_thread, (solar, 60*15) )
    sleep(5) # Give some time to pull data before displaying
    # Display
    # thread.start_new_thread( show_blocks, (5,))
    # Listen to the joystick
    thread.start_new_thread( joystick, (0.1,))
except:
    print "Error starting thread."
    traceback.print_exc()

while True:
    bView.refresh()
    # if bus.updated or weather.updated or solar.updated:
    #     # os.system('clear')
    #     print(bus)
    #     print(weather)
    #     print(solar)
    #     print("")
    #
    #     if bus.updated: bus.updated = False
    #     if weather.updated: weather.updated = False
    #     if solar.updated: solar.updated = False

    sleep(2)
