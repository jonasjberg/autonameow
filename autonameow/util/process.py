# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   E-mail:          jomeganas[a]g m a i l[dot]com
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
Utility functions for controlling and interacting with system processes.
"""

import subprocess

from core.exceptions import AutonameowException


class ChildProcessError(AutonameowException):
    """Child process was not successfully executed."""


def blocking_read_stdout(*args):
    """
    Executes a child process and returns its standard output.

    Catches all exceptions and re-raising a 'ChildProcessError'.
    The 'ChildProcessError' exception is also raised if the child
    process returns a non-zero exit code.

    Args:
        args: Any number of Unicode string arguments to execute,
              Should contain both the process name and any args.

    Returns:
        Standard output of the executed child process as a bytestring.

    Raises:
        ChildProcessError: Process returned non-zero or any other error.
    """
    try:
        process = subprocess.Popen(
            args,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ChildProcessError(e)

    returncode = process.returncode
    if returncode != 0:
        raise ChildProcessError(
            'Process returned {!s}. stderr:\n{!s}'.format(returncode, stderr)
        )
    return stdout or b''
