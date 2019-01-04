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

"""
Utility functions for controlling and interacting with system processes.
"""

import os
import shutil
import subprocess
from functools import lru_cache

from core import constants as C
from core.exceptions import AutonameowException


class ChildProcessFailure(AutonameowException):
    """Child process was not successfully executed."""


def blocking_read_stdout(*args):
    """
    Executes a child process and returns its standard output.

    Catches all exceptions and re-raising a 'ChildProcessFailure'.
    The 'ChildProcessFailure' exception is also raised if the child
    process returns a non-zero exit code.

    Args:
        args: Any number of Unicode string arguments to execute,
              Should contain both the process name and any args.

    Returns:
        Standard output of the executed child process as a bytestring.

    Raises:
        ChildProcessFailure: Process returned non-zero or any other error.
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
        raise ChildProcessFailure(e)

    returncode = process.returncode
    if returncode != 0:
        raise ChildProcessFailure(
            'Process returned {!s}. stderr:\n{!s}'.format(returncode, stderr)
        )
    return stdout or b''


@lru_cache(maxsize=128)
def is_executable(command):
    """
    Checks if the given command is executable.

    Args:
        command: The command to test.

    Returns:
        True if the command would be executable, otherwise False.
    """
    return bool(shutil.which(command) is not None)


@lru_cache(maxsize=1)
def git_commit_hash():
    if not is_executable('git'):
        return None

    _old_pwd = os.path.curdir
    try:
        os.chdir(C.AUTONAMEOW_SRCROOT_DIR)
        process = subprocess.Popen(
            ['git', 'rev-parse', '--short', 'HEAD'],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
    except (OSError, ValueError, TypeError, subprocess.SubprocessError):
        return None
    else:
        # NOTE(jonas): git returns 128 for the "fatal: Not a git repository.."
        # error. Substring matching is redundant but probably won't hurt either.
        if process.returncode == 0:
            from util import coercers
            str_stdout = coercers.force_string(stdout).strip()
            if str_stdout and 'fatal: Not a git repository' not in str_stdout:
                return str_stdout
        return None
    finally:
        os.chdir(_old_pwd)


def current_process_id():
    """
    Returns the current process ID as an integer.
    """
    return os.getpid()
