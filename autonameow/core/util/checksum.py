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

import hashlib


AVAILABLE_ALGORITHMS = hashlib.algorithms_guaranteed


KIBIBYTE = 1024
CHUNK_SIZE = 128 * KIBIBYTE


def hashlib_digest(file_path, algorithm=None):
    def _bad_algorithm():
        raise ValueError(
            '"algorithm" must be one of {!s}'.format(AVAILABLE_ALGORITHMS)
        )

    if algorithm is None:
        algorithm = 'sha256'

    if not algorithm in AVAILABLE_ALGORITHMS:
        _bad_algorithm()

    _hash_function = getattr(hashlib, algorithm, None)
    if not _hash_function:
        _bad_algorithm()

    hasher = _hash_function()
    try:
        with open(file_path, 'rb', buffering=0) as fh:
            for b in iter(lambda: fh.read(CHUNK_SIZE), b''):
                hasher.update(b)
            return hasher.hexdigest()
    except IOError as e:
        raise e


def sha256digest(file_path):
    return hashlib_digest(file_path, algorithm='sha256')


def sha1digest(file_path):
    return hashlib_digest(file_path, algorithm='sha1')


def md5digest(file_path):
    return hashlib_digest(file_path, algorithm='md5')
