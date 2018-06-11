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
import pickle

from core import config
from core import constants as C
from core import event
from core.exceptions import AutonameowException
from core.exceptions import FilesystemError
from util import coercers
from util import disk
from util import encoding as enc
from util import sanity


log = logging.getLogger(__name__)


class PersistenceError(AutonameowException):
    """Irrecoverable error while reading or writing persistent data."""


class PersistenceImplementationBackendError(PersistenceError):
    """Error while reading/writing using a specific backend. Should only be
    raised from the '_load()' and '_dump()' methods by implementing classes."""


class BasePersistence(object):
    """
    Abstract base class for all file-based data persistence implementations.

    Example initialization and storage:

        p = AutonameowPersistence('meowmeow')
        p.set('kibble', {'a': 1, 'b': 2})

    This will cache the data in memory by storing in a class instance dict,
    and also write the data to disk using the path:

        "PERSISTENCE_DIR_ABSPATH/meowmeow_kibble"

    Example retrieval:

        stored_data = p.get('kibble')
        assert stored_data == {'a': 1, 'b': 2}

    The idea is to keep many smaller files instead of a single shared file
    for possibly easier pruning of old date, file size limits, etc.

    Inheriting class must implement '_load' and '_dump' which does the actual
    serialization and reading/writing to disk.
    These methods should only raise 'PersistenceImplementationBackendError'.
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
        assert disk.isabs(self._persistence_dir_abspath)

        str_file_prefix = coercers.force_string(file_prefix)
        if not str_file_prefix.strip():
            raise ValueError(
                'Argument "file_prefix" must be a valid string'
            )
        # TODO: Add hardcoded prefix to the prefix for arguably "safer" deletes?
        self.persistencefile_prefix = str_file_prefix

        self._dp = enc.displayable_path(self._persistence_dir_abspath)
        if not self.has_persistencedir():
            log.debug('Directory for persistent storage does not exist:'
                      ' "{!s}"'.format(self._dp))

            try:
                disk.makedirs(self._persistence_dir_abspath)
            except FilesystemError as e:
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
        except FilesystemError:
            return False

    def _persistence_file_abspath(self, key):
        if key in self._persistence_file_abspath_cache:
            return self._persistence_file_abspath_cache[key]

        p = _key_as_file_path(key, self.persistencefile_prefix,
                              self.PERSISTENCE_FILE_PREFIX_SEPARATOR,
                              self._persistence_dir_abspath)
        self._persistence_file_abspath_cache[key] = p
        return p

    def get(self, key):
        """
        Returns data from the persistent data storage.

        The key is used as the last part of the basename of file storing
        the data on disk.

        Args:
            key (str): The key of the data to retrieve.

        Returns:
            Any data stored with the given key, as any serializable type.

        Raises:
            KeyError: The given 'key' is not a valid non-empty string, was not
                      found in the persistent data or the read failed.
            PersistenceError: Failed to read stored data for some reason;
                              data corruption, encoding errors, missing files..
                              This should not happen, implementing classes must
                              re-raise any exceptions as
                              'PersistenceImplementationBackendError'.
        """
        if not key:
            raise KeyError

        if key not in self._data:
            key_file_path = self._persistence_file_abspath(key)
            if not disk.exists(key_file_path):
                # Avoid displaying errors on first use.
                raise KeyError

            try:
                key_file_data = self._load(key_file_path)
            except PersistenceImplementationBackendError as e:
                _dp = enc.displayable_path(key_file_path)
                log.error('Error while reading key "{!s}" from file "{!s}"; '
                          '{!s}'.format(key, _dp, e))

                # Is it a good idea to delete files that could not be read?
                log.error('Deleting failed read key "{!s}"'.format(key))
                self.delete(key)

                raise KeyError(e)
            except Exception as e:
                _dp = enc.displayable_path(key_file_path)
                log.critical(
                    'Caught top-level exception reading key "{!s}" from'
                    'persistence file "{!s}"; {!s}'.format(key, _dp, e)
                )
                raise PersistenceError('Error while reading persistence; '
                                       '{!s}'.format(e))
            else:
                self._data[key] = key_file_data

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
        except FilesystemError as e:
            raise PersistenceError(
                'Error while deleting "{!s}"; {!s}'.format(_dp, e)
            )
        else:
            # Computed path should always be cached at this point.
            del self._persistence_file_abspath_cache[key]
            log.debug('Deleted persistence file "{!s}"'.format(_dp))

    def has(self, key):
        if key in self._data:
            return True

        key_file_path = self._persistence_file_abspath(key)
        try:
            return disk.exists(key_file_path)
        except FilesystemError:
            return False

    def keys(self):
        # TODO: This is a major security vulnerability (!)
        out = list()
        for bytestring_basename in disk.listdir(self._persistence_dir_abspath):
            str_basename = coercers.force_string(bytestring_basename)
            if not str_basename:
                continue

            key = _basename_as_key(str_basename, self.persistencefile_prefix,
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
        if not disk.exists(key_file_path):
            return 0

        try:
            size = disk.file_bytesize(key_file_path)
            return size
        except FilesystemError as e:
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

    # Remove the first occurrence of the prefix.
    key = str_basename.replace(persistencefile_prefix, '', 1)

    # Remove the first occurrence of the separator.
    if key.startswith(persistence_file_prefix_separator):
        key = key[len(persistence_file_prefix_separator):]

    return key


def _key_as_file_path(key, persistencefile_prefix,
                      persistence_file_prefix_separator,
                      persistence_dir_abspath):
    str_key = coercers.force_string(key)
    if not str_key.strip():
        raise KeyError('Invalid key: "{!s}" ({!s})'.format(key, type(key)))

    basename = '{pre}{sep}{key}'.format(pre=persistencefile_prefix,
                                        sep=persistence_file_prefix_separator,
                                        key=key)
    bytestring_basename = enc.encode_(basename)
    abspath = coercers.AW_PATH.normalize(
        disk.joinpaths(persistence_dir_abspath, bytestring_basename)
    )
    return abspath


class PicklePersistence(BasePersistence):
    """
    Persistence implementation using 'pickle' to read/write data to disk.
    """
    def _load(self, file_path):
        try:
            with open(enc.syspath(file_path), 'rb') as fh:
                try:
                    return pickle.load(fh, encoding='bytes')
                except (EOFError, ValueError) as e:
                    # Might raise 'EOFError' if the pickled file is empty.
                    raise PersistenceImplementationBackendError(e)
                except AttributeError as e:
                    # Could happen if pickled objects implementation has changed.
                    raise PersistenceImplementationBackendError(e)
                except pickle.UnpicklingError as e:
                    raise PersistenceImplementationBackendError(e)
        except OSError as e:
            raise PersistenceImplementationBackendError(e)

    def _dump(self, value, file_path):
        try:
            with open(enc.syspath(file_path), 'wb') as fh:
                try:
                    pickle.dump(value, fh, pickle.HIGHEST_PROTOCOL)
                except (AttributeError, pickle.PicklingError) as e:
                    raise PersistenceImplementationBackendError(e)
        except OSError as e:
            raise PersistenceImplementationBackendError(e)


def get_persistence(file_prefix, persistence_dir_abspath=None):
    """
    Main "public" interface for getting a mechanism for persistent storage.

    Callers should not be concerned with how (if) files are written to disk.
    This provides a common interface for using "some" persistent storage.

    >>> from autonameow.core.persistence import get_persistence
    >>> p = get_persistence('FOOBAR')
    >>> p.persistence_dir_abspath
    b'/tmp/autonameow_cache'

    No file has been written to '/tmp/autonameow_cache' at this point.
    The call to 'set()' in the following line writes the data to the
    file '/tmp/autonameow_cache/FOOBAR_TESTKEY', which is created if it
    does not already exist.

    >>> p.set('TESTKEY', 'TESTVALUE')
    >>> p.get('TESTKEY')
    'TESTVALUE'

                                                    file_prefix
                                                       |____|
    Path in the above example:  '/tmp/autonameow_cache/FOOBAR_TESTKEY'
                                 |___________________|        |_____|
                                persistence_dir_abspath        "key"

    Args:
        file_prefix: Used as the first part of the storage file basename.
                     The second part is the "key" used when calling 'set()'.
        persistence_dir_abspath: Optional absolute bytestring path to the
                                 directory to use when storing persistent data.

    Returns: A class instance that implements the 'BasePersistence' interface.
    """
    try:
        return PicklePersistence(file_prefix, persistence_dir_abspath)
    except PersistenceError as e:
        log.error('Persistence unavailable :: {!s}'.format(e))
        return None


class PersistencePathStore(object):
    def __init__(self):
        self._config_persistence_path = None
        self.default_persistence_dirpath = C.DEFAULT_PERSISTENCE_DIR_ABSPATH

    def update_from_config(self, active_config):
        if not active_config:
            return

        cache_dirpath = active_config.get(['PERSISTENCE', 'cache_directory'])
        if not cache_dirpath:
            return

        if disk.isdir(cache_dirpath):
            self._config_persistence_path = cache_dirpath
            return

        if disk.exists(cache_dirpath):
            log.warning(
                'Configuration persistence cache directory already exists '
                'and is not a directory: "{!s}"'.format(enc.displayable_path(cache_dirpath))
            )
            return

        try:
            disk.makedirs(cache_dirpath)
        except FilesystemError as e:
            log.error(
                'Unable to create persistence directory path specified in the '
                'configuration: "{!s}"'.format(enc.displayable_path(cache_dirpath))
            )
            log.error(str(e))
            return

        if disk.isdir(cache_dirpath):
            self._config_persistence_path = cache_dirpath

    @property
    def config_persistence_path(self):
        if not self._config_persistence_path:
            log.info('Using DEFAULT persistence file path "{!s}"'.format(
                self.default_persistence_dirpath
            ))
            return self.default_persistence_dirpath

        log.debug('Using persistence path specified in the config "{!s}"'.format(
            self._config_persistence_path
        ))
        return self._config_persistence_path


_persistence_path_store = PersistencePathStore()


def _on_config_changed(*_, **kwargs):
    """
    Called whenever the global configuration changes.
    """
    active_config = kwargs.get('config')
    assert active_config

    _persistence_path_store.update_from_config(active_config)


event.dispatcher.on_config_changed.add(_on_config_changed)


def get_config_persistence_path():
    cache_dirpath = _persistence_path_store.config_persistence_path
    sanity.check_internal_bytestring(cache_dirpath)
    return cache_dirpath
