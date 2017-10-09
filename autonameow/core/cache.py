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

from core.util import diskutils

try:
    import cPickle as pickle
except ImportError:
    import pickle

from core import (
    exceptions,
    types,
    util,
    config
)


log = logging.getLogger(__name__)


DEFAULT_CACHE_DIRECTORY_ROOT = util.encode_('/tmp')
DEFAULT_CACHE_DIRECTORY_LEAF = util.encode_('autonameow_cache')
DEFAULT_CACHE_DIR_ABSPATH = util.normpath(
    os.path.join(
        util.syspath(DEFAULT_CACHE_DIRECTORY_ROOT),
        util.syspath(DEFAULT_CACHE_DIRECTORY_LEAF)
    )
)
assert DEFAULT_CACHE_DIR_ABSPATH not in (b'', b'/', None)
assert DEFAULT_CACHE_DIR_ABSPATH not in (b'', None)


def get_config_cache_path():
    _active_config = config.ActiveConfig
    if not _active_config:
        return DEFAULT_CACHE_DIR_ABSPATH

    try:
        _cache_path = _active_config.get(['PERSISTENCE', 'cache_directory'])
    except AttributeError:
        _cache_path = None

    if _cache_path:
        return _cache_path
    else:
        # TODO: Duplicate default setting! Already set in 'configuration.py'.
        return DEFAULT_CACHE_DIR_ABSPATH


