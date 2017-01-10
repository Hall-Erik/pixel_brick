from sense_hat import SenseHat
from time import sleep, strftime, localtime
import json
import requests
import configparser

sense = SenseHat()

config = configparser.ConfigParser()
config.read("config.ini")

testing = False
testing = True

#colours
g = [0,100,0] # Green
b = [0,0,100] # Blue
y = [100,80,0] # Yellow
o = [100,50,0] # Orange
r = [100,0,0] # Red
e = [0,0,0] # Empty
w = [90,90,100]

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

key = config['weather']['wunderground_key']

while True:
    if not testing:
        url = 'http://api.wunderground.com/api/' + key + '/conditions/yesterday/forecast/q/UT/Roy.json'
        parsed_json = requests.get(url).json()
    else:
        with open('api.json') as json_string:
            parsed_json = json.load(json_string)

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

    # Print stuff
    sense.clear()
    print(strftime("%a, %d %b %Y %H:%M:%S +0000", localtime()))
    show_uv(uv)
    show_pop(pop, snow)
    show_his(hi_now, hi_tom)
    show_curr(temp, temp_yes)

    sleep(60 * 15)
