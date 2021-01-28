from enum import auto, unique

from .base_enum import BaseEnum

@unique
class Unit(BaseEnum):
    # auto allows the values for each enum to be set automatically
    CELSIUS = auto()
    FAHRENHEIT = auto()
    