class BaseCache(object):
    """
    Abstract base class for all file-based cache implementations.

    Example initialization and storage:

        c = AutonameowCache('mycache')
        c.set('mydata', {'a': 1, 'b': 2})

    This will cache the data in memory by storing in a class instance dict,
    and also write the data to disk using the path:

        "CACHE_DIR_ABSPATH/mycache_mydata"

    Example retrieval:

        cached_data = c.get('mydata')
        assert cached_data == {'a': 1, 'b': 2}

    The idea is to keep many smaller files instead of a single shared file
    for possibly easier pruning of old date, file size limits, etc.

    Inheriting class must implement '_load' and '_dump' which does the actual
    serialization and reading/writing to disk.
    """
    CACHEFILE_PREFIX_SEPARATOR = '_'

    # TODO: [TD0101] Add ability to limit sizes of persistent storage/caches.
    #                Store timestamps with stored data and remove oldest
    #                entries when exceeding the file size limit.

    def __init__(self, cachefile_prefix, cache_dir_abspath=None):
        self._data = {}

        if not cache_dir_abspath:
            self.cachedir_abspath = get_config_cache_path()
        else:
            self.cachedir_abspath = cache_dir_abspath
        assert os.path.isabs(util.syspath(self.cachedir_abspath))
        self._dp = util.displayable_path(self.cachedir_abspath)

        _prefix = types.force_string(cachefile_prefix)
        if not _prefix.strip():
            raise ValueError(
                'Argument "cachefile_prefix" must be a valid string'
            )
        self.cachefile_prefix = _prefix

        if not self.has_cachedir():
            log.debug('Cache directory does not exist: "{!s}"'.format(self._dp))

            try:
                diskutils.makedirs(self.cachedir_abspath)
            except exceptions.FilesystemError as e:
                raise CacheError('Unable to create cache directory "{!s}": '
                                 '{!s}'.format(self._dp, e))
            else:
                log.info('Created cache directory: "{!s}"'.format(self._dp))

        if not self.has_cachedir_permissions():
            raise CacheError('Cache directory requires RWX-permissions: '
                             '"{!s}'.format(self._dp))

        log.debug('{!s} using cache directory "{!s}"'.format(self, self._dp))

    def has_cachedir_permissions(self):
        try:
            return diskutils.has_permissions(self.cachedir_abspath, 'rwx')
        except (TypeError, ValueError):
            return False

    def has_cachedir(self):
        _path = util.syspath(self.cachedir_abspath)
        try:
            return bool(os.path.exists(_path) and os.path.isdir(_path))
        except (OSError, ValueError, TypeError):
            return False

    def _cache_file_abspath(self, key):
        string_key = types.force_string(key)
        if not string_key.strip():
            raise KeyError('Invalid key: "{!s}" ({!s})'.format(key, type(key)))

        _basename = '{pre}{sep}{key}'.format(
            pre=self.cachefile_prefix,
            sep=self.CACHEFILE_PREFIX_SEPARATOR,
            key=key
        )
        _p = util.normpath(
            os.path.join(util.syspath(self.cachedir_abspath),
                         util.syspath(util.encode_(_basename)))
        )
        return _p

    def get(self, key):
        """
        Returns data from the cache.

        Args:
            key (str): The key of the data to retrieve.
                       Postfix of the cache file that is written to disk.

        Returns:
            Any cached data stored with the given key, as any serializable type.
        Raises:
            KeyError: The given 'key' is not a valid non-empty string,
                      or the key is not found in the cached data.
            CacheError: Failed to read cached data for some reason;
                        data corruption, encoding errors, missing files, etc..
        """
        if not key:
            raise KeyError

        if key not in self._data:
            _file_path = self._cache_file_abspath(key)
            if not os.path.exists(util.syspath(_file_path)):
                # Avoid displaying errors on first use.
                raise KeyError

            try:
                value = self._load(_file_path)
                self._data[key] = value
            except ValueError as e:
                _dp = util.displayable_path(_file_path)
                log.error(
                    'Error when reading key "{!s}" from cache file "{!s}" '
                    '(corrupt file?); {!s}'.format(key, _dp, e)
                )
                self.delete(key)
            except OSError as e:
                _dp = util.displayable_path(_file_path)
                log.warning(
                    'Error while trying to read key "{!s}" from cache file '
                    '"{!s}"; {!s}'.format(key, _dp, e)
                )
                raise KeyError
            except Exception as e:
                raise CacheError('Error while reading cache; {!s}'.format(e))

        return self._data.get(key)

    def set(self, key, value):
        """
        Stores data in the cache.

        Args:
            key (str): The key to store the data under.
                       Postfix of the cache file that is written to disk.
            value: The data to store, as any serializable type.
        """
        self._data[key] = value

        _file_path = self._cache_file_abspath(key)
        try:
            self._dump(value, _file_path)
        except OSError as e:
            _dp = util.displayable_path(_file_path)
            log.error(
                'Error while trying to write key "{!s}" with value "{!s}" to '
                'cache file "{!s}"; {!s}'.format(key, value, _dp, e)
            )

    def delete(self, key):
        try:
            del self._data[key]
        except KeyError:
            pass

        _p = self._cache_file_abspath(key)
        _dp = util.displayable_path(_p)
        log.debug('Deleting cache file "{!s}"'.format(_dp))
        try:
            diskutils.delete(_p, ignore_missing=True)
        except exceptions.FilesystemError as e:
            raise CacheError(
                'Error while deleting "{!s}"; {!s}'.format(_dp, e)
            )
        else:
            log.debug('Deleted cache file "{!s}"'.format(_dp))

    def has(self, key):
        # TODO: Test this ..
        if key in self._data:
            return True

        _file_path = self._cache_file_abspath(key)
        try:
            os.path.exists(_file_path)
        except OSError:
            return False
        else:
            return True

    def _load(self, file_path):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def _dump(self, value, file_path):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.cachefile_prefix)


class PickleCache(BaseCache):
    def _load(self, file_path):
        with open(util.syspath(file_path), 'rb') as fh:
            return pickle.load(fh, encoding='bytes')

    def _dump(self, value, file_path):
        with open(util.syspath(file_path), 'wb') as fh:
            pickle.dump(value, fh, pickle.HIGHEST_PROTOCOL)


def get_cache(cachefile_prefix):
    try:
        return PickleCache(cachefile_prefix)
    except CacheError as e:
        log.error('Cache unavailable :: {!s}'.format(e))
        return None


class CacheError(exceptions.AutonameowException):
    """Irrecoverable error while reading or writing to caches."""
