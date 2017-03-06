from sense_hat import SenseHat
from time import sleep, strftime, localtime
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree
import json
import xmltodict
import requests
import configparser
import datetime

sense = SenseHat()

# For reading config file
config = configparser.ConfigParser()
config.read("config.ini")

# For saving
persist = configparser.ConfigParser()
persist.read("persistence.ini")

# set up wunderground url
w_key = config['weather']['wunderground_key']
w_url = 'http://api.wunderground.com/api/' + w_key + '/conditions/yesterday/forecast/q/UT/Roy.json'

# set up uta url
b_key = config['uta']['uta_key']
b_stop = config['uta']['stop_id']
b_url = 'http://api.rideuta.com/SIRI/SIRI.svc/StopMonitor?stopid=' + b_stop + '&minutesout=' + '90' + '&usertoken=' + b_key

# set up solar urls
todaysDate = datetime.date.today()
month = str(todaysDate.replace(day=1))
s_key = config['solar']['enphase_key']
s_u_id = config['solar']['enphase_user_id']
s_s_id = config['solar']['enphase_system_id']
s_summary_url = 'https://api.enphaseenergy.com/api/v2/systems/' + s_s_id + '/summary?key=' + s_key + '&user_id=' + s_u_id
s_month_url = 'https://api.enphaseenergy.com/api/v2/systems/' + s_s_id + '/energy_lifetime?key=' + s_key + '&user_id=' + s_u_id + '&start_date=' + month

# get solar records
daily_rcd = persist['solar'].getint('daily_rcd', 0)
monthly_rcd = persist['solar'].getint('monthly_rcd', 0)

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
    print("UV: %s" % uv)
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
    print("POP: %s" % pop)
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
    print("hi diff: " + str(hi_tom - hi_now))
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
    elif pop > 15:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(0+cols,6,color)
        sense.set_pixel(0+cols,7,color)

def show_curr(temp, temp_yes):
    print("temp diff: " + str(temp - temp_yes))
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
    elif pop > 15:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(0+cols,4,color)
        sense.set_pixel(0+cols,5,color)

def show_solar_summary(kWh_today, daily_rcd):
    print("energy today: " + str(kWh_today/1000.0) + "kWh")
    cols = 0
    color = y
    diff = float(kWh_today) / float(daily_rcd) * 100
    if diff > 0 and diff <= 25:
        cols = 1
    elif diff > 25 and diff <= 50:
        cols = 2
    elif diff > 50 and diff <= 75:
        cols = 3
    elif pop > 75:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(4+cols,0,color)
        sense.set_pixel(4+cols,1,color)

def show_solar_month(kWh_month, monthly_rcd):
    print("energy this month: " + str(kWh_month/1000.0) + "kWh")
    cols = 0
    color = y
    diff = float(kWh_month) / float(monthly_rcd) * 100
    if diff > 0 and diff <= 25:
        cols = 1
    elif diff > 25 and diff <= 50:
        cols = 2
    elif diff > 50 and diff <= 75:
        cols = 3
    elif pop > 75:
        cols = 4
    while cols > 0:
        cols -= 1
        sense.set_pixel(4+cols,2,color)
        sense.set_pixel(4+cols,3,color)

while True:
    if not testing:
        parsed_json = requests.get(w_url).json()
        solar_summary_json = requests.get(s_summary_url).json()
        solar_month_json = requests.get(s_month_url).json()
        with open('api.xml') as xml_string:
            parsed_xml = xmltodict.parse(xml_string)
    else:
        with open('api.json') as json_string:
            parsed_json = json.load(json_string)
        with open('api.xml') as xml_string:
            parsed_xml = xmltodict.parse(xml_string)

    # UTA
    progress_rate = int(parsed_xml['Siri']['StopMonitoringDelivery']['MonitoredStopVisit']['MonitoredVehicleJourney']['ProgressRate'])

    # Weather
    uv = float(parsed_json['current_observation']['UV'])
    pop = int(parsed_json['forecast']['txt_forecast']['forecastday'][0]['pop'])
    snow = parsed_json['current_observation']['icon'] == 'snow'
    temp = float(parsed_json['current_observation']['temp_f'])
    temp_yes = 0 # Just in case
    for obs in parsed_json['history']['observations']:
        if obs['date']['hour'] == strftime("%H", localtime()):
            temp_yes = float(obs['tempi'])
            break
    hi_now = int(parsed_json['forecast']['simpleforecast']['forecastday'][0]['high']['fahrenheit'])
    hi_tom = int(parsed_json['forecast']['simpleforecast']['forecastday'][1]['high']['fahrenheit'])

    # Solar
    kWh_today = int(solar_summary_json['energy_today'])
    production = solar_month_json['production']
    kWh_month = kWh_today
    for p in production:
        kWh_month += int(p)

    if kWh_today > daily_rcd:
        daily_rcd = kWh_today
        persist['solar']['daily_rcd'] = str(daily_rcd)
    if kWh_month > monthly_rcd:
        monthly_rcd = kWh_month
        persist['solar']['monthly_rcd'] = str(monthly_rcd)

    with open('persistence.ini', 'w') as persistfile:
        persist.write(persistfile)

    # Print stuff
    sense.clear()
    print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    show_bus(progress_rate)
    show_uv(uv)
    show_pop(pop, snow)
    show_his(hi_now, hi_tom)
    show_curr(temp, temp_yes)
    show_solar_summary(kWh_today, daily_rcd)
    show_solar_month(kWh_month, monthly_rcd)

    sleep(60 * 15)
