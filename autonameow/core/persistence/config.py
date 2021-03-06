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


def config_dirpath_candidates(system_platform):
    """
    Returns a list of possible platform-specific user configuration directories.

    The returned directories are listed in order of priority, from high to low.
    Assume that the first directory to contain a configuration file is the one
    that is used.

    Args:
        system_platform (str): Simplified name of the current operating system;
                               E.G. "Linux", "windows", etc.

    CREDITS: Parts of this code is shamelessly lifted pretty much as-is from
             the venerable "beets" (/beets/util/confit.py) by Adrian Sampson.

    Returns:
        A list of absolute paths to configuration directories sorted by
        priority/probability, from high to low.
    """
    _system_platform = system_platform.lower()

    candidate_paths = list()

    def _consider_candidate(_path):
        _abspath = os.path.abspath(os.path.expanduser(_path))
        if _abspath not in candidate_paths:
            candidate_paths.append(_abspath)

    if _system_platform == 'darwin':
        _consider_candidate(FILEPATH_CONFIG_MACOS)
        _consider_candidate(FILEPATH_CONFIG_UNIX_FALLBACK)

        if FILEPATH_CONFIG_UNIX_VAR in os.environ:
            _consider_candidate(os.environ[FILEPATH_CONFIG_UNIX_VAR])

    elif _system_platform == 'windows':
        # NOTE: Unsupported platform!
        _consider_candidate(FILEPATH_CONFIG_WINDOWS_FALLBACK)
        if FILEPATH_CONFIG_WINDOWS_VAR in os.environ:
            _consider_candidate(os.environ[FILEPATH_CONFIG_WINDOWS_VAR])

    else:
        # Assume *nix.
        _consider_candidate(FILEPATH_CONFIG_UNIX_FALLBACK)

        if FILEPATH_CONFIG_UNIX_VAR in os.environ:
            _consider_candidate(os.environ[FILEPATH_CONFIG_UNIX_VAR])

    return candidate_paths


def config_filepath_for_platform():
    """
    Returns the path to a configuration file for the running operating system.
    Any file at the path might or might not actually exist.

    Returns:
        The absolute path to the autonameow configuration filepath as a string
        with the "internal bytestring" encoding.

    Raises:
        ConfigError: No config path candidates could be found.
    """
    dirpaths = config_dirpath_candidates(system_platform=platform.system())
    if not dirpaths:
        raise ConfigError('Unable to determine configuration directory path')

    # Path name encoding boundary. Convert to internal bytestring format.
    config_filepath = disk.joinpaths(dirpaths[0], CONFIG_BASENAME)
    return enc.normpath(config_filepath)


def has_config_file():
    """
    Checks if a configuration file is available.

    Returns:
        True if a configuration file is available, else False.
    """
    path = DefaultConfigFilePath
    return bool(disk.isfile(path) or disk.islink(path))


def load_config_from_file(filepath):
    parser = ConfigurationParser()
    return parser.from_file(filepath)


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


DefaultConfigFilePath = config_filepath_for_platform()
