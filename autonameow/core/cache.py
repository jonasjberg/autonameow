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
    util
)
from core import constants as C


log = logging.getLogger(__name__)


# TODO: [TD0097] Add proper handling of cache directories.
DEFAULT_CACHE_DIRECTORY_ROOT = '/Users/jonas/temp/'
DEFAULT_CACHE_DIRECTORY_LEAF = 'autonameow_cache'
assert DEFAULT_CACHE_DIRECTORY_ROOT not in ('', '/', None)
assert DEFAULT_CACHE_DIRECTORY_ROOT not in ('', None)

CACHE_DIR_ABSPATH = util.normpath(
    os.path.join(
        util.syspath(DEFAULT_CACHE_DIRECTORY_ROOT),
        util.syspath(DEFAULT_CACHE_DIRECTORY_LEAF)
    )
)


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

    def __init__(self, cachefile_prefix):
        self._data = {}

        _prefix = types.force_string(cachefile_prefix)
        if not _prefix.strip():
            raise ValueError(
                'Argument "cachefile_prefix" must be a valid string'
            )
        self.cachefile_prefix = _prefix

        if not os.path.exists(util.syspath(CACHE_DIR_ABSPATH)):
            raise CacheError(
                'Cache directory does not exist: "{!s}"'.format(
                    util.displayable_path(CACHE_DIR_ABSPATH)
                )
            )

            # TODO: [TD0097] Add proper handling of cache directories.
            # try:
            #     os.makedirs(util.syspath(self._cache_dir))
            # except OSError as e:
            #     raise CacheError(
            #         'Error while creating cache directory "{!s}": '
            #         '{!s}'.format(util.displayable_path(self._cache_dir), e)
            #     )
        else:
            if not diskutils.has_permissions(CACHE_DIR_ABSPATH, 'rwx'):
                raise CacheError(
                    'Cache directory path requires RWX-permissions: '
                    '"{!s}'.format(util.displayable_path(CACHE_DIR_ABSPATH))
                )
        log.debug('{!s} Using _cache_dir "{!s}'.format(
            self, util.displayable_path(CACHE_DIR_ABSPATH))
        )

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
            os.path.join(util.syspath(CACHE_DIR_ABSPATH),
                         util.syspath(util.encode_(_basename)))
        )
        return _p

    def get(self, key):
        if not key:
            raise KeyError

        if key not in self._data:
            _file_path = self._cache_file_abspath(key)
            _dp = util.displayable_path(_file_path)
            try:
                value = self._load(_file_path)
                self._data[key] = value
            except ValueError as e:
                log.error(
                    'Error when reading key "{!s}" from cache file "{!s}" '
                    '(corrupt file?); {!s}'.format(key, _dp, e)
                )
                self.delete(key)
            except OSError as e:
                log.error(
                    'Error while trying to read key "{!s}" from cache file '
                    '"{!s}"; {!s}'.format(key, _dp, e)
                )
                raise KeyError
            except Exception as e:
                raise CacheError('Error while reading cache; {!s}'.format(e))

        return self._data.get(key)

    def set(self, key, value):
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

        _dp = util.displayable_path(self._cache_file_abspath(key))
        try:
            log.critical('would have deleted "{!s}"'.format(_dp))
            # TODO: [TD0097] Double-check this and actually delete the file ..
            pass
        except OSError as e:
            raise CacheError(
                'Error when trying to delete "{!s}"; {!s}'.format(_dp, e)
            )

    def _load(self, file_path):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def _dump(self, value, file_path):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return self.__class__.__name__


class PickleCache(BaseCache):
    def _load(self, file_path):
        with open(util.syspath(file_path), 'rb') as fh:
            return pickle.load(fh, encoding='bytes')

    def _dump(self, value, file_path):
        with open(util.syspath(file_path), 'wb') as fh:
            pickle.dump(value, fh, pickle.HIGHEST_PROTOCOL)


def get_cache(cachefile_prefix):
    return PickleCache(cachefile_prefix)


class CacheError(exceptions.AutonameowException):
    """Irrecoverable error while reading or writing to caches."""
