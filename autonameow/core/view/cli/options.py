# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import argparse
import os
from collections import namedtuple

from core import constants as C
from core.view import cli
from util import disk
from util import encoding as enc


def arg_is_readable_file(arg):
    """
    Used by argparse to validate argument is a readable file.
    Handles expansion of '~' into the proper user "$HOME" directory.
    Throws an exception if the checks fail. Exception is caught by argparse.

    Args:
        arg: The argument to validate.

    Returns:
        The expanded absolute path specified by "arg" if valid.
    """
    if arg and disk.isfile(arg) and disk.has_permissions(arg, 'r'):
        arg = os.path.expanduser(arg)
        return enc.normpath(arg)
    raise argparse.ArgumentTypeError('Invalid file: "{!s}"'.format(arg))


def init_argparser():
    """
    Initializes the argparser. Adds all possible arguments and options.

    Returns:
        The initialized argument parser as a instance of 'ArgumentParser'.
    """
    parser = cli.get_argparser(
        prog='autonameow',
        description='{} {} <{}>'.format(C.STRING_PROGRAM_NAME,
                                        C.STRING_PROGRAM_VERSION,
                                        C.STRING_AUTHOR_EMAIL),
        epilog='Automatic renaming of files from analysis of '
               'several sources of information.'
               '\n Project website:  {}'.format(C.STRING_URL_REPO),
    )

    default_value_template = 'DEFAULT: %(default)s'

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
    optgrp_action.add_argument(
        '--list-all',
        dest='list_all',
        action='store_true',
        help='List all information found.'
    )
    optgrp_action.add_argument(
        '--list-rulematch',
        dest='list_rulematch',
        action='store_true',
        help='List detailed information on any rule matching.'
    )

    optgrp_mode_method = parser.add_argument_group(
        'Operating mode',
        description='Methods for resolving new file names.'
    )
    optgrp_mode_method.add_argument(
        '--automagic',
        dest='automagic',
        action='store_true',
        default=False,
        help='Enable AUTOMAGIC MODE. Try to perform renames without user '
             'interaction, first by matching the given paths against available'
             ' rules. Information provided by the highest ranked rule is used '
             ' when performing any actions on that path. If none of the rules '
             'apply, the highest ranked rule scored low, or the data '
             'specified in the rule is unavailable, additional means are used '
             'to come up with suitable alternatives. '
             'The user might still be asked to resolve any uncertainties. '
             'Use the "--batch" option to force non-interactive mode and '
             'skip paths with unresolved queries. '
             + default_value_template
    )
    optgrp_mode_method.add_argument(
        '--postprocess-only',
        dest='postprocess_only',
        action='store_true',
        default=False,
        help='Enable POST-PROCESSING ONLY.'
             'Do not construct new file names, only do post-processing '
             'using any global post-processing settings. '
             + default_value_template
    )

    optgrp_mode_interaction = parser.add_argument_group(
        'User interaction',
        description='Controls how the user will interact with the program.'
    )
    optgrp_mode_interaction.add_argument(
        '--timid',
        dest='timid',
        action='store_true',
        default=False,
        help='Enable TIMID MODE. '
             'Have the user confirm each file before renaming. '
             + default_value_template
    )
    optgrp_mode_interaction.add_argument(
        '--interactive',
        dest='interactive',
        action='store_true',
        default=False,
        help='Enable INTERACTIVE MODE. '
             'Have the user weigh in on all decisions. '
             + default_value_template
    )
    optgrp_mode_interaction.add_argument(
        '--batch',
        dest='batch',
        action='store_true',
        default=False,
        help='Enable BATCH MODE. '
             'Abort instead of querying the user, suitable '
             'for scripting, etc. Disables all user interaction except TIMID '
             'MODE file rename confirmations, if enabled. '
             + default_value_template
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
        default=False,
        help='Simulate what would happen but do not actually write any '
             'changes to disk. '
             + default_value_template
    )
    parser.add_argument(
        '--version',
        dest='show_version',
        action='store_true',
        default=False,
        help='Print program version and exit.'
    )
    parser.add_argument(
        '--config-path',
        dest='config_path',
        metavar='CONFIG_PATH',
        type=arg_is_readable_file,
        help='Use configuration file at CONFIG_PATH instead of the default '
             'configuration file path.'
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
             + default_value_template
    )

    optgrp_debug = parser.add_argument_group('Debug/developer options')
    optgrp_debug.add_argument(
        '--dump-options',
        dest='dump_options',
        action='store_true',
        default=False,
        help='Dump options to stdout.'
    )
    optgrp_debug.add_argument(
        '--dump-config',
        dest='dump_config',
        action='store_true',
        default=False,
        help='Dump active configuration to stdout.'
    )
    optgrp_debug.add_argument(
        '--dump-meowuris',
        dest='dump_meowuris',
        action='store_true',
        default=False,
        help='Dump all MeowURIs registered to the "Repository" at startup. '
             'Use "--verbose" for detailed information with a list of '
             'providers excluded due to unsatisfied dependencies.'
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
            if not value:
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


ArgparserOption = namedtuple('ArgparserOption', ('short', 'long', 'dest'))


def get_optional_argparser_options(parser=None):
    """
    Grabs information *options of interest for the regression runner* by
    introspecting an instance of 'ArgumentParser'.

    Intended to be used primarily (solely) by the regression tests so that
    options only need to be defined in this file as compared to manually
    keeping changes in sync.
    Returns *options of interest for the regression runner* as tuples of three
    strings; [SHORT] [GNU] [DEST]:

        SHORT  Short form of the command-line option ("-h")
         LONG  Longer "GNU-style" form of the command-line option ("--help")
         DEST  Name of the attribute that stores the option value.

    Args:
        parser: Optional Instance of 'ArgumentParser' to grab options from.
                Creates a new default parser if unspecified.

    Returns:
        Information on command-line options as a set of Unicode string tuples.
    """
    if not parser:
        parser = init_argparser()

    option_tuples = set()
    for _, action in parser._optionals._option_string_actions.items():
        if action.__class__.__name__ == '_StoreAction':
            # Skip options that accept arguments, such as "--color always".
            continue

        # Compare string lengths to get "GNU-style" '--help' and short form '-h'.
        gnu_style_option_string = max(action.option_strings, key=len)
        short_option_string = min(action.option_strings, key=len)
        if short_option_string == gnu_style_option_string:
            # Option has no short form.
            short_option_string = ''

        option_tuples.add(ArgparserOption(
            short=short_option_string,
            long=gnu_style_option_string,
            dest=action.dest,
        ))

    return option_tuples
