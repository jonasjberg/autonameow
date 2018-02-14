# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time
from contextlib import contextmanager
from functools import wraps

from core import view


LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# TODO: Fix global logging state making testing tedious.
_logging_initialized = False


def init_logging(opts):
    """
    Configures the global log format and settings.

    Args:
        opts: Per-instance program options, as type dict.
    """
    global _logging_initialized
    # assert not _logging_initialized
    if _logging_initialized:
        # TODO: Fix global logging state making testing tedious.
        return

    # NOTE(jonas): This is probably a bad idea, but seems to work good enough.
    # TODO: [hardcoded] Remove spaces after labels, used for alignment.
    logging.addLevelName(logging.INFO, view.colorize(
        '[INFO]    ', fore='LIGHTBLUE_EX', style='BRIGHT'
    ))
    logging.addLevelName(logging.DEBUG, view.colorize(
        '[DEBUG]   ', fore='BLUE'
    ))
    logging.addLevelName(logging.WARNING, view.colorize(
        '[WARNING] ', fore='RED', style='BRIGHT'
    ))
    logging.addLevelName(logging.ERROR, view.colorize(
        '[ERROR]   ', fore='RED', style='BRIGHT'
    ))
    logging.addLevelName(logging.CRITICAL, view.colorize(
        '[CRITICAL]', fore='LIGHTRED_EX', style='BRIGHT'
    ))

    # Setup logging output format.
    # TODO: Make logging verbosity more controllable with additional logging
    #       levels, enabled by adding on any number of '-v' options to the
    #       command-line. For instance, verbosity levels 1 and 3 would be
    #       enabled with '-v' and '-vvv', respectively.

    _colored_timestamp = view.colorize('%(asctime)s', style='DIM')
    if opts.get('debug'):
        fmt = (
            _colored_timestamp
            + ' %(levelname)s %(name)-25.25s %(funcName)-20.20s  %(message)s'
        )
        logging.basicConfig(level=logging.DEBUG, format=fmt,
                            datefmt=LOG_DATE_FORMAT)
    elif opts.get('verbose'):
        fmt = _colored_timestamp + ' %(levelname)s %(message)s'
        logging.basicConfig(level=logging.INFO, format=fmt,
                            datefmt=LOG_DATE_FORMAT)
    elif opts.get('quiet'):
        fmt = '%(levelname)s %(message)s'
        logging.basicConfig(level=logging.CRITICAL, format=fmt)
    else:
        fmt = '%(levelname)s %(message)s'
        logging.basicConfig(level=logging.WARNING, format=fmt)

    _logging_initialized = True


def deinit_logging():
    """
    Attempt to reset logging to an initial state.
    Used by unit tests to clean up after themselves.
    """
    # This seems to be enough to solve the problems at hand.
    if logging.root:
        del logging.root.handlers[:]

    # Additional methods for reloading the module, currently not required.
    # import importlib
    # logging.shutdown()
    # importlib.reload(logging)

    global _logging_initialized
    _logging_initialized = False


def silence():
    logging.disable(logging.DEBUG)
    logging.disable(logging.INFO)
    logging.disable(logging.WARNING)
    logging.disable(logging.CRITICAL)
    logging.disabled = True


def unsilence():
    logging.disabled = False


@contextmanager
def log_runtime(logger, name):
    def _log(message):
        MAX_WIDTH = 120
        message = ' ' + message + ' '
        logger.debug(message.center(MAX_WIDTH, '='))

    _log('{} Started'.format(name))
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        _log('{} Completed in {:.9f} seconds'.format(name, elapsed_time))


def log_func_runtime(logger):
    """
    Logs execution time of a method or function to the given logger.

    Example usage:

        my_log = logging.getLogger(__name__)

        @log_func_runtime(my_log)
        def foo():
            pass

    """
    def decorator(func):
        if not __debug__:
            return func

        @wraps(func)
        def log_runtime_wrapper(*args, **kwds):
            _start_time = time.time()
            func_returnval = func(*args, **kwds)
            _elapsed_time = time.time() - _start_time
            logger.debug('{}.{} Completed in {:.9f} seconds'.format(
                func.__module__, func.__name__, _elapsed_time))
            return func_returnval
        return log_runtime_wrapper
    return decorator
