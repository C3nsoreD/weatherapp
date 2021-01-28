from enum import Enum

# Base Enum class should used in other Enum classes 
class BaseEnum(Enum):
    def _generate_next_value_(name, start, count, last_value):
        return name 
