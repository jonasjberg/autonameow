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

import logging
import os
import platform

try:
    import yaml
except ImportError:
    raise SystemExit(
        'Missing required module "yaml". '
        'Make sure "pyyaml" is available before running this program.'
    )

from core import constants as C
from core.config.default_config import DEFAULT_CONFIG
from core import (
    exceptions,
    util,
)


log = logging.getLogger(__name__)


CONFDIR_MAC = '~/Library/Application Support'
CONFDIR_UNIX_VAR = 'XDG_CONFIG_HOME'
CONFDIR_UNIX_FALLBACK = '~/.config'
CONFDIR_WINDOWS_VAR = 'APPDATA'
CONFDIR_WINDOWS_FALLBACK = '~\\AppData\\Roaming'
CONFIG_BASENAME = 'autonameow.yaml'
YAML_TAB_PROBLEM = "found character '\\t' that cannot start any token"


class ConfigReadError(exceptions.ConfigError):
    """A configuration file could not be read."""
    def __init__(self, filename, reason=None):
        self.filename = filename
        self.reason = reason

        message = 'file {} could not be read'.format(filename)
        if (isinstance(reason, yaml.scanner.ScannerError)
            and reason.problem == YAML_TAB_PROBLEM):
            # Special-case error message for tab indentation in YAML markup.
            message += ': found tab character at line {}, column {}'.format(
                reason.problem_mark.line + 1,
                reason.problem_mark.column + 1,
                )
        elif reason:
            # Generic error message uses exception's message.
            message += ': {}'.format(reason)

        super(ConfigReadError, self).__init__(message)


class ConfigWriteError(exceptions.ConfigError):
    """A configuration file could not be written."""


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
        raise exceptions.ConfigError('No configurations paths were found')

    # Path name encoding boundary. Convert to internal bytestring format.
    config_path = os.path.normpath(os.path.join(dirs[0], CONFIG_BASENAME))
    return util.enc.normpath(config_path)


def has_config_file():
    """
    Checks if a configuration file is available.

    Returns:
        True if a configuration file is available, else False.
    """
    config_path = util.enc.syspath(DefaultConfigFilePath)
    if os.path.exists(config_path):
        if os.path.isfile(config_path) or os.path.islink(config_path):
            return True

    return False


def write_default_config():
    """
    Writes a default template configuration file in YAML format to disk.

    Raises:
        ConfigWriteError: The default configuration file could not be written.
    """
    config_path = DefaultConfigFilePath

    if os.path.exists(util.enc.syspath(config_path)):
        log.warning(
            'Path exists: "{}"'.format(util.enc.displayable_path(config_path))
        )
        raise ConfigWriteError

    _default_config = DEFAULT_CONFIG.copy()
    _default_config['autonameow_version'] = C.STRING_PROGRAM_VERSION

    write_yaml_file(config_path, _default_config)


def load_yaml_file(file_path):
    """
    Loads a YAML file from the specified path and returns its contents.

    Callers should handle exceptions and logging.

    Args:
        file_path: (Absolute) path of the file to read.

    Returns:
        The contents of the yaml file at the given file as a "Python object"
        (dict).  Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        ConfigReadError: The configuration file could not be read and/or loaded.
    """
    try:
        with open(util.enc.syspath(file_path), 'r',
                  encoding=C.DEFAULT_ENCODING) as fh:
            return yaml.safe_load(fh)
    except (OSError, yaml.YAMLError, UnicodeDecodeError) as e:
        raise ConfigReadError(file_path, e)


def write_yaml_file(dest_path, yaml_data):
    """
    Writes the given data ("Python object"/dict) to the specified path.

    Args:
        dest_path: The (absolute) path to the output file as a bytestring.
                   NOTE: The path will be *OVERWRITTEN* if it already exists!
        yaml_data: Data to write as a "Python object" (dict).
                   Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        ConfigWriteError: The yaml file could not be written.
    """
    if not os.access(os.path.dirname(dest_path), os.W_OK):
        raise ConfigWriteError(dest_path, 'Insufficient permissions')

    try:
        with open(util.enc.syspath(dest_path), 'w',
                  encoding=C.DEFAULT_ENCODING) as fh:
            yaml.dump(yaml_data, fh, default_flow_style=False,
                      encoding=C.DEFAULT_ENCODING,
                      width=160, indent=4)
    except (OSError, yaml.YAMLError) as e:
        raise ConfigWriteError(dest_path, e)


def set_active(config):
    """
    Sets the global configuration.

    Args:
        config:  The new global config as an instance of 'Configuration'.
    """
    global ActiveConfig
    log.debug('Updated active global config ..')
    ActiveConfig = config


# Variables listed here are intended for public, global use.
DefaultConfigFilePath = config_file_path()
ActiveConfig = None
