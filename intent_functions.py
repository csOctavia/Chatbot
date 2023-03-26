import datetime

from city import City

def general_query(query):
    query.require(1)
    if len(query.dates) == 1: # use the same date for all cities
        dates_gen = (date for date in query.dates*len(query.cities))
    else: # different dates for different cities
        dates_gen = (date for date in query.dates)
    for city in query.cities:
        date = next(dates_gen, None)
        if date is None or date==datetime.date.today(): # current weather
            print(f'The temperature in {city} is {city.temp()} °C. It feels like {city.feels_like()} °C.')
            rain = city.rain()
            if rain:
                print(f'The rain forecast is {rain} mm.')
            else:
                print(f'No rain is planned for today :)')
            print(f'The wind moves at {city.wind_speed()} km/h.')
        else: # forecasted weather
            print(f'On {date}, the temperature in {city} is {city.temp(date)} °C. It feels like {city.feels_like(date)} °C.')
            rain = city.rain(date)
            if rain:
                print(f'The rain forecast is {rain} mm.')
            else:
                print(f'No rain is planned for {date} :)')
            print(f'The wind moves at {city.wind_speed()} km/h.')
    query.update_prev()

def temp_query(query):
    query.require(1)
    if len(query.dates) == 1:
        dates_gen = (date for date in query.dates*len(query.cities))
    else:
        dates_gen = (date for date in query.dates)
    for city in query.cities:
        date = next(dates_gen, None)
        if date is None or date==datetime.date.today():
            print(f'The temperature in {city} is {city.temp()} °C. It feels like {city.feels_like()} °C.')
        else:
            print(f'On {date}, the temperature in {city} is {city.temp(date)} °C. It feels like {city.feels_like(date)} °C.')
    query.update_prev()

def temp_compare(query):
    query.require(2)
    dates = query.dates
    if len(query.dates) == 0:
        for city in query.cities:
            print(f'The temperature in {city} is {city.temp()} °C. It feels like {city.feels_like()} °C.')
    else:
        if len(query.cities) != len(query.dates):
            dates = [query.dates[-1]] * len(query.cities)
        for city, date in zip(query.cities, dates):
            print(f'On {date}, the temperature in {city} is {city.temp(date)} °C. It feels like {city.feels_like(date)} °C.')

    print(comparison(query.cities, dates, 'cold', 'colder', City.temp))
    query.update_prev()

def rain_query(query):
    query.require(1)
    if len(query.dates) == 1:
        dates_gen = (date for date in query.dates*len(query.cities))
    else:
        dates_gen = (date for date in query.dates)
    for city in query.cities:
        date = next(dates_gen, None)
        if date is None or date==datetime.date.today():
            rain = city.rain()
            if rain:
                print(f'The rain forecast in {city} is {rain} mm.')
            else:
                print(f'No rain today in {city} :)')
        else:
            rain = city.rain(date)
            if rain:
                print(f'The rain forecast for {date} in {city} is {rain} mm.')
            else:
                print(f'No rain on {date} in {city} :)')
    query.update_prev()

def rain_compare(query):
    query.require(2)
    dates = query.dates
    if len(query.dates) == 0:
        for city in query.cities:
            rain = city.rain()
            if rain:
                print(f'The rain forecast in {city} is {rain} mm.')
            else:
                print(f'No rain today in {city} :)')
    else:
        if len(query.cities) != len(query.dates):
            dates = [query.dates[-1]] * len(query.cities)
        for city, date in zip(query.cities, dates):
            rain = city.rain(date)
            if rain:
                print(f'The rain forecast for {date} in {city} is {rain} mm.')
            else:
                print(f'No rain on {date} in {city} :)')
    print(comparison(query.cities, dates, 'rainy', 'rainier', City.rain, reverse=True))
    query.update_prev()

def wind_query(query):
    query.require(1)
    if len(query.dates) == 1:
        dates_gen = (date for date in query.dates*len(query.cities))
    else:
        dates_gen = (date for date in query.dates)
    for city in query.cities:
        date = next(dates_gen, None)
        if date is None or date==datetime.date.today():
            print(f'The wind moves at {city.wind_speed()} km/h in {city}.')
        else:
            print(f'On {date}, the wind moves at {city.wind_speed(date)} km/h in {city}.')
    query.update_prev()

def wind_compare(query):
    query.require(2)
    dates = query.dates
    if len(query.dates) == 0:
        for city in query.cities:
            print(f'The wind moves at {city.wind_speed()} km/h in {city}.')
    else:
        if len(query.cities) != len(query.dates):
            dates = [query.dates[-1]] * len(query.cities)
        for city, date in zip(query.cities, dates):
            print(f'On {date}, the wind moves at {city.wind_speed(date)} km/h in {city}.')

    print(comparison(query.cities, dates, 'windy', 'windier', City.wind_speed, reverse=True))
    query.update_prev()

#### UTILITY FUNCTIONS
def name_join(names):
    """ create a nice natural language list from the names """
    if len(names) == 1:
        return names[0]
    else:
        return ', '.join(names[:-1]) + f' and {names[-1]}'
def is_are(counter, str1, str2):
    """ join the 2 strings with "is" or "are" """
    return f'{str1} {"is" if counter==1 else "are"} {str2}'
def comparison(cities, dates, adj, super, key, reverse=False):
    """ sort the cities and dates by key, then return a string showing which one is on top. example call: comparison(query.cities, dates, 'cold', 'colder', City.temp)) """
    if len(dates)==0: # don't use any dates in the comparison (today will be the default)
        sorted_cities = sorted(cities, key=key, reverse=reverse)
        if len(sorted_cities) == 2: # two cities
            if key(sorted_cities[0]) == key(sorted_cities[1]):
                return f'{sorted_cities[0]} is as {adj} as {sorted_cities[1]}'
            else:
                return f'{sorted_cities[0]} is {super} than {sorted_cities[1]}'
        else: # multiple cities
            min_count = len([key(city) for city in sorted_cities if key(city)==key(sorted_cities[0])])
            min_str = name_join([f'{city}' for city in sorted_cities[:min_count]])
            max_str = name_join([f'{city}' for city in sorted_cities[min_count:]])
            return is_are(min_count, min_str, f'{super} than {max_str}')
    else: # also use the dates
        cities_dates = zip(cities, dates)
        sorted_cities_dates = sorted(cities_dates, key=lambda cd: key(cd[0], cd[1]), reverse=reverse)
        if len(sorted_cities_dates) == 2: # two cities
            if key(sorted_cities_dates[0][0], sorted_cities_dates[0][1]) == key(sorted_cities_dates[1][0], sorted_cities_dates[1][1]):
                return f'{sorted_cities_dates[0][0]} is as {adj} on {sorted_cities_dates[0][1]} as {sorted_cities_dates[1][0]} on {sorted_cities_dates[1][1]}'
            else:
                return f'{sorted_cities_dates[0][0]} is {super} on {sorted_cities_dates[0][1]} than {sorted_cities_dates[1][0]} on {sorted_cities_dates[1][1]}'
        else: # multiple cities
            min_count = len([key(city, date) for city, date in sorted_cities_dates if key(city, date)==key(sorted_cities_dates[0][0], sorted_cities_dates[0][1])])
            min_str = name_join([f'{city} on {date}' for city, date in sorted_cities_dates[:min_count]])
            max_str = name_join([f'{city} on {date}' for city, date in sorted_cities_dates[min_count:]])
            return is_are(min_count, min_str, f'{super} than {max_str}')
