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

# Initialize the view
# bView is the main view that shows info as blocks
bView = view.BlockView(bus,weather,solar)

#If true show default pixel display
show_blocks = True

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
    sleep(2) # Give some time to pull data before displaying
    # Listen to the joystick
    thread.start_new_thread( joystick, (0.1,))
except:
    print "Error starting thread."
    traceback.print_exc()

while True:
    bView.refresh()
    if bus.updated or weather.updated or solar.updated:
        os.system('clear')
        print(bus)
        print(weather)
        print(solar)
        print("")
    
        if bus.updated: bus.updated = False
        if weather.updated: weather.updated = False
        if solar.updated: solar.updated = False

    sleep(2)
