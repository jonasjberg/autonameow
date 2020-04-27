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

import pprint


def check_isinstance(thing, expected_type, msg=None):
    """
    Checks that a given "thing" is an instance of "expected_type".

    Args:
        thing: The object to test.
        expected_type: Expected type of the passed in "thing".
        msg: Optional message to include in the assertion error.

    Raises:
        AssertionError: Given "thing" is not an instance of "expected_type".
    """
    if not __debug__:
        return

    if not isinstance(thing, expected_type):
        error_msg = 'Expected instance of {!s}.  Got {!s}\n{!s}'.format(
            expected_type, type(thing), pprint.pformat(thing))
        if msg:
            error_msg += '\n\n{!s}'.format(msg)

        raise AssertionError(error_msg)


def check_isinstance_meowuri(thing, msg=None):
    """
    Checks that a given "thing" is an instance of class "MeowURI".

    Args:
        thing: The object to test.
        msg: Optional message to include in with a failed assertion error.

    Raises:
        AssertionError: Given object is not an instance of the "MeowURI" class.
    """
    if not __debug__:
        return

    from core.model import MeowURI
    check_isinstance(thing, MeowURI, msg)


def check_isinstance_fileobject(thing, msg=None):
    """
    Checks that a given "thing" is an instance of class "FileObject".

    Args:
        thing: The object to test.
        msg: Optional message to include in with a failed assertion error.

    Raises:
        AssertionError: Given object is not an instance of "FileObject".
    """
    if not __debug__:
        return

    # NOTE(jonas): Prevent circular imports.
    from core.fileobject import FileObject
    check_isinstance(thing, FileObject, msg)
