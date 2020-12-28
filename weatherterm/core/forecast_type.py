from enum import Enum, unique

@unique
class ForecastType(Enum):
    TODAY = 'today'
    FIVEDAYS = '5days'
    TENDAYS = '10days'
    WEEKEND = 'weekend'

