# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
import os
import platform

from core import constants as C
from core.config.config_parser import ConfigurationParser
from core.config.default_config import DEFAULT_CONFIG
from core.exceptions import ConfigError
from core.exceptions import FilesystemError
from util import disk
from util import encoding as enc


FILEPATH_CONFIG_MACOS = '~/Library/Application Support'
FILEPATH_CONFIG_UNIX_VAR = 'XDG_CONFIG_HOME'
FILEPATH_CONFIG_UNIX_FALLBACK = '~/.config'
FILEPATH_CONFIG_WINDOWS_VAR = 'APPDATA'
FILEPATH_CONFIG_WINDOWS_FALLBACK = '~\\AppData\\Roaming'

# TODO: [TD0162] Split up 'autonameow.yaml' into separate files.
CONFIG_BASENAME = 'autonameow.yaml'


log = logging.getLogger(__name__)


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
    paths = list()

    if platform.system() == 'Darwin':
        paths.append(FILEPATH_CONFIG_MACOS)
        paths.append(FILEPATH_CONFIG_UNIX_FALLBACK)

        if FILEPATH_CONFIG_UNIX_VAR in os.environ:
            paths.append(os.environ[FILEPATH_CONFIG_UNIX_VAR])

    elif platform.system() == 'Windows':
        # NOTE: Unsupported platform!
        paths.append(FILEPATH_CONFIG_WINDOWS_FALLBACK)
        if FILEPATH_CONFIG_WINDOWS_VAR in os.environ:
            paths.append(os.environ[FILEPATH_CONFIG_WINDOWS_VAR])

    else:
        # Assume Unix.
        paths.append(FILEPATH_CONFIG_UNIX_FALLBACK)

        if FILEPATH_CONFIG_UNIX_VAR in os.environ:
            paths.append(os.environ[FILEPATH_CONFIG_UNIX_VAR])

    abs_paths = list()
    for path in paths:
        path = os.path.abspath(os.path.expanduser(path))
        if path not in abs_paths:
            abs_paths.append(path)

    return abs_paths


def config_file_path():
    """
    Returns the path to the configuration file. The file might or might not
    actually exist.

    Returns:
        The absolute path to the autonameow configuration file as a string
        in the "internal bytestring" encoding.
    Raises:
        ConfigError: No config path candidates could be found.
    """
    dirs = config_dirs()
    if not dirs:
        raise ConfigError('No configurations paths were found')

    # Path name encoding boundary. Convert to internal bytestring format.
    config_path = disk.joinpaths(dirs[0], CONFIG_BASENAME)
    return enc.normpath(config_path)


def has_config_file():
    """
    Checks if a configuration file is available.

    Returns:
        True if a configuration file is available, else False.
    """
    path = DefaultConfigFilePath
    return bool(disk.isfile(path) or disk.islink(path))


def load_config_from_file(file_path):
    parser = ConfigurationParser()
    return parser.from_file(file_path)


def write_default_config():
    """
    Writes a default configuration file in YAML format to disk.

    Raises:
        ConfigError: The default configuration file could not be written.
    """
    path = DefaultConfigFilePath
    if disk.exists(path):
        raise ConfigError(
            'Path exists: "{}"'.format(enc.displayable_path(path))
        )

    default_config_ = DEFAULT_CONFIG.copy()
    default_config_['autonameow_version'] = C.STRING_PROGRAM_VERSION

    try:
        disk.write_yaml_file(path, default_config_)
    except FilesystemError as e:
        raise ConfigError(e)


DefaultConfigFilePath = config_file_path()
