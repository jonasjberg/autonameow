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
import time

from core import types
from core.exceptions import AutonameowException
from core.persistence.base import (
    PersistenceError,
    PicklePersistence
)


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

    # TODO: [TD0101] Add ability to limit sizes of persistent storage/caches.
    #                Store timestamps with stored data and remove oldest
    #                entries when exceeding the file size limit.

    def __init__(self, owner, cache_dir_abspath=None):
        self._owner = None

        self._persistence = _get_persistence_backend(
            file_prefix=self.CACHE_PERSISTENCE_FILE_PREFIX,
            persistence_dir_abspath=cache_dir_abspath
        )

        self.owner = owner

        try:
            self._data = self._persistence.get(self.owner)
        except PersistenceError as e:
            raise CacheError(e)
        except KeyError:
            self._data = {}

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        _owner = types.force_string(value)
        if not _owner.strip():
            raise ValueError(
                'Argument "owner" must be a valid, non-empty/whitespace string'
            )
        self._owner = _owner

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
        _timestamped_value = (self.get_timestamp(), value)
        self._data[key] = _timestamped_value

        self._persistence.set(self.owner, self._data)

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
        self._data = {}
        try:
            self._persistence.delete(self.owner)
        except PersistenceError as e:
            raise CacheError(e)

    def get_timestamp(self):
        return int(time.time())


def get_cache(owner):
    try:
        return BaseCache(owner)
    except PersistenceError as e:
        log.error('Cache unavailable :: {!s}'.format(e))
        return None
