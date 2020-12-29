import re 

from bs4 import BeautifulSoup

from weatherterm.core import ForecastType
from weatherterm.core import Forecast
from weatherterm.core import Unit 
from weatherterm.core import UnitConverter
from weatherterm.core import Request


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
        raise NotImplementedError()

    def _five_and_ten_days_forecast(self, args):
        raise NotImplementedError()

    def _weekend_forecast(self, args):
        raise NotImplementedError()
    
    def run(self, args):
        self._forecast_type = args.forecast_option
        forecast_function = self._forecast[args.forecast_option]
        return forecast_function(args)
