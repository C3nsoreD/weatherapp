import os 
import re
import inspect 

"""
Parsers loader
Dynamically discovers files inside the parsers directory 
Rules: 
    - creates a file with a class implementing the methods for fetching weather data
    - the file name has to end with parser, 
    - the file name mus not start with __
"""

def _get_parser_list(dirname):
    """
    Returns a list of all fills in `weatherterm/parsers` based on
    the rules.
    """
    files = [
        f.replace('.py', '') 
        for f in os.listdir(dirname) 
        if not f.startswith('__')
    ]
    return files 


def _import_parsers(parserfiles):
    m = re.compile('.+parser$', re.I)
    _modules = __import__(
        'weatherterm.parsers',
        globals(),
        locals(),
        parserfiles,
        0)

    _parsers = [
        (k, v) for k, v in inspect.getmembers(_modules)
        if inspect.ismodule(v) and m.match(k)
    ]

    _classes = dict()
    for k, v in _parsers:
        _classes.update(
            {k: v for k, v in inspect.getmembers(v)
            if inspect.isclass(v) and m.match(k)}
        )
    return _classes


def load(dirname):
    # Entry point of parser_loader
    parserfiles = _get_parser_list(dirname)
    return _import_parsers(parserfiles)