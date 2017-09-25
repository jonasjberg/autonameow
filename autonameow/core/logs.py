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

import logging

from core.util import cli


def init_logging(args):
    """
    Configures the log format and logging settings.

    Args:
        args: Parsed option arguments as type 'argparse.NameSpace'.
    """
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

    _colored_timestamp = cli.colorize('%(asctime)s', fore='LIGHTBLACK_EX',
                                      style='DIM')
    if args.debug:
        fmt = (
            _colored_timestamp
            + ' %(levelname)s %(name)-25.25s %(funcName)-20.20s  %(message)s'
        )
        logging.basicConfig(level=logging.DEBUG, format=fmt,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif args.verbose:
        fmt = (_colored_timestamp
               + ' %(levelname)s %(message)s')
        logging.basicConfig(level=logging.INFO, format=fmt,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif args.quiet:
        fmt = '%(levelname)s %(message)s'
        logging.basicConfig(level=logging.CRITICAL, format=fmt)
    else:
        fmt = '%(levelname)s %(message)s'
        logging.basicConfig(level=logging.WARNING, format=fmt)
