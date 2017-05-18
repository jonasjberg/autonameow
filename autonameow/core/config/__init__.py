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

import platform
import os

import yaml

CONFDIR_MAC = '~/Library/Application Support'
CONFDIR_UNIX_VAR = 'XDG_CONFIG_HOME'
CONFDIR_UNIX_FALLBACK = '~/.config'
CONFDIR_WINDOWS_VAR = 'APPDATA'
CONFDIR_WINDOWS_FALLBACK = '~\\AppData\\Roaming'

CONFIG_BASENAME = 'autonameow.yaml'


def config_dirs():
    """
    Returns a platform-specific list of possible user configuration directories.

    The returned directories are listed in order of priority, from high to low.
    Assume that the first directory to contain a configuration file is the one
    that is used.

    CREDITS: Parts of this code is shamelessly lifted pretty much as-is from
             the venerable "beets" (/beets/util/confit.py) by Adrian Sampson.

    Returns:
        A list of absolute paths to configuration directories, ordered from
        high to low priority.
    """
    paths = []

    if platform.system() == 'Darwin':
        paths.append(CONFDIR_MAC)
        paths.append(CONFDIR_UNIX_FALLBACK)

        if CONFDIR_UNIX_VAR in os.environ:
            paths.append(os.environ[CONFDIR_UNIX_VAR])

    elif platform.system() == 'Windows':
        # NOTE: Unsupported platform!
        paths.append(CONFDIR_WINDOWS_FALLBACK)
        if CONFDIR_WINDOWS_VAR in os.environ:
            paths.append(os.environ[CONFDIR_WINDOWS_VAR])
        pass

    else:
        # Assume Unix.
        paths.append(CONFDIR_UNIX_FALLBACK)

        if CONFDIR_UNIX_VAR in os.environ:
            paths.append(os.environ[CONFDIR_UNIX_VAR])

    abs_paths = []
    for path in paths:
        path = os.path.abspath(os.path.expanduser(path))
        if path not in abs_paths:
            abs_paths.append(path)

    return abs_paths


# TODO: What is this?
def default_config_dict():
    default_config = dict(
        A='a',
        B=dict(
            M='b',
            J='c',
            A='d',
            O='e',
        ),
        C='f'
    )

    return default_config


def config_file_path():
    """
    Returns the path to the configuration file. The file might or might not
    actually exist.

    Returns:
        The absolute path to the autonameow configuration file.
    """

    directories = config_dirs()
    if not directories:
        return False

    out = os.path.normpath(os.path.join(directories[0], CONFIG_BASENAME))
    return out


def config_file():
    """
    Returns the path to an existing configuration file.

    Returns:
        The absolute path to an autonameow configuration file or False.
    """

    out = config_file_path
    if os.path.isfile(out):
        return out

    return False


# TODO: Document.
def has_config_file():
    # TODO: [BL004] Implement copy default configuration.
    file = config_file()
    if file:
        return True

    return False


# TODO: Document.
def write_default_config():
    # TODO: [BL004] Implement copy default configuration.
    config_path = config_file_path
    default_config = default_config_dict()

    if os.path.exists(config_path):
        print('Path exists: "{}"'.format(config_path))
        return False

    if not default_config:
        print('Missing default config!')
        return False

    if os.access(config_path, os.W_OK):
        try:
            with open(config_path, 'w') as fh:
                yaml.dump(default_config, fh, default_flow_style=False)
        except OSError:
            pass


if __name__ == '__main__':
    dirs = config_dirs()

    print('Configuration directories:')
    for dir in dirs:
        print('  "{}"'.format(str(dir)))

    config_file_path = config_file_path()
    print('Configuration file path: "{}"'.format(str(config_file_path)))

    has_config = has_config_file()
    print('Has config file?: "{}"'.format(str(has_config)))

    config_file = config_file()
    print('Configuration file: "{}"'.format(str(config_file)))
