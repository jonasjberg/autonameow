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

from colorama import Fore

from core.util import dateandtime


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
    if arg and os.path.exists(arg) and os.path.isfile(arg) \
            and os.access(arg, os.R_OK):
        if arg.startswith('~/'):
            arg = os.path.expanduser(arg)
        return os.path.normpath(os.path.abspath(arg))

    raise argparse.ArgumentTypeError('Invalid file: "{}"'.format(str(arg)))


def init_argparser():
    """
    Initialize the argparser. Add all arguments/options.
    :return: the argument parser
    """
    parser = argparse.ArgumentParser(
        prog='autonameow',
        description='Automatic renaming of files from analysis of '
                    'several sources of information.',
        epilog='Example usage: TODO ..')

    # Add option group for controlling what is printed to stdout.
    optgrp_output = parser.add_mutually_exclusive_group()
    optgrp_output.add_argument('--debug',
                               dest='debug',
                               action='store_true',
                               help='Debug mode.')

    optgrp_output.add_argument('-v', '--verbose',
                               dest='verbose',
                               action='store_true',
                               help='Verbose mode.',
                               default=False)

    optgrp_output.add_argument('-q', '--quiet',
                               dest='quiet',
                               action='store_true',
                               help='Quiet mode.',
                               default=False)

    # Add option group for actions to be performed.
    optgrp_action = parser.add_argument_group('Action options')
    optgrp_action.add_argument('--list-datetime',
                               dest='list_datetime',
                               action='store_true',
                               help='List all found "date/time"-information.')

    optgrp_action.add_argument('--list-title',
                               dest='list_title',
                               action='store_true',
                               help='List all "title"-information.')

    optgrp_action.add_argument('--list-all',
                               dest='list_all',
                               action='store_true',
                               help='List all information found.')

    optgrp_action.add_argument('--prepend-datetime',
                               dest='prepend_datetime',
                               action='store_true',
                               help='Prepend most probable '
                                    '"date/time"-information to file names.')

    # Add option group for operating mode.
    optgrp_mode = parser.add_argument_group('Operating mode')
    optgrp_mode.add_argument('--automagic',
                             dest='automagic',
                             action='store_true',
                             help='Figure out most probable new filename '
                                  'without requiring user interaction.'
                                  ' (development feature)')

    optgrp_mode.add_argument('--interactive',
                             dest='interactive',
                             action='store_true',
                             help='(DEFAULT) Enable interactive mode. User '
                                  'selects which of the analysis results is to '
                                  'make up the new filename.')

    # Add option group for filter options.
    optgrp_filter = parser.add_argument_group('Processing options')
    ignore_to_year_default = str(dateandtime.YEAR_LOWER_LIMIT.strftime('%Y'))
    optgrp_filter.add_argument('--ignore-to-year',
                               metavar='YYYY',
                               type=arg_is_year,
                               default=ignore_to_year_default,
                               dest='filter_ignore_to_year',
                               action='store',
                               help='Ignore all date/time-information for the '
                                    'specified year and years prior. Default: '
                                    '{}'.format(ignore_to_year_default))

    ignore_from_year_default = str(dateandtime.YEAR_UPPER_LIMIT.strftime('%Y'))
    optgrp_filter.add_argument('--ignore-from-year',
                               metavar='YYYY',
                               type=arg_is_year,
                               default=ignore_from_year_default,
                               dest='filter_ignore_from_year',
                               action='store',
                               help='Ignore all date/time-information following'
                                    ' the specified year (inclusive). Default: '
                                    '{}'.format(ignore_from_year_default))

    optgrp_filter.add_argument('--ignore-years',
                               metavar='YYYY',
                               type=arg_is_year,
                               default=[],
                               nargs='+',
                               dest='filter_ignore_years',
                               action='store',
                               help='Ignore date/time-information '
                                    'from the year(s) specified.')

    parser.add_argument(dest='input_files',
                        metavar='filename',
                        nargs='*',
                        help='Input file(s)')

    parser.add_argument('-d', '--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='Simulate what would happen but do not '
                             'actually write any changes to disk.')

    parser.add_argument('--dump-options',
                        dest='dump_options',
                        action='store_true',
                        help='Dump options to stdout.')

    parser.add_argument('--version',
                        dest='show_version',
                        action='store_true',
                        help='Print program version and exit.')

    parser.add_argument('--config-path',
                        dest='config_path',
                        metavar='CONFIG_PATH',
                        nargs=1,
                        type=arg_is_readable_file,
                        help='Use configuration file at CONFIG_PATH instead '
                             'of the default configuration file.')
    return parser


def parse_args(opts):
    """
    Parse command line arguments.
    Check combination legality, print debug info.
    Apply selected options.
    """
    parser = init_argparser()
    args = parser.parse_args(args=opts)

    # Setup logging output format.
    # TODO: Make logging verbosity more controllable with additional logging
    #       levels, enabled by adding on any number of '-v' options to the
    #       command-line. For instance, verbosity levels 1 and 3 would be
    #       enabled with '-v' and '-vvv', respectively.
    if args.debug:
        fmt = Fore.LIGHTBLACK_EX + '%(asctime)s' + Fore.RESET + \
              Fore.LIGHTBLUE_EX + ' %(levelname)-8.8s' + Fore.RESET + \
              ' %(funcName)-25.25s (%(lineno)3d) ' + \
              Fore.LIGHTBLACK_EX + ' -- ' + Fore.RESET + \
              '%(message)-120.120s'
        logging.basicConfig(level=logging.DEBUG, format=fmt,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif args.verbose:
        fmt = Fore.LIGHTBLACK_EX + '%(asctime)s' + Fore.RESET + \
              Fore.LIGHTBLUE_EX + ' %(levelname)-8.8s' + Fore.RESET + \
              Fore.LIGHTBLACK_EX + ' -- ' + Fore.RESET + \
              '%(message)-130.130s'
        logging.basicConfig(level=logging.INFO, format=fmt,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif args.quiet:
        fmt = '%(levelname)s -- %(message)s'
        logging.basicConfig(level=logging.CRITICAL, format=fmt)
    else:
        fmt = '%(levelname)s -- %(message)s'
        logging.basicConfig(level=logging.WARNING, format=fmt)

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


def prettyprint_options(opts):
    """
    Display details on the command line options that are in effect.
    Mainly for debug purposes.
    :param opts: arguments to display
    """
    opts_dict = vars(opts)
    for k, v in opts_dict.items():
        if v == 0:
            v = 'False'
        elif v == 1:
            v = 'True'
        print(('{:<30}'.format(str(k)) + Fore.LIGHTBLACK_EX + ' : ' +
              Fore.RESET + '{:<40}'.format(str(v))))
