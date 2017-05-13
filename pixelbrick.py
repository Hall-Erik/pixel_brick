# from sense_hat import SenseHat
from nonsensehat import NonsenseHat
from time import sleep, strftime, localtime
import model
import view
import thread
import os
import traceback
import datetime

# sense = SenseHat()
sense = NonsenseHat()

# Initialize models
weather = model.WeatherModel()
bus = model.BusModel()
solar = model.SolarModel()

# Initialize the view
bView = view.BlockView(sense,bus,weather,solar) # main view that shows info as blocks
sView = view.SolarView(sense,solar) # print out solar production
wView = view.WeatherView(sense,weather)
tView = view.TransitView(sense,bus)

#If true show default pixel display
show_blocks = True

view_modes = ['main','solar','weather','bus']
view_mode = 0

# Tells XModel object to pull fresh data from its API
def x_thread(obj, delay):
    while True:
        obj.update()
        sleep(delay)

def joystick(delay):
    global show_blocks, view_mode
    while True:
        for event in sense.stick.get_events():
            if event.action == "released":
                if view_modes[view_mode] != "main":
                    sense.interrupt = True
                if event.direction == "middle":
                    show_blocks = not show_blocks
                    if not show_blocks:
                        bView.clear()
                elif event.direction == "right":
                    sense.clear()
                    view_mode = (view_mode+1)%len(view_modes)
                elif event.direction == "left":
                    sense.clear()
                    view_mode = (view_mode-1)%len(view_modes)
                elif event.direction == "down":
                    sense.clear()
                    view_mode = 0
                elif event.direction == "up":
                    pass # some kind of settings should go here.
                if view_modes[view_mode] != "main":
                    show_blocks = True

try:
    # Services
    thread.start_new_thread( x_thread, (bus, 60*15) )
    thread.start_new_thread( x_thread, (weather, 60*15) )
    thread.start_new_thread( x_thread, (solar, 60*15) )
    sleep(2) # Give some time to pull data before displaying
    # Listen to the joystick
    thread.start_new_thread( joystick, (0.1,))
except:
    print "Error starting thread."
    traceback.print_exc()

while True:
    if view_modes[view_mode] == "main" and show_blocks:
        bView.refresh()
    elif view_modes[view_mode] == "solar":
        sView.refresh()
    elif view_modes[view_mode] == "weather":
        wView.refresh()
    elif view_modes[view_mode] == "bus":
        tView.refresh()

    if bus.updated or weather.updated or solar.updated:
        os.system('clear')
        print(bus)
        print(weather)
        print(solar)
        print("")

        if bus.updated: bus.updated = False
        if weather.updated: weather.updated = False
        if solar.updated: solar.updated = False

    sleep(0.1)
