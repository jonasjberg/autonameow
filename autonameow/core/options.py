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

import argparse
import logging
import os

from core import util
from core.util import (
    dateandtime,
    cli
)


def arg_is_year(value):
    """
    Check if "value" is a year, here defined as consisting solely of 4 digits,
    with a value in the range 0 >= year > 9999.
    :return: True if the value is a year by the above definition
    """
    if value:
        try:
            ivalue = int(value.strip())
        except ValueError:
            pass
        else:
            if len(str(ivalue)) == 4 and ivalue >= 0:
                return ivalue
    raise argparse.ArgumentTypeError('"{}" is not a valid year'.format(value))


def arg_is_readable_file(arg):
    """
    Used by argparse to validate argument is a readable file.
    Handles expansion of '~' into the proper user "$HOME" directory.
    Throws an exception if the checks fail. Exception is caught by argparse.

    Args:
        arg: The argument to validate.

    Returns: The expanded absolute path specified by "arg" if valid.

    """
    if (arg and os.path.exists(arg) and os.path.isfile(arg)
            and os.access(arg, os.R_OK)):
        if arg.startswith('~/'):
            arg = os.path.expanduser(arg)
        return util.normpath(arg)

    raise argparse.ArgumentTypeError('Invalid file: "{!s}"'.format(arg))


def init_argparser():
    """
    Initializes the argparser. Adds all possible arguments and options.

    Returns:
        The initialized argument parser as a instance of 'ArgumentParser'.
    """
    parser = argparse.ArgumentParser(
        prog='autonameow',
        description='Automatic renaming of files from analysis of '
                    'several sources of information.',
        epilog='Example usage: TODO ..'
    )

    optgrp_output = parser.add_mutually_exclusive_group()
    optgrp_output.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        default=False,
        help='Debug mode. Enables displaying detailed debug information.'
    )
    optgrp_output.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Verbose mode. Enables displaying additional information.'
    )
    optgrp_output.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        default=False,
        help='Quiet mode. Supress all output except critical errors.'
    )

    optgrp_action = parser.add_argument_group('Action options')
    # TODO: Replace '--list-datetime' and '--list-title' with '--list {FIELD}'
    optgrp_action.add_argument(
        '--list-datetime',
        dest='list_datetime',
        action='store_true',
        help='List all found "date/time"-information.'
    )
    optgrp_action.add_argument(
        '--list-title',
        dest='list_title',
        action='store_true',
        help='List all "title"-information.'
    )
    optgrp_action.add_argument(
        '--list-all',
        dest='list_all',
        action='store_true',
        help='List all information found.'
    )

    optgrp_mode = parser.add_argument_group('Operating mode')
    optgrp_mode.add_argument(
        '--automagic',
        dest='automagic',
        action='store_true',
        help='Perform renames without requiring any user interaction. '
             'Matches the given paths against the available file rules. '
             'Paths matched to a rule is renamed in accordance with the rule.'
    )
    optgrp_mode.add_argument(
        '--interactive',
        dest='interactive',
        action='store_true',
        help='(DEFAULT) Enable interactive mode. User selects which of the '
             'analysis results is to make up the new filename.'
    )

    optgrp_filter = parser.add_argument_group('Processing options')

    ignore_to_year_default = str(dateandtime.YEAR_LOWER_LIMIT.strftime('%Y'))
    optgrp_filter.add_argument(
        '--ignore-to-year',
        metavar='YYYY',
        type=arg_is_year,
        default=ignore_to_year_default,
        dest='filter_ignore_to_year',
        action='store',
        help='Ignore all date/time-information for the specified year and '
             'years prior. Default: {}'.format(ignore_to_year_default)
    )

    ignore_from_year_default = str(dateandtime.YEAR_UPPER_LIMIT.strftime('%Y'))
    optgrp_filter.add_argument(
        '--ignore-from-year',
        metavar='YYYY',
        type=arg_is_year,
        default=ignore_from_year_default,
        dest='filter_ignore_from_year',
        action='store',
        help='Ignore all date/time-information following the specified year '
             '(inclusive). Default: {}'.format(ignore_from_year_default)
    )
    optgrp_filter.add_argument(
        '--ignore-years',
        metavar='YYYY',
        type=arg_is_year,
        default=[],
        nargs='+',
        dest='filter_ignore_years',
        action='store',
        help='Ignore date/time-information from the year(s) specified.'
    )

    parser.add_argument(
        dest='input_paths',
        metavar='INPUT_PATH',
        nargs='*',
        help='Path(s) to file(s) to process.'
    )
    parser.add_argument(
        '-d', '--dry-run',
        dest='dry_run',
        action='store_true',
        help='Simulate what would happen but do not actually write any '
             'changes to disk.'
    )
    parser.add_argument(
        '--version',
        dest='show_version',
        action='store_true',
        help='Print program version and exit.'
    )
    parser.add_argument(
        '--config-path',
        dest='config_path',
        metavar='CONFIG_PATH',
        type=arg_is_readable_file,
        help='Use configuration file at CONFIG_PATH instead of the default '
             'configuration file.'
    )
    parser.add_argument(
        '-r', '--recurse',
        dest='recurse_paths',
        action='store_true',
        default=False,
        help='Controls whether directory input paths are traversed '
             'recursively. The default behaviour is to only act on the files '
             'in the specified directory. This flag enables acting on files '
             'in all subdirectories of the specified directory. '
    )

    optgrp_debug = parser.add_argument_group('Debug/developer options')
    optgrp_debug.add_argument(
        '--dump-options',
        dest='dump_options',
        action='store_true',
        help='Dump options to stdout.'
    )
    optgrp_debug.add_argument(
        '--dump-config',
        dest='dump_config',
        action='store_true',
        help='Dump active configuration to stdout.'
    )

    return parser


