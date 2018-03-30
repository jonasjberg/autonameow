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
import time

from core import constants as C
from core.exceptions import AutonameowException
from core.persistence.base import (
    PersistenceError,
    PicklePersistence
)
from util import coercers


log = logging.getLogger(__name__)


class CacheError(AutonameowException):
    """Irrecoverable error while reading or writing to caches."""


def _get_persistence_backend(file_prefix, persistence_dir_abspath):
    # NOTE: Passing 'persistence_dir_abspath' only to simplify unit testing.
    try:
        return PicklePersistence(file_prefix,
                                 persistence_dir_abspath)
    except PersistenceError as e:
        raise CacheError(e)


class BaseCache(object):
    """
    General-purpose cache that behaves like a dict named "owner" that is
    stored both in RAM and on disk, using some method of persistence.

    Each instance of this class is passed a "owner", which could be an
    Extractor or any type of string-like identifier.
    The cache adds timestamps to the data for later pruning by creation time.

    Example usage:

        c = BaseCache(owner='gibson')
        c.set('data-key', {'a': 1, 'b': 2})

    This will cache the data in both RAM as well as to disk using some method
    of persistent data storage.  The data is written to disk using the path:

        "CACHE_DIR_ABSPATH/cache_gibson"
         ^_______________^ ^   ^ ^____^
          Cache directory  |___|  Stringified "owner"
                           Prefix used by all caches

    Data is retrieved by:

        _cached_data = c.get('data-key')

    """
    CACHE_PERSISTENCE_FILE_PREFIX = 'cache'

    def __init__(self, owner, cache_dir_abspath=None, max_filesize=None):
        self._owner = None
        self.owner = owner

        self._persistence = _get_persistence_backend(
            file_prefix=self.CACHE_PERSISTENCE_FILE_PREFIX,
            persistence_dir_abspath=cache_dir_abspath
        )

        if max_filesize is None:
            self.max_filesize = C.DEFAULT_CACHE_MAX_FILESIZE
        else:
            assert isinstance(max_filesize, int) and max_filesize > 0, (
                'Expected argument "max_filesize" to be a positive integer. '
                'Got ({!s}) "{!s}"'.format(type(max_filesize), max_filesize)
            )
            self.max_filesize = max_filesize

        try:
            self._data = self._persistence.get(self.owner)
        except PersistenceError as e:
            raise CacheError(e)
        except KeyError:
            self._data = dict()

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        str_value = coercers.force_string(value)
        if not str_value.strip():
            raise CacheError(
                'Argument "owner" must be a valid, non-empty/whitespace string'
            )
        self._owner = str_value

    def get(self, key):
        """
        Returns data from the cache.

        Args:
            key (str): The key of the data to retrieve.

        Returns:
            Any cached data stored with the given key, as any serializable type.

        Raises:
            KeyError: The given 'key' is not a valid non-empty string,
                      or the key is not found in the cached data.
            CacheError: Failed to read cached data for some reason;
                        data corruption, encoding errors, missing files, etc..
        """
        if not self._data:
            return None

        _timestamped_data = self._data.get(key)
        if not _timestamped_data:
            return None

        _timestamp, _data = _timestamped_data
        return _data

    def set(self, key, value):
        """
        Stores data "value" using the given "key" in the cache.

        Args:
            key (str): The key to store the data under.
            value: The data to store, as any serializable type.
        """
        _timestamped_value = (self._get_timestamp(), value)
        self._data[key] = _timestamped_value

        self._enforce_max_filesize()
        try:
            self._persistence.set(self.owner, self._data)
        except PersistenceError as e:
            raise CacheError(e)

    def delete(self, key):
        try:
            self._data.pop(key)
        except KeyError:
            pass
        else:
            try:
                self._persistence.set(self.owner, self._data)
            except PersistenceError as e:
                raise CacheError(e)

    def keys(self):
        return list(self._data.keys())

    def flush(self):
        self._data = dict()
        try:
            self._persistence.delete(self.owner)
        except PersistenceError as e:
            raise CacheError(e)

    @staticmethod
    def _get_timestamp():
        return int(time.time())

    def filesize(self):
        return self._persistence.filesize(self.owner)

    def _enforce_max_filesize(self):
        # TODO: [TD0144] Avoid enforcing cache file size too frequently.
        size = self.filesize()
        if size >= self.max_filesize:
            log.debug('Cache filesize {!s} bytes exceeds {!s} '
                      'byte limit'.format(size, self.max_filesize))
            self._prune_oldest()

            size = self.filesize()
            log.debug('Cache filesize {!s} bytes after prune'.format(size))

    def _prune_oldest(self):
        """
        Removes half of all cached items, favouring recent items.
        """
        # 'data_items' will be a list of nested tuples:
        # [(key1, (timestamp1, data1)), (key2, (timestamp2, data2))]
        data_items = list(self._data.items())
        sorted_by_timestamp = sorted(data_items, key=lambda x: x[1][0])

        number_data_items = len(data_items)
        number_items_to_remove = number_data_items // 2
        # Pop the last (oldest) 'number_items_to_remove' number of items.
        for key, _ in sorted_by_timestamp[:number_items_to_remove]:
            self._data.pop(key)

        log.debug('Cache pruned {!s} oldest items (was {!s} total)'.format(
            number_items_to_remove, number_data_items
        ))


def get_cache(owner, max_filesize=None):
    try:
        return BaseCache(owner, max_filesize=max_filesize)
    except (CacheError, PersistenceError) as e:
        log.error('Failed to get cache for owner {!s} :: {!s}'.format(owner, e))
        return None
