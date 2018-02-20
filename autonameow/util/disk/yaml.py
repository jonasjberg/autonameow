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

try:
    import yaml
except ImportError:
    raise SystemExit(
        'Missing required module "yaml". '
        'Make sure "pyyaml" is available before running this program.'
    )

from core import constants as C
from core.exceptions import (
    AutonameowException,
    FilesystemError
)
from util import encoding as enc
from util import disk


class YamlLoadError(AutonameowException):
    """Error loading YAML data"""


def load_yaml(data):
    """
    Loads YAML from the given data and returns its contents.

    Callers must handle all exceptions.

    Args:
        data: Data to read.

    Returns:
        The parsed YAML contents of the given data as a "Python object"
        (dict).  Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        YamlLoadError: The data could not be successfully parsed.
    """
    try:
        return yaml.safe_load(data)
    except (AttributeError, UnicodeDecodeError, yaml.YAMLError) as e:
        raise YamlLoadError(e)


def load_yaml_file(file_path):
    """
    Loads a YAML file from the specified path and returns its contents.

    Args:
        file_path: (Absolute) path of the file to read.

    Returns:
        The contents of the yaml file at the given file as a "Python object"
        (dict).  Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        FilesystemError: The configuration file could not be read and/or loaded.
    """
    if not file_path:
        raise FilesystemError(
            'Missing required argument "file_path"'
        )
    try:
        with open(enc.syspath(file_path), 'r',
                  encoding=C.DEFAULT_ENCODING) as fh:
            return load_yaml(fh)
    except (OSError, YamlLoadError) as e:
        raise FilesystemError(e)


def write_yaml_file(dest_path, yaml_data):
    """
    Writes the given data ("Python object"/dict) to the specified path.

    Args:
        dest_path: The (absolute) path to the output file as a bytestring.
                   NOTE: The path will be *OVERWRITTEN* if it already exists!
        yaml_data: Data to write as a "Python object" (dict).
                   Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        FilesystemError: The yaml file could not be written.
    """
    if not dest_path:
        raise FilesystemError(
            'Missing required argument "dest_path"'
        )
    if not disk.has_permissions(disk.dirname(dest_path), 'w'):
        raise FilesystemError(dest_path, 'Insufficient permissions')

    try:
        with open(enc.syspath(dest_path), 'w',
                  encoding=C.DEFAULT_ENCODING) as fh:
            yaml.dump(yaml_data, fh,
                      encoding=C.DEFAULT_ENCODING,
                      default_flow_style=False,
                      width=160, indent=4)
    except (OSError, UnicodeEncodeError, yaml.YAMLError) as e:
        raise FilesystemError(dest_path, e)
