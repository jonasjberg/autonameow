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
    # TODO: [TD0101] Add ability to limit sizes of persistent storage/caches.
    #                Store timestamps with stored data and remove oldest
    #                entries when exceeding the file size limit.

    def __init__(self, owner, cache_dir_abspath=None):
        self._persistence = _get_persistence_backend(
            file_prefix=owner,
            persistence_dir_abspath=cache_dir_abspath
        )

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
        try:
            _timestamp, _data = self._persistence.get(key)
        except PersistenceError as e:
            raise CacheError(e)
        else:
            return _data

    def set(self, key, value):
        """
        Stores data "value" using the given "key" in the cache.

        Args:
            key (str): The key to store the data under.
            value: The data to store, as any serializable type.
        """
        _timestamped_value = (self.get_timestamp(), value)
        self._persistence.set(key, _timestamped_value)

    def delete(self, key):
        try:
            self._persistence.delete(key)
        except PersistenceError as e:
            raise CacheError(e)

    def keys(self):
        return self._persistence.keys()

    def flush(self):
        self._persistence.flush()

    def get_timestamp(self):
        return int(time.time())


class FileobjectDataCache(BaseCache):
    def __init__(self, owner, key):
        super().__init__(owner)

        self._data = self.get(key)

    def store(self, key, data):
        _data = {self._fileobject: {key: data}}
        self._persistence.set(key)

    def retrieve(self, fileobject):
        for _timestamp, _data in self._cached_data:
            if fileobject in _data:
                return _data.get()
                return _text
        return None

    def update_persistent_data(self):
        self._persistence.set(self._cached_data)


def get_fileobject_data_cache(owner, fileobject):
    try:
        return FileobjectDataCache(owner, fileobject)
    except PersistenceError as e:
        log.error('Cache unavailable :: {!s}'.format(e))
        return None


def get_cache(owner):
    try:
        return BaseCache(owner)
    except PersistenceError as e:
        log.error('Cache unavailable :: {!s}'.format(e))
        return None
