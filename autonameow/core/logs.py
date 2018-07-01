# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import shutil
import time
from contextlib import contextmanager
from functools import wraps


LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
TERMINAL_WIDTH, TERMINAL_HEIGHT = shutil.get_terminal_size(fallback=(80, 24))


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

    # This module is likely imported from a lot of places. The "lazy" import
    # below is intended to prevent prematurely importing third-party modules
    # that might be missing, like 'prompt_toolkit'.
    from core.view import cli

    # NOTE(jonas): This is probably a bad idea, but seems to work good enough.
    # TODO: [hardcoded] Remove spaces after labels, used for alignment.
    logging.addLevelName(logging.INFO, cli.colorize(
        '[INFO]    ', fore='LIGHTBLUE_EX', style='BRIGHT'
    ))
    logging.addLevelName(logging.DEBUG, cli.colorize(
        '[DEBUG]   ', fore='BLUE'
    ))
    logging.addLevelName(logging.WARNING, cli.colorize(
        '[WARNING] ', fore='RED', style='BRIGHT'
    ))
    logging.addLevelName(logging.ERROR, cli.colorize(
        '[ERROR]   ', fore='RED', style='BRIGHT'
    ))
    logging.addLevelName(logging.CRITICAL, cli.colorize(
        '[CRITICAL]', fore='LIGHTRED_EX', style='BRIGHT'
    ))

    # Setup logging output format.
    # TODO: Make logging verbosity more controllable with additional logging
    #       levels, enabled by adding on any number of '-v' options to the
    #       command-line. For instance, verbosity levels 1 and 3 would be
    #       enabled with '-v' and '-vvv', respectively.

    _colored_timestamp = cli.colorize('%(asctime)s', style='DIM')
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

    # Reset global list of logged run-times.
    # TODO: [cleanup] Do not use global variable to store logged run-times
    global global_logged_runtime
    global_logged_runtime = list()

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

    # Reset global list of logged run-times.
    # TODO: [cleanup] Do not use global variable to store logged run-times
    global global_logged_runtime
    global_logged_runtime = list()

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


# TODO: [cleanup] Do not use global variable to store logged run-times
global_logged_runtime = list()


def center_pad(string, maxwidth, fillchar):
    """
    Centers the given string and fills all but two padding spaces with
    'fillchar' so that the returned string is 'maxwidth' characters wide.

    The string is returned as-is if its length exceeds 'width'.

    Args:
        string: Unicode string to center.
        maxwidth: Number of characters to fill, as an integer.
        fillchar: Unicode character used to fill any left over space.

    Returns:
        The given string, padded with two spaces and surrounded by
        'fillchar' so that the total number of characters is 'maxwidth'.
    """
    assert isinstance(string, str)
    assert isinstance(fillchar, str)
    assert isinstance(maxwidth, int)
    if maxwidth < 0:
        maxwidth = 0

    string_len = len(string)
    if string_len + 1 == maxwidth:
        # Pad with one leading space char to match the width.
        return ' ' + string
    if string_len + 2 > maxwidth:
        # Padding with one space on either side would exceed the width.
        return string

    # Add one space on either space, fill any remaining with 'fillchar'.
    return ' {!s} '.format(string).center(maxwidth, fillchar)


def center_pad_log_entry(string):
    """
    Uses max width tailored to work well in a debug log message.
    """
    assert isinstance(string, str)
    return center_pad(string, maxwidth=TERMINAL_WIDTH - 80, fillchar='=')


@contextmanager
def report_runtime(reporter_function, description, decorate=True):
    """
    Context manager that reports the time taken for the context to complete.

    Args:
        reporter_function: Callable that accepts Unicode string messages.
        description: Name of thing being measured for use in the log entry.
        decorate: Whether to center and pad the string passed to the reporter.
    """
    assert callable(reporter_function)
    assert isinstance(description, str)

    def _report(message):
        if decorate:
            _msg = center_pad(message, maxwidth=TERMINAL_WIDTH, fillchar='=')
        else:
            _msg = message
        reporter_function(_msg)

    _report('{} Started'.format(description))
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        completed_msg = '{} Completed in {:.9f} seconds'.format(description, elapsed_time)
        _report(completed_msg)


@contextmanager
def log_runtime(logger, description, log_level=None):
    """
    Context manager that logs the time taken for the context to complete.

    Args:
        logger: Logger instance that is used to log the results.
        description: Name of thing being measured for use in the log entry,
                     as a Unicode string.
        log_level: Log level to call the logger instance with, as a string
                   or integer. Refer to 'logging.getLevelName()'.
    """
    assert isinstance(description, str)

    if not log_level:
        # Include log level 'NOTSET' (0)
        log_level = 'DEBUG'

    # Translate either string or integer log levels to integer.
    _log_level = logging.getLevelName(log_level)

    def _log(message):
        decorated_message = center_pad_log_entry(message)
        logger.log(_log_level, decorated_message)

    global global_logged_runtime
    _log('{} Started'.format(description))
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        completed_msg = '{} Completed in {:.9f} seconds'.format(description, elapsed_time)
        global_logged_runtime.append(completed_msg)
        _log(completed_msg)


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
        @wraps(func)
        def log_runtime_wrapper(*args, **kwds):
            _start_time = time.time()
            func_returnval = func(*args, **kwds)
            _elapsed_time = time.time() - _start_time
            completed_msg = '{}.{} Completed in {:.9f} seconds'.format(
                func.__module__, func.__name__, _elapsed_time)
            global global_logged_runtime
            global_logged_runtime.append(completed_msg)
            logger.debug(completed_msg)
            return func_returnval
        return log_runtime_wrapper
    return decorator


def log_previously_logged_runtimes(logger):
    global global_logged_runtime
    for entry in global_logged_runtime:
        logger.debug(entry)


DEBUG = bool(__debug__)
