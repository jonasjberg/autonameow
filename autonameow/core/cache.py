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

try:
    import cPickle as pickle
except ImportError:
    import pickle

from core.exceptions import CacheError
from core import (
    config,
    util,
    types
)
from core import constants as C


log = logging.getLogger(__name__)


# TODO: [TD0097] Add proper handling of cache directories.
DEFAULT_CACHE_DIRECTORY_ROOT = '/tmp'
DEFAULT_CACHE_DIRECTORY_LEAF = 'autonameow_cache'
assert DEFAULT_CACHE_DIRECTORY_ROOT not in ('', '/', None)
assert DEFAULT_CACHE_DIRECTORY_ROOT not in ('', None)

CACHE_DIR_ABSPATH = util.normpath(
    os.path.join(
        util.syspath(DEFAULT_CACHE_DIRECTORY_ROOT),
        util.syspath(DEFAULT_CACHE_DIRECTORY_LEAF)
    )
)


# TODO: [TD0012] Add some type of caching.


class BaseCache(object):
    CACHEFILE_PREFIX_SEPARATOR = '_'

    def __init__(self, cachefile_prefix):
        self._data = {}

        if not cachefile_prefix:
            raise ValueError('Missing required argument "cachefile_prefix"')
        else:
            self.cachefile_prefix = cachefile_prefix

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
            for x in (os.R_OK, os.W_OK, os.X_OK):
                if not os.access(util.syspath(CACHE_DIR_ABSPATH), x):
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
        if key not in self._data:
            if not key:
                raise KeyError

            _file_path = self._cache_file_abspath(key)
            try:
                value = self._load(_file_path)
                self._data[key] = value
            except ValueError as e:
                log.error(
                    'Error when trying to read "{!s}" from cache file "{!s}";'
                    ' {!s}'.format(key, util.displayable_path(_file_path), e)
                )
                self.delete(key)

        return self._data.get(key)

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
        with open(file_path, 'rb') as fh:
            return pickle.load(fh, encoding='bytes')

    def _dump(self, value, file_path):
        with open(file_path, 'wb') as fh:
            pickle.dump(value, fh, pickle.HIGHEST_PROTOCOL)