def initialize(raw_args):
    """
    Handles raw option arguments and initializes logging.

    Configures logging and checks legality of combined options.

    Args:
        raw_args: The option arguments as a list of strings.

    Returns:
        Parsed option arguments as type 'argparse.NameSpace'.
    """
    args = parse_args(raw_args)

    init_logging(args)

    if args.automagic and args.interactive:
        logging.critical('Operating mode must be either one of "automagic" or '
                         '"interactive", not both. Reverting to default: '
                         '[interactive mode].')
        args.automagic = False
        args.interactive = True
    if not args.automagic and not args.interactive:
        logging.debug('Using default operating mode: [interactive mode].')
        args.interactive = True

    return args


def parse_args(raw_args):
    """
    Parses the given option arguments with argparse.

    Args:
        raw_args: The option arguments to parse as a list of strings.

    Returns:
        Parsed option arguments as type 'argparse.NameSpace'.
    """
    parser = init_argparser()
    return parser.parse_args(args=raw_args)


def init_logging(args):
    """
    Configures the log format and logging settings.

    Args:
        args: Parsed option arguments as type 'argparse.NameSpace'.
    """
    # NOTE(jonas): This is probably a bad idea, but seems to work good enough.
    # TODO: [hardcoded] Remove spaces after labels, used for alignment.
    logging.addLevelName(logging.INFO, cli.colorize(
        '[INFO]    ', fore='GREEN'
    ))
    logging.addLevelName(logging.DEBUG, cli.colorize(
        '[DEBUG]   ', fore='BLUE'
    ))
    logging.addLevelName(logging.WARNING, cli.colorize(
        '[WARNING] ', fore='YELLOW', style='BRIGHT'
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
    if args.debug:
        fmt = (_colored_timestamp
               + ' %(levelname)s %(funcName)-25.25s (%(lineno)3d) %(message)s')
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


def prettyprint_options(opts, extra_opts):
    """
    Prints information on the command line options that are in effect.

    Mainly for debug purposes.

    Args:
        opts: The parsed options returned by argparse.
        extra_opts: Extra information to be included, as type dict.
    """
    opts_dict = vars(opts)
    if extra_opts:
        opts_dict.update(extra_opts)

    out = []
    for k, v in opts_dict.items():
        if v == 0:
            v = 'False'
        elif v == 1:
            v = 'True'

        out.append('{:<30} {:<40}'.format(str(k), str(v)))

    cli.msg('Current Options', style='heading')
    cli.msg('\n'.join(out) + '\n')


