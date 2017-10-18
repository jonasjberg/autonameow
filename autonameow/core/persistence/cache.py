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

from core.exceptions import AutonameowException
from core.persistence.base import (
    PersistenceError,
    PicklePersistence
)


log = logging.getLogger(__name__)


class CacheError(AutonameowException):
    """Irrecoverable error while reading or writing to caches."""


# TODO: Possibly implement?
# class TextCache(PicklePersistence):
#     CACHE_KEY = 'text'
#
#     def __init__(self, file_prefix):
#         super(TextCache).__init__(file_prefix)
#
#         try:
#             self._cached_text = self.get(self.CACHE_KEY)
#         except (KeyError, PersistenceError):
#             self._cached_text = {}
#
#     def get_timestamp(self):
#         return int(time.time())
#
#     def save_text(self, fileobject, text):
#         self._cached_text.update({fileobject: text})
#         self._cache_write()
#
#     def load_text(self, fileobject):
#         if fileobject in self._cached_text:
#             _, _text = self._cached_text.get(fileobject)
#             return _text
#         return None


# TODO: Possibly implement?
# def get_text_cache(cachefile_prefix):
#     try:
#         return TextCache(cachefile_prefix)
#     except PersistenceError as e:
#         log.error('Cache unavailable :: {!s}'.format(e))
#         return None


class BaseCache(object):
    def __init__(self, owner):
        self._persistence = self._get_persistence_backend(file_prefix=owner)

    @staticmethod
    def _get_persistence_backend(file_prefix):
        try:
            return PicklePersistence(file_prefix)
        except PersistenceError as e:
            raise CacheError(e)

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
        if not key:
            raise KeyError

        try:
            return self._persistence.get(key)
        except PersistenceError as e:
            raise CacheError(e)

    def set(self, key, value):
        """
        Stores data "value" using the given "key" in the cache.

        Args:
            key (str): The key to store the data under.
            value: The data to store, as any serializable type.
        """
        self._persistence.set(key, value)


def get_cache(owner):
    try:
        return BaseCache(owner)
    except PersistenceError as e:
        log.error('Cache unavailable :: {!s}'.format(e))
        return None
