# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

"""
Modifications of the default 'argparse' parser are extracted here to allow
both the main autonameow program as well as other auxiliary programs like
the regression test runner to use the modified 'argparse' parser.
"""

import argparse


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

    def _split_lines(self, text, width):
        """
        Keep newlines, etc. if the text starts with 'R|'.
        Based on:  https://bitbucket.org/ruamel/std.argparse
        """
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)


def get_argparser(**kwargs):
    """
    Returns a customized instance of 'argparse.ArgumentParser'.

    This function is intended to be transparently equivalent to calling
    'argparse.ArgumentParser()' directly.
    Some keyword arguments are overridden here, passing them will not have
    any effect. Most of the keyword arguments are passed through as-is.

    Returns: An instance of 'argparse.ArgumentParser' with modifications.
    """
    # Merge/override incoming kwargs.
    _kwargs = dict(
        kwargs,
        add_help=False,
        formatter_class=CapitalisedHelpFormatter
    )
    parser = argparse.ArgumentParser(**_kwargs)

    # Iffy, ill-advised manipulation of internals. Likely to break!
    # pylint: disable=protected-access
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'

    # Add back the default '-h'/'--help' but with proper capitalization.
    parser.add_argument(
        '-h', '--help', action='help',
        default=argparse.SUPPRESS,
        help='Show this help message and exit.'
    )

    return parser
