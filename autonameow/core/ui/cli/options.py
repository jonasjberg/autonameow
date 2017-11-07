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
import os

from core import constants as C
from core import util
from core.ui import cli


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
        return util.enc.normpath(arg)

    raise argparse.ArgumentTypeError('Invalid file: "{!s}"'.format(arg))


def init_argparser():
    """
    Initializes the argparser. Adds all possible arguments and options.

    Returns:
        The initialized argument parser as a instance of 'ArgumentParser'.
    """
    parser = argparse.ArgumentParser(
        prog='autonameow',
        description='{} {}'.format(C.STRING_PROGRAM_NAME,
                                         C.STRING_PROGRAM_VERSION),
        epilog='Automatic renaming of files from analysis of '
               'several sources of information.' +
               '\n Project website:  {}'.format(C.STRING_REPO_URL),
        formatter_class=CapitalisedHelpFormatter,
        add_help=False
    )
    # Iffy, ill-advised manipulation of internals. Likely to break!
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'

    # Add back the default '-h'/'--help' but with proper capitalization.
    parser.add_argument(
        '-h', '--help', action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit.'
    )

    optgrp_output = parser.add_mutually_exclusive_group()
    optgrp_output.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        default=False,
        help='Enables debug mode, prints detailed debug information.'
    )
    optgrp_output.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Enables verbose mode, prints additional information.'
    )
    optgrp_output.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        default=False,
        help='Enables quiet mode, suppress all but renames.'
    )

    optgrp_action = parser.add_argument_group(
        'Action options',
        # description='Enable ACTIONS to perform for any matched files.'
    )
    # TODO: [TD0059] Replace '--list-*' options with something more flexible.
    #       I.E. '--list-datetime' and '--list-title' could be '--list {FIELD}'
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

    optgrp_mode = parser.add_argument_group(
        'Operating mode',
        # description='Select program operating mode. Manual or fully automatic.'
    )
    optgrp_mode.add_argument(
        '--automagic',
        dest='mode_automagic',
        action='store_true',
        help='Enable AUTOMAGIC MODE. Try to perform renames without user '
             'interaction by matching the given paths against available rules.'
             ' The information provided by the highest ranked rule is used '
             ' when performing any actions on that path. '
             'The user might still be asked to resolve any uncertainties. '
             'Use the "--batch" option to force non-interactive mode and '
             'skip paths with unresolved queries.'
    )
    optgrp_mode.add_argument(
        '--interactive',
        dest='mode_interactive',
        action='store_true',
        help='(DEFAULT) Enable INTERACTIVE MODE. User selects which of the '
             'analysis results is to make up the new filename.'
    )
    optgrp_mode.add_argument(
        '--batch',
        default=False,
        dest='mode_batch',
        action='store_true',
        help='Enable BATCH MODE. Ignores any and all queries, does not '
             'require any user interaction. Suitable for scripting, etc.'
    )

    parser.add_argument(
        dest='input_paths',
        metavar='INPUT_PATH',
        nargs='*',
        help='Path(s) to file(s) and/or directories of files to process. '
             'If the path is a directory, all files in the directory are '
             'included but any containing directories are not traversed. '
             'Use "--recurse" to enable recursive traversal. '
             'NOTE: Some files (defined in "constants.py") are silently '
             'ignored.  Additional ignore patterns can also be specified in '
             'the config.  Use "--dump-config" to list all ignore patterns.'
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
    optgrp_debug.add_argument(
        '--dump-meowuris',
        dest='dump_meowuris',
        action='store_true',
        help='Dump all MeowURIs registered to the "Repository" at startup. '
             'NOTE: Some sources require explict inclusion and might therefore'
             ' not be included.  Use "--debug" for more information.'
    )

    return parser


def cli_parse_args(raw_args):
    """
    Parses raw positional arguments.

    Parses the given option arguments with 'argparse'.

    Args:
        raw_args: The option arguments as a list of strings.

    Returns:
        Parsed option arguments as type 'argparse.NameSpace'.
    """
    parser = init_argparser()
    return parser.parse_args(args=raw_args)


def prettyprint_options(opts, extra_opts):
    """
    Prints information on the command line options that are in effect.

    Mainly for debug purposes.

    Args:
        opts: The parsed options returned by argparse.
        extra_opts: Extra information to be included, as type dict.
    """
    COLSEP = ':'

    opts_dict = dict(opts)
    if extra_opts:
        opts_dict.update(extra_opts)

    cf = cli.ColumnFormatter()
    for key, value in opts_dict.items():
        strkey = str(key)

        if isinstance(value, list):
            if len(value) == 0:
                cf.addrow(strkey, COLSEP, str(value))
            else:
                cf.addrow(strkey, COLSEP, str(value[0]))
                for v in value[1:]:
                    cf.addrow(None, None, str(v))

        else:
            cf.addrow(strkey, COLSEP, str(value))

    cf.addemptyrow()
    cf.setalignment('left', 'right', 'left')

    cli.msg('Current Options', style='heading')
    cli.msg(str(cf))


class CapitalisedHelpFormatter(argparse.HelpFormatter):
    """
    Fix for capitalization of the usage help text.

    Based on the following post:
    https://stackoverflow.com/a/35848313
    https://stackoverflow.com/questions/35847084/customize-argparse-help-message
    """
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super(CapitalisedHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)
