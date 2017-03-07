import abc # for abstractions
try:
    from xml.etree import cElementTree as ElementTree
except ImportError, e:
    from xml.etree import ElementTree
import xmltodict
import json
import requests
import configparser
import datetime

# For reading config file
config = configparser.ConfigParser()
config.read("config.ini")

# For saving
persist = configparser.ConfigParser()
persist.read("persistence.ini")

class Model(object):
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError('must implement __str__ method to this base class.')

    @abc.abstractmethod
    def hitApi(self):
        raise NotImplementedError('must implement hitApi method to this base class.')

    def update(self):
        if datetime.datetime.now() > self.nextUpdate:
            self.hitApi()

class SolarModel(Model):
    def __init__(self):
        global config
        global persist
        self.s_key = config['solar']['enphase_key']
        self.s_u_id = config['solar']['enphase_user_id']
        self.s_s_id = config['solar']['enphase_system_id']
        self.s_summary_url = 'https://api.enphaseenergy.com/api/v2/systems/' + self.s_s_id + '/summary?key=' + self.s_key + '&user_id=' + self.s_u_id
        # get solar records
        self.daily_rcd = persist['solar'].getint('daily_rcd', 0)
        self.monthly_rcd = persist['solar'].getint('monthly_rcd', 0)
        self.hitApi()

    def __str__(self):
        return "energy today: " + str(self.kWh_today/1000.0) + "kWh\n" + "energy this month: " + str(self.kWh_month/1000.0) + "kWh"

    def hitApi(self):
        global persist
        todaysDate = datetime.date.today()
        month = str(todaysDate.replace(day=1))
        s_month_url = 'https://api.enphaseenergy.com/api/v2/systems/' + self.s_s_id + '/energy_lifetime?key=' + self.s_key + '&user_id=' + self.s_u_id + '&start_date=' + month
        solar_summary_json = requests.get(self.s_summary_url).json()
        solar_month_json = requests.get(s_month_url).json()

        self.kWh_today = int(solar_summary_json['energy_today'])
        production = solar_month_json['production']
        self.kWh_month = self.kWh_today
        for p in production:
            self.kWh_month += int(p)

        if self.kWh_today > self.daily_rcd:
            self.daily_rcd = self.kWh_today
            persist['solar']['daily_rcd'] = str(self.daily_rcd)
        if self.kWh_month > self.monthly_rcd:
            self.monthly_rcd = self.kWh_month
            persist['solar']['monthly_rcd'] = str(self.monthly_rcd)

        with open('persistence.ini', 'w') as persistfile:
            persist.write(persistfile)

        self.nextUpdate = datetime.datetime.now() + datetime.timedelta(minutes=15)
