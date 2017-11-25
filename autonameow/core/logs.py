# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
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

from contextlib import contextmanager
import logging
import time

from core import ui


def init_logging(opts):
    """
    Configures the log format and logging settings.

    Args:
        opts: Dictionary of program options.
    """
    # NOTE(jonas): This is probably a bad idea, but seems to work good enough.
    # TODO: [hardcoded] Remove spaces after labels, used for alignment.
    logging.addLevelName(logging.INFO, ui.colorize(
        '[INFO]    ', fore='LIGHTBLUE_EX', style='BRIGHT'
    ))
    logging.addLevelName(logging.DEBUG, ui.colorize(
        '[DEBUG]   ', fore='BLUE'
    ))
    logging.addLevelName(logging.WARNING, ui.colorize(
        '[WARNING] ', fore='RED', style='BRIGHT'
    ))
    logging.addLevelName(logging.ERROR, ui.colorize(
        '[ERROR]   ', fore='RED', style='BRIGHT'
    ))
    logging.addLevelName(logging.CRITICAL, ui.colorize(
        '[CRITICAL]', fore='LIGHTRED_EX', style='BRIGHT'
    ))

    # Setup logging output format.
    # TODO: Make logging verbosity more controllable with additional logging
    #       levels, enabled by adding on any number of '-v' options to the
    #       command-line. For instance, verbosity levels 1 and 3 would be
    #       enabled with '-v' and '-vvv', respectively.

    _colored_timestamp = ui.colorize('%(asctime)s', style='DIM')
    if opts.get('debug'):
        fmt = (
            _colored_timestamp
            + ' %(levelname)s %(name)-25.25s %(funcName)-20.20s  %(message)s'
        )
        logging.basicConfig(level=logging.DEBUG, format=fmt,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif opts.get('verbose'):
        fmt = (_colored_timestamp
               + ' %(levelname)s %(message)s')
        logging.basicConfig(level=logging.INFO, format=fmt,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif opts.get('quiet'):
        fmt = '%(levelname)s %(message)s'
        logging.basicConfig(level=logging.CRITICAL, format=fmt)
    else:
        fmt = '%(levelname)s %(message)s'
        logging.basicConfig(level=logging.WARNING, format=fmt)


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
