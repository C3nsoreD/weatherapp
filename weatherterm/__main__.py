import sys
from argparse import ArgumentParser 

from weatherterm.core import parser_loader
from weatherterm.core import ForecastType
from weatherterm.core import Unit
from weatherterm.core import SetUnitAction

def _validate_forecast_args(args):
    if args.forecast_option is None:
        err_msg = ('one of these arguments must be used: '
                    'td/--today, -5d/--fivedays, -10d/--tendays, -w/--weekend')
        print(f'{argparser.prog}: error: {err_msg}', file=sys.stderr)
        sys.exit()
    
parser = parser_loader('./weatherterm/parsers')

argparser = ArgumentParser(
    prog='weatherterm',
    description='Weather info from weather.com on your terminal'
)

required = argparser.add_argument_group('required arguments')

required.add_argument(
    '-p', 
    '--parser', 
    choices=parsers.keys(), 
    required=True,
    dest='parser',
    help=('Specify which parser is going to be used to scrape weather information')
)

unit_values = [name.title() for name, value in Unit.__members__.items()]

argparser.add_argument(
    '-u', 
    '--Unit',
    choices=unit_values,
    required=False,
    dest='unit',
    action=SetUnitAction
    help=('Specify the unit that will be used to display the temperature')
)

argparser.add_argument(
    '-a', 
    '--areacode',
    required=False,
    dest='area_code',
    help=('The code to get the weather broadcast from. Obtained at https://weather.com')
)

argparser.add_argument(
    '-v', 
    '--version',
    action='version',
    version='%(prog)s 1.0'
)

argparser.add_argument(
    '-td', 
    '--today',
    dest='forecast_option',
    action='store_const',
    const=ForecastType.TODAY,
    help='Show the current weather forecast for today'
)

args = argparser.parse_args()

_validate_forecast_args(args)

cls = parsers[args.parser]

parser = cls()
results = parser.run(args)

for result in results:
    print(results)
