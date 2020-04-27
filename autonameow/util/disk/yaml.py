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

from core import constants as C
from core.exceptions import AutonameowException
from core.exceptions import DependencyError
from core.exceptions import FilesystemError
from util import disk
from util import encoding as enc

try:
    import yaml
except ImportError:
    raise DependencyError(missing_modules='yaml')


# TODO: Merge separate 'YamlLoadError' and "YamlReadError" exceptions?
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


def load_yaml_file(filepath):
    """
    Loads a YAML file from the specified path and returns its contents.

    Args:
        filepath: (Absolute) path of the file to read.

    Returns:
        The contents of the yaml file at the given file as a "Python object"
        (dict).  Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        FilesystemError: The configuration file could not be read and/or loaded.
    """
    if not filepath:
        # TODO: [TD0193] Clean up arguments passed to 'FilesystemError'
        raise FilesystemError(
            'Missing required argument "filepath"'
        )
    try:
        with open(enc.syspath(filepath), 'r',
                  encoding=C.DEFAULT_ENCODING) as fh:
            return load_yaml(fh)
    except (OSError, YamlLoadError) as e:
        # TODO: [TD0193] Clean up arguments passed to 'FilesystemError'
        raise FilesystemError(e)


def write_yaml(data, destination=None):
    _kwargs = dict(
        encoding=C.DEFAULT_ENCODING,
        default_flow_style=False,
        width=160,
        indent=4
    )
    # TODO: [hack] Pass stdout to destination instead of returning the result?
    if destination is not None:
        yaml.dump(data, destination, **_kwargs)
        return None
    return yaml.dump(data, **_kwargs)


def write_yaml_file(dest_filepath, datadict):
    """
    Writes the given data ("Python object"/dict) to the specified path.

    NOTE: The destination path is *OVERWRITTEN* if it already exists!

    Args:
        dest_filepath: The (absolute) path to the output file as a bytestring.
        datadict: Data to write as a "Python object" (dict).
                  Refer to: http://pyyaml.org/wiki/PyYAMLDocumentation

    Raises:
        FilesystemError: The yaml file could not be written.
    """
    if not dest_filepath:
        # TODO: [TD0193] Clean up arguments passed to 'FilesystemError'
        raise FilesystemError(
            'Missing required argument "dest_path"'
        )
    if not disk.has_permissions(disk.dirname(dest_filepath), 'w'):
        # TODO: [TD0193] Clean up arguments passed to 'FilesystemError'
        raise FilesystemError(dest_filepath, 'Insufficient permissions')

    try:
        with open(enc.syspath(dest_filepath), 'w',
                  encoding=C.DEFAULT_ENCODING) as fh:
            write_yaml(datadict, fh)
    except (OSError, UnicodeEncodeError, yaml.YAMLError) as e:
        # TODO: [TD0193] Clean up arguments passed to 'FilesystemError'
        raise FilesystemError(dest_filepath, e)
