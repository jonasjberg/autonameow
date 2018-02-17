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
import pickle

from core import (
    config,
    exceptions,
    types,
)
from core import constants as C
from util import encoding as enc
from util import (
    disk,
    sanity
)


log = logging.getLogger(__name__)


def get_config_persistence_path():
    _active_config = config.ActiveConfig
    if not _active_config:
        return C.DEFAULT_PERSISTENCE_DIR_ABSPATH

    try:
        _path = _active_config.get(['PERSISTENCE', 'cache_directory'])
    except AttributeError:
        _path = None

    if not _path:
        # TODO: Duplicate default setting! Already set in 'configuration.py'.
        _path = C.DEFAULT_PERSISTENCE_DIR_ABSPATH

    sanity.check_internal_bytestring(_path)
    return _path


class BasePersistence(object):
    """
    Abstract base class for all file-based data persistence implementations.

    Example initialization and storage:

        p = AutonameowPersistence('meow-persistence')
        p.set('meow-data', {'a': 1, 'b': 2})

    This will cache the data in memory by storing in a class instance dict,
    and also write the data to disk using the path:

        "PERSISTENCE_DIR_ABSPATH/meow-persistence_meow-data"

    Example retrieval:

        stored_data = p.get('meow-data')
        assert stored_data == {'a': 1, 'b': 2}

    The idea is to keep many smaller files instead of a single shared file
    for possibly easier pruning of old date, file size limits, etc.

    Inheriting class must implement '_load' and '_dump' which does the actual
    serialization and reading/writing to disk.
    """
    PERSISTENCE_FILE_PREFIX_SEPARATOR = '_'

    def __init__(self, file_prefix, persistence_dir_abspath=None):
        self._data = dict()

        # Cache for computed paths.
        self._persistence_file_abspath_cache = dict()

        if not persistence_dir_abspath:
            self._persistence_dir_abspath = get_config_persistence_path()
        else:
            self._persistence_dir_abspath = persistence_dir_abspath
        sanity.check_internal_bytestring(self._persistence_dir_abspath)
        assert os.path.isabs(enc.syspath(self._persistence_dir_abspath))

        _prefix = types.force_string(file_prefix)
        if not _prefix.strip():
            raise ValueError(
                'Argument "file_prefix" must be a valid string'
            )
        # TODO: Add hardcoded prefix to the prefix for arguably "safer" deletes?
        self.persistencefile_prefix = _prefix

        self._dp = enc.displayable_path(self._persistence_dir_abspath)
        if not self.has_persistencedir():
            log.debug('Directory for persistent storage does not exist:'
                      ' "{!s}"'.format(self._dp))

            try:
                disk.makedirs(self._persistence_dir_abspath)
            except exceptions.FilesystemError as e:
                raise PersistenceError('Unable to create persistence directory'
                                       ' "{!s}": {!s}'.format(self._dp, e))
            else:
                log.info(
                    'Created persistence directory: "{!s}"'.format(self._dp)
                )

        if not self.has_persistencedir_permissions():
            raise PersistenceError('Persistence directory requires '
                                   'RWX-permissions: "{!s}'.format(self._dp))

        log.debug(
            '{!s} using persistence directory "{!s}"'.format(self, self._dp)
        )

    @property
    def persistence_dir_abspath(self):
        return self._persistence_dir_abspath

    def has_persistencedir_permissions(self):
        try:
            return disk.has_permissions(self._persistence_dir_abspath, 'rwx')
        except (TypeError, ValueError):
            return False

    def has_persistencedir(self):
        try:
            return bool(disk.exists(self._persistence_dir_abspath)
                        and disk.isdir(self._persistence_dir_abspath))
        except exceptions.FilesystemError:
            return False

    def _persistence_file_abspath(self, key):
        if key in self._persistence_file_abspath_cache:
            return self._persistence_file_abspath_cache[key]

        string_key = types.force_string(key)
        if not string_key.strip():
            raise KeyError('Invalid key: "{!s}" ({!s})'.format(key, type(key)))

        _basename = '{pre}{sep}{key}'.format(
            pre=self.persistencefile_prefix,
            sep=self.PERSISTENCE_FILE_PREFIX_SEPARATOR,
            key=key
        )
        _p = enc.normpath(
            os.path.join(enc.syspath(self._persistence_dir_abspath),
                         enc.syspath(enc.encode_(_basename)))
        )
        self._persistence_file_abspath_cache[key] = _p
        return _p

    def get(self, key):
        """
        Returns data from the persistent data storage.

        Args:
            key (str): The key of the data to retrieve.
                       Postfix of the persistence file that is written to disk.

        Returns:
            Any data stored with the given key, as any serializable type.
        Raises:
            KeyError: The given 'key' is not a valid non-empty string,
                      or the key is not found in the persistent data.
            PersistenceError: Failed to read stored data for some reason;
                              data corruption, encoding errors, missing files..
        """
        if not key:
            raise KeyError

        if key not in self._data:
            key_file_path = self._persistence_file_abspath(key)
            if not disk.exists(key_file_path):
                # Avoid displaying errors on first use.
                raise KeyError

            try:
                value = self._load(key_file_path)
                self._data[key] = value
            except (EOFError, ValueError) as e:
                # Might raise 'EOFError' if the pickled file is empty.
                _dp = enc.displayable_path(key_file_path)
                log.error(
                    'Error when reading key "{!s}" from persistence file "{!s}"'
                    ' (corrupt file?); {!s}'.format(key, _dp, e)
                )
                self.delete(key)
                raise KeyError
            except OSError as e:
                _dp = enc.displayable_path(key_file_path)
                log.warning(
                    'Error while trying to read key "{!s}" from persistence'
                    ' file "{!s}"; {!s}'.format(key, _dp, e)
                )
                raise KeyError
            except AttributeError as e:
                # Could happen if pickled objects implementation has changed.
                _dp = enc.displayable_path(key_file_path)
                log.error(
                    'Error reading key "{!s}" from persistence file "{!s}" '
                    '(object version mismatch?); {!s}'.format(key, _dp, e)
                )
                self.delete(key)
            except Exception as e:
                _dp = enc.displayable_path(key_file_path)
                log.critical(
                    'Caught top-level exception reading key "{!s}" from'
                    'persistence file "{!s}"; {!s}'.format(key, _dp, e)
                )
                raise PersistenceError('Error while reading persistence; '
                                       '{!s}'.format(e))

        return self._data.get(key)

    def set(self, key, value):
        """
        Stores data in the persistent data store.

        Args:
            key (str): The key to store the data under.
                       Postfix of the file that is written to disk.
            value: The data to store, as any serializable type.
        """
        self._data[key] = value

        key_file_path = self._persistence_file_abspath(key)
        try:
            self._dump(value, key_file_path)
        except OSError as e:
            _dp = enc.displayable_path(key_file_path)
            log.error(
                'Error while trying to write key "{!s}" with value "{!s}" to '
                'persistence file "{!s}"; {!s}'.format(key, value, _dp, e)
            )

    def delete(self, key):
        try:
            del self._data[key]
        except KeyError:
            pass

        _p = self._persistence_file_abspath(key)
        _dp = enc.displayable_path(_p)
        log.debug('Deleting persistence file "{!s}"'.format(_dp))
        try:
            disk.delete(_p, ignore_missing=True)
        except exceptions.FilesystemError as e:
            raise PersistenceError(
                'Error while deleting "{!s}"; {!s}'.format(_dp, e)
            )
        else:
            log.debug('Deleted persistence file "{!s}"'.format(_dp))

    def has(self, key):
        # TODO: Test this ..
        if key in self._data:
            return True

        key_file_path = self._persistence_file_abspath(key)
        try:
            os.path.exists(key_file_path)
        except OSError:
            return False
        else:
            return True

    def keys(self):
        # TODO: This is a major security vulnerability (!)
        out = []
        key_file_path = enc.syspath(self._persistence_dir_abspath)
        for bytestring_basename in os.listdir(key_file_path):
            string_basename = types.force_string(bytestring_basename)
            if not string_basename:
                continue

            key = _basename_as_key(string_basename, self.persistencefile_prefix,
                                   self.PERSISTENCE_FILE_PREFIX_SEPARATOR)
            if key:
                out.append(key)
        return out

    def flush(self):
        """
        Delete all data in RAM and in the persistent storage.
        """
        self._data = dict()

        for key in self.keys():
            try:
                self.delete(key)
            except PersistenceError:
                pass

    def filesize(self, key):
        """
        Get the file size in bytes of the stored data under the given key.
        """
        if not key:
            raise KeyError

        key_file_path = self._persistence_file_abspath(key)
        if not os.path.exists(enc.syspath(key_file_path)):
            return 0

        try:
            size = disk.file_bytesize(key_file_path)
            return size
        except exceptions.FilesystemError as e:
            _dp = enc.displayable_path(key_file_path)
            log.error(
                'Error when getting file size for persistence file "{!s}"'
                ' from key "{!s}"; {!s}'.format(_dp, key, e)
            )
            raise PersistenceError(e)

    def _load(self, file_path):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def _dump(self, value, file_path):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return '{}("{}")'.format(self.__class__.__name__,
                                 self.persistencefile_prefix)


