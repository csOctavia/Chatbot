import json
import requests
import datetime
import string

from nltk.tokenize import word_tokenize

class City():
    # class variables, these are not to be accessed directly
    __all = None # all city instances, access with City.all()
    __name_tokens = None # list of lists of word tokens (city names), access with City.name_tokens()
    def __init__(self, name, country, lat, lon):
        self.name = name.lower()
        self.country = country.lower()
        self.lat = lat
        self.lon = lon
        self.__weather = None
        self.all().append(self)
    def __str__(self):
        return self.name.title()
    def __repr__(self):
        return f"City('{self.name}', '{self.country}', '{self.lat}', '{self.lon}')"

    def weather(self):
        """ return all weather json data """
        if self.__weather is None:
            response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={self.lat}&lon={self.lon}&units=metric&appid=97ac59e96a25dd0e59f4d3d453c3b583')
            ... # check response.status_code https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
            self.__weather = response.json()
        return self.__weather

    def daily_weather(self, date):
        """ return current weather ("daily") """
        for day in self.weather()['daily']:
            if datetime.date.fromtimestamp(day['dt']) == date:
                return day
        return None

    def temp(self, date=None):
        """ return temperature for specified date (current temperature if date is None) """
        if date is None:
            return int(round(self.weather()['current']['temp']))
        else:
            dw = self.daily_weather(date)
            if dw is None:
                return None
            return int(round(dw['temp']['day']))

    def feels_like(self, date=None):
        """ return temperature "feels like" for specified date (current feels like if date is None) """
        if date is None:
            return int(round(self.weather()['current']['feels_like']))
        else:
            dw = self.daily_weather(date)
            if dw is None:
                return None
            return int(round(dw['feels_like']['day']))

    def rain(self, date=None):
        """ return rain amount for specified date (current rain if date is None) """
        if date is None:
            if 'rain' in self.weather()['current']:
                return self.weather()['current']['rain']
        else:
            dw = self.daily_weather(date)
            if dw is None:
                return None
            if 'rain' in dw:
                return int(round(dw['rain']))
        return 0

    def wind_speed(self, date=None):
        """ return wind speed for specified date (current wind speed if date is None) """
        if date is None:
            return int(round(self.weather()['current']['wind_speed']))
        else:
            dw = self.daily_weather(date)
            if dw is None:
                return None
            return int(round(dw['wind_speed']))

    @classmethod
    def all(cls):
        """ return all City instances """
        if cls.__all is None:
            cls.read()
        return cls.__all

    @classmethod
    def name_tokens(cls):
        """ return the list of name tokens (as lists) for all City instances """
        if cls.__name_tokens is None:
            cls.read()
        return cls.__name_tokens

    @classmethod
    def read(cls, file_name='city.list.json'):
        """ read the city list """
        ... # check file exists
        with open(file_name) as f:
            cities_json = json.load(f)
        # {'id': 833, 'name': 'Ḩeşār-e Sefīd', 'state': '', 'country': 'IR', 'coord': {'lon': 47.159401, 'lat': 34.330502}}
        cls.__all = []
        cls.__name_tokens = []
        for city in cities_json:
            c = City(city['name'], city['country'], city['coord']['lat'], city['coord']['lon'])
            cls.__name_tokens.append([word for word in word_tokenize(c.name.lower())])

    @classmethod
    def get(cls, name):
        """ get the first city in the list by name """
        for city in cls.all():
            if city.name == name.lower():
                return city
        return None
    @classmethod
    def get_all(cls, name):
        """ get all cities in the list by name """
        for city in cls.all():
            if city.name == name.lower():
                yield city
