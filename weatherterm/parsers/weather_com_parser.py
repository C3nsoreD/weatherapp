import re 

from bs4 import BeautifulSoup

from weatherterm.core import ForecastType
from weatherterm.core import Forecast
from weatherterm.core import Unit 
from weatherterm.core import UnitConverter
from weatherterm.core import Request
from weatherterm.core import Mapper


class WeatherComParser:
    def __init__(self):
        self._forecast = {
            ForecastType.TODAY: self._today_forecast,
            ForecastType.FIVEDAYS: self._five_and_ten_days_forecast,
            ForecastType.TENDAYS: self._five_and_ten_days_forecast,
            ForecastType.WEEKEND: self._weekend_forecast,
        }
        self._base_url = 'https://weather.com/weather/{forecast}}/l{area}'
        self._request = Request(self._base_url)

        self._temp_regex = re.compile('([0-9]+)\D{,2} ([0-9]+)')
        self._only_digits_regex =re.compile('[0-9]+')

        self._unit_converter = UnitConverter(Unit.FAHRENHEIT)
    
    def _get_data(self, container, search_items):
        """
        Searches items within a container that matches given criteria 
    
        Container: DOM element
        criteria: a dict of codes we want
        """
        scraped_data = {}
        
        for key, value in search_items.items():
            result = container.find(value, class_=key)
            data = None if result is None else result.get_text()
            if data is not None:
                scraped_data[key] = data
            
        return scraped_data

    def _parse(self, container, criteria):
        """
        Return a list of non empty dictionaries containing text from HTML elements that meet the criteria.
        
        Container: DOM element
        criteria: a dict of codes we want
        """
        results = [
            self._get_data(item, criteria) for item in container.children
            ]
        
        return [result for result in results if result]

    def _clear_str_number(self, str_number):
        # Using regex expressions to make sure digits are returned
        result = self._only_digits_regex.match(str_number)
        return '--' if result is None else result.group()

    def _get_additional_info(self, content):
        # Returns a list of weather info,
        # Only interested in the first 2 wind, humidity
        # optional: return data[:]
        data = tuple(
            item.id.span.get_text() for item in content.table.tbody.children
        )
        return data[:2]

    def _today_forecast(self, args):
        criteria = {
            'today_nowcard-temp': 'div',
            'today_nowcard-phrase': 'div',
            'today_nowcard-hilo': 'div',
        }
        content = self._request.fetch_data(args.forecast_option.value, args.area_code)
        
        ## BS returns an html file
        bs = BeautifulSoup(content, 'html.parser')

        container = bs.find('section', class_='today_nowcard-container')

        weather_conditions = self._parse(container, criteria)

        if len(weather_conditions) < 1:
            raise Exception('Could not parse weather forecast for today')
        
        weatherinfo = weather_conditions[0]
    
        ## The regex explained: 
        # Look for `H` followed by some spaces, and then a grouped value which is either a number
        # or a maximum of two dash symbols
        temp_regex = re.compile(
            ('H\s+(\d+|\-{,2}).+', 'L\s+(\d+|\-{,2}).+')
        )
        temp_info = temp_regex.search(weatherinfo['today_nowcard-hilo'])
        high_temp, low_temp = temp_info.groups()        
        
        side = container.find('div', class_='today_nowcard-sidecar')
        wind, humidity = self._get_additional_info(side)

        curr_temp = self._clear_str_number(weatherinfo['today_nowcard-temp'])

        self._unit_converter.dest_unit = args.unit

        td_forecast = Forecast(
            self._unit_converter.convert(curr_temp), 
            humidity, 
            wind, 
            high_temp = self._unit_converter.convert(high_temp),
            low_temp = self._unit_converter.convert(low_temp),
            description = weatherinfo['today_nowcard-phrase']
        )
        return [td_forecast]


    def _five_and_ten_days_forecast(self, args):
        content = self._request.fetch_data(args.forecast_option.value, args.area_code)
        results = self._parse_list_forecast(content, args)
        
        return self._prepare_date(results)
        
    # Weekend data will be different from today, 5days, 10days
    # Thus a mapper was built to replace/change the css names 
    # so that our _parse can work the same way
    
    def _weekend_forecast(self, args):
        criteria - {
            'weather-ceil': 'header',
            'temp':'p',
            'weather-phrase': 'h3',
            'wind-conditions': 'p',
            'humidity': 'p',
        }
        
        mapper = Mapper()
        mapper.remap_key('wind-conditions', 'wind')
        mapper.remap_key('weather-phrase', 'description')
        
        content = self._request.fetch_data(args.forecast_option.value, args.area_code)
         
        bs = BeautifulSoup(content, 'html.parser')
        
        forecast_data = bs.find('article', class_='ls-mod')
        container = forecast_data.div.div

        partial_results = self._parse(container, criteria)
        results = mapper.remap(partial_results)

        return self._prepare_data(results, args)



    def _parse_list_forecast(self, content, args):
        criteria = {
            'date-time': 'span',
            'day-detail': 'span',
            'description': 'td',
            'temp': 'td',
            'wind': 'td',
            'humidity': 'td',
        }
        bs = BeautifulSoup(content, 'html.parser')

        forecast_data = bs.find('table', class_='twc-table')
        container = forecast_data.tbody
        
        return self._parse(container, criteria)

    def _prepare_data(self, results, args):
        forecast_result = []

        self._unit_converter.dest_unit = args.unit

        for item in results:
            match = self._temp_regex.search(item['temp'])
            if match is not None:
                high_temp, low_temp = match.groups()

            try:
                dateinfo = item['weather-ceil']
                date_time, day_detail = dateinfo[:3], dateinfo[3:]
                item['date-time'] = date_time
                item['day-detail'] = day_detail
            except KeyError:
                pass 

            day_forecast = Forecast(    
                self._unit_converter.convert(item['temp']), 
                item['humidity'], 
                item['wind'], 
                high_temp = self._unit_converter.convert(high_temp),
                low_temp = self._unit_converter.convert(low_temp),
                description = item['description'].strip(),
                forecast_date=f'{item["date-time"]} {item["day-detail"]}',
                forecast_type=self._forecast_type
            )
            forecast_result.append(day_forecast)

        return forecast_result            
    
    
    def run(self, args):
        self._forecast_type = args.forecast_option
        forecast_function = self._forecast[args.forecast_option]
        return forecast_function(args)