def _basename_as_key(str_basename, persistencefile_prefix,
                     persistence_file_prefix_separator):
    if not str_basename.startswith(persistencefile_prefix):
        return None

    # Remove the first occurance of the prefix.
    key = str_basename.replace(persistencefile_prefix, '', 1)

    # Remove the first occurrence of the separator.
    if key.startswith(persistence_file_prefix_separator):
        key = key[len(persistence_file_prefix_separator):]

    return key


class PicklePersistence(BasePersistence):
    """
    Persistence implementation using 'pickle' to read/write data to disk.
    """
    def _load(self, file_path):
        with open(enc.syspath(file_path), 'rb') as fh:
            return pickle.load(fh, encoding='bytes')

    def _dump(self, value, file_path):
        with open(enc.syspath(file_path), 'wb') as fh:
            pickle.dump(value, fh, pickle.HIGHEST_PROTOCOL)


class PersistenceError(exceptions.AutonameowException):
    """Irrecoverable error while reading or writing persistent data."""


def get_persistence(file_prefix, persistence_dir_abspath=None):
    """
    Main "public" interface for getting a mechanism for persistent storage.

    Callers should not be concerned with how (if) files are written to disk.
    This provides a common interface for using "some" persistent storage.

    Args:
        file_prefix: Used as the first part of the storage file basename.
                     The second part is the "key" used when calling 'set()'.
        persistence_dir_abspath: Optional absolute bytestring path to the
                                 directory to use when storing persistent data.

    Returns: An instance of a 'BasePersistence' subclass.
    """
    try:
        return PicklePersistence(file_prefix, persistence_dir_abspath)
    except PersistenceError as e:
        log.error('Persistence unavailable :: {!s}'.format(e))
        return None
