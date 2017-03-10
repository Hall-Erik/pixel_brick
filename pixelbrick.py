from sense_hat import SenseHat
from time import sleep, strftime, localtime
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree
import xmltodict
import configparser
import model
import requests

sense = SenseHat()

# For reading config file
config = configparser.ConfigParser()
config.read("config.ini")

# Initialize Weather model
weather = model.WeatherModel()

# set up uta url
b_key = config['uta']['uta_key']
b_stop = config['uta']['stop_id']
b_url = 'http://api.rideuta.com/SIRI/SIRI.svc/StopMonitor?stopid=' + b_stop + '&minutesout=' + '90' + '&usertoken=' + b_key

# Initialize Solar model
solar = model.SolarModel()

testing = False
# testing = True

#colours
g = [0,100,0] # Green
b = [0,0,100] # Blue
y = [100,80,0] # Yellow
o = [100,50,0] # Orange
r = [100,0,0] # Red
e = [0,0,0] # Empty
w = [90,90,100]

def show_bus(progress_rate):
    print("Progress: %s" % progress_rate)
    if progress_rate == 1: # On time
        color = g
        rows = 4
    elif progress_rate == 0: # 5-10 min early
        color = b
        rows = 2
    elif progress_rate == 4: # 10+ min early
        color = b
        rows = 4
    elif progress_rate == 2: # 5-10 min late
        color = r
        rows = 2
    elif progress_rate == 3: # 10+ min late
        color = r
        rows = 4
    else:
        rows = 0
    while rows > 0:
        rows -= 1
        for x in range(4):
            sense.set_pixel(x, rows, color)

def show_uv(uv):
    # print("UV: %s" % uv)
    cols = 0
    color = g
    if uv > 0 and uv <= 3:
        color = g
        cols = 1
    elif uv > 3 and uv <= 6:
        color = y
        cols = 2
    elif uv > 6 and uv <= 8:
        color = o
        cols = 3
    elif uv > 8:
        color = r
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(4+cols,6,color)
        sense.set_pixel(4+cols,7,color)

def show_pop(pop, snow):
    # print("POP: %s" % pop)
    cols = 0
    if snow:
        color = w
    else:
        color = b

    if pop > 0 and pop <= 25:
        cols = 1
    elif pop > 25 and pop <= 50:
        cols = 2
    elif pop > 50 and pop <= 75:
        cols = 3
    elif pop > 75:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(4+cols,4,color)
        sense.set_pixel(4+cols,5,color)

def show_his(hi_now, hi_tom):
    # print("hi diff: " + str(hi_tom - hi_now))
    cols = 0
    if hi_tom > hi_now:
        color = o
    else:
        color = b
    diff = abs(hi_now - hi_tom)
    if diff > 0 and diff <= 5:
        cols = 1
    elif diff > 5 and diff <= 10:
        cols = 2
    elif diff > 10 and diff <= 15:
        cols = 3
    elif diff > 15:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(0+cols,6,color)
        sense.set_pixel(0+cols,7,color)

def show_curr(temp, temp_yes):
    # print("temp diff: " + str(temp - temp_yes))
    cols = 0
    if temp > temp_yes:
        color = o
    else:
        color = b
    diff = abs(temp - temp_yes)
    if diff > 0 and diff <= 5:
        cols = 1
    elif diff > 5 and diff <= 10:
        cols = 2
    elif diff > 10 and diff <= 15:
        cols = 3
    elif diff > 15:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(0+cols,4,color)
        sense.set_pixel(0+cols,5,color)

def show_solar_summary(kWh_today, daily_rcd):
    # print("energy today: " + str(kWh_today/1000.0) + "kWh")
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
    # print("energy this month: " + str(kWh_month/1000.0) + "kWh")
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

while True:
    if not testing:
        solar.update()
        weather.update()
        parsed_xml = xmltodict.parse(requests.get(b_url).text)
        # with open('api.xml') as xml_string:
        #     parsed_xml = xmltodict.parse(xml_string)
    else:
        with open('api.xml') as xml_string:
            parsed_xml = xmltodict.parse(xml_string)

    # UTA
    print(parsed_xml['Siri']['StopMonitoringDelivery']['MonitoredStopVisit'])
    if 'MonitoredVehicleJourney' in parsed_xml['Siri']['StopMonitoringDelivery']['MonitoredStopVisit'].keys():
        progress_rate = int(parsed_xml['Siri']['StopMonitoringDelivery']['MonitoredStopVisit']['MonitoredVehicleJourney']['ProgressRate'])
    else:
        progress_rate = -1

    # Print stuff
    sense.clear()
    print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    show_bus(progress_rate)
    show_uv(weather.uv)
    show_pop(weather.pop, weather.snow)
    show_his(weather.hi_now, weather.hi_tom)
    show_curr(weather.temp, weather.temp_yes)
    show_solar_summary(solar.kWh_today, solar.daily_rcd)
    show_solar_month(solar.kWh_month, solar.monthly_rcd)
    print(weather)
    print(solar)

    sleep(60 * 15)
