"""Logging and Profiling

Mostly copied and adapted from https://github.com/theislab/scanpy/
"""

import time as time_module
import datetime
import psutil
import os
import logging

from colorama import Fore, Style

from pypairs import settings

_previous_memory_usage = -1

logger = logging.getLogger('pypairs')
logger.propagate = False  # Don’t pass log messages on to logging.root and its handler
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())  # Logs go to stderr
logger.handlers[-1].setFormatter(logging.Formatter('%(message)s'))
logger.handlers[-1].setLevel('INFO')

def get_logger(name):
    """Creates a child logger that delegates to pypairs_logger instead to logging.root"""
    return logger.manager.getLogger(name)


_VERBOSITY_LEVELS_FROM_STRINGS = {
    'error': 0,
    'warn': 1,
    'info': 2,
    'hint': 3,
}

def get_time_formatted():
    return time_module.strftime("%H:%M:%S", time_module.gmtime())


def info(*args, **kwargs):
    s = "{} [{}{}{}]".format(get_time_formatted(), Fore.GREEN, 'INFO', Style.RESET_ALL)
    args = (s, ) + args
    return msg(*args, v='info', **kwargs)


def error(*args, **kwargs):
    s = "{} [{}{}{}]".format(get_time_formatted(), Fore.RED, 'ERR ', Style.RESET_ALL)
    args = (s,) + args
    return msg(*args, v='error', **kwargs)


def warn(*args, **kwargs):
    s = "{} [{}{}{}]".format(get_time_formatted(), Fore.YELLOW, 'WARN', Style.RESET_ALL)
    args = (s,) + args
    return msg(*args, v='warn', **kwargs)


def hint(*args, **kwargs):
    s = "{} [{}{}{}]".format(get_time_formatted(), Fore.BLUE, 'HINT', Style.RESET_ALL)
    args = (s,) + args
    return msg(*args, v='hint', **kwargs)


def _settings_verbosity_greater_or_equal_than(v):
    if isinstance(settings.verbosity, str):
        settings_v = _VERBOSITY_LEVELS_FROM_STRINGS[settings.verbosity]
    else:
        settings_v = settings.verbosity
    return settings_v >= v


def msg(*msg, v=4, time=False, memory=False, reset=False, end='\n',
        t=None, m=None, r=None):
    """Write message to logging output.
    Log output defaults to standard output but can be set to a file
    by setting `sc.settings.log_file = 'mylogfile.txt'`.
    v : {'error', 'warn', 'info', 'hint'} or int, (default: 4)
        0/'error', 1/'warn', 2/'info', 3/'hint', 4, 5, 6...
    time, t : bool, optional (default: False)
        Print timing information; restart the clock.
    memory, m : bool, optional (default: Faulse)
        Print memory information.
    reset, r : bool, optional (default: False)
        Reset timing and memory measurement. Is automatically reset
        when passing one of ``time`` or ``memory``.
    end : str (default: '\n')
        Same meaning as in builtin ``print()`` function.
    no_indent : bool (default: False)
        Do not indent for ``v >= 4``.
    """
    # variable shortcuts
    if t is not None: time = t
    if m is not None: memory = m
    if r is not None: reset = r
    if isinstance(v, str):
        v = _VERBOSITY_LEVELS_FROM_STRINGS[v]
    #if v == 3:  # insert "--> " before hints
    #    msg = ('-->',) + msg
    #if v >= 4 and not no_indent:
    #    msg = ('   ',) + msg
    if _settings_verbosity_greater_or_equal_than(v):
        if not time and not memory and len(msg) > 0:
            _write_log(*msg, end=end)
        if reset:
            try:
                settings._previous_memory_usage, _ = get_memory_usage()
            except:
                pass
            settings._previous_time = time_module.time()
        if time:
            elapsed = get_passed_time()
            msg = msg + ('({})'.format(_sec_to_str(elapsed)),)
            _write_log(*msg, end=end)
        if memory:
            _write_log(format_memory_usage(get_memory_usage()),
                        msg='' if time else msg, end=end)

m = msg  # backwards compat


def _write_log(*msg, end='\n'):
    """Write message to log output, ignoring the verbosity level.
    This is the most basic function.
    Parameters
    ----------
    *msg :
        One or more arguments to be formatted as string. Same behavior as print
        function.
    """
    from pypairs.settings import logfile
    if logfile == '':
        print(*msg, end=end)
    else:
        out = ''
        for s in msg:
            out += str(s) + ' '
        with open(logfile, 'a') as f:
            f.write(out + end)


def _sec_to_str(t):
    """Format time in seconds.
    Parameters
    ----------
    t : int
        Time in seconds.
    """
    from functools import reduce
    return "%d:%02d:%02d.%02d" % \
        reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
               [(t*100,), 100, 60, 60])


def get_passed_time():
    now = time_module.time()
    elapsed = now - settings._previous_time
    settings._previous_time = now
    return elapsed


def print_version_and_date():
    from . import __version__
    _write_log('Running Scanpy', __version__, 'on {}.'.format(get_date_string()))


_DEPENDENCIES_NUMERICS = [
    'anndata',
    'numpy',
    'pandas',
    'numba',
]

_DEPENDENCIES_PLOTTING = ['matplotlib', 'seaborn']


def _print_versions_dependencies(dependencies):
    # this is not the same as the requirements!
    for mod in dependencies:
        mod_name = mod[0] if isinstance(mod, tuple) else mod
        mod_install = mod[1] if isinstance(mod, tuple) else mod
        try:
            imp = __import__(mod_name)
            print('{}=={}'.format(mod_install, imp.__version__), end=' ')
        except (ImportError, AttributeError):
            pass
    print()


def print_versions():
    """Versions that might influence the numerical results.
    Matplotlib and Seaborn are excluded from this.
    """
    _print_versions_dependencies(['pypairs'] + _DEPENDENCIES_NUMERICS)


def print_versions_dependencies_numerics():
    """Dependencies that might influence numerical results (computed data).
    """
    print('Dependencies:', end=' ')
    _print_versions_dependencies(_DEPENDENCIES_NUMERICS)


def print_versions_dependencies_plotting():
    """Dependencies that might influence plots (but not computed data).
    """
    print('Dependencies:', end=' ')
    _print_versions_dependencies(_DEPENDENCIES_PLOTTING)


def print_versions_dependencies_all():
    """All relevant dependencies.
    """
    _print_versions_dependencies(
        _DEPENDENCIES_NUMERICS + _DEPENDENCIES_PLOTTING)


def get_date_string():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def get_memory_usage():
    process = psutil.Process(os.getpid())
    meminfo_attr = ('memory_info' if hasattr(process, 'memory_info')
                    else 'get_memory_info')
    mem = getattr(process, meminfo_attr)()[0] / 2**30  # output in GB
    mem_diff = mem
    global _previous_memory_usage
    if _previous_memory_usage != -1:
        mem_diff = mem - _previous_memory_usage
    _previous_memory_usage = mem
    return mem, mem_diff


def format_memory_usage(mem_usage, msg='', newline=False):
    mem, diff = mem_usage
    string = (('\n' if newline else '')
              + msg + (' \n... ' if msg != '' else '')
              + 'Memory usage: current {:.2f} GB, difference {:+.2f} GB'
              .format(mem, diff))
    return string


def print_memory_usage(msg='', newline=False):
    string = format_memory_usage(get_memory_usage(), msg, newline)
    print(string)
