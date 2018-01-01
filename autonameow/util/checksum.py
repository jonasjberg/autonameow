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

import hashlib

from core import exceptions

__all__ = [
    'sha256digest', 'sha1digest', 'md5digest', 'partial_sha256digest',
    'partial_sha1digest', 'partial_md5digest'
]


AVAILABLE_ALGORITHMS = getattr(hashlib, 'algorithms_guaranteed', set())
KIBIBYTE = 1024
CHUNK_SIZE = 128 * KIBIBYTE
PARTIAL_SIZE = 10 * KIBIBYTE**2  # ~10MB


def hashlib_digest(file_path, algorithm=None, maxbytes=None):
    def _bad_algorithm():
        raise ValueError(
            '"algorithm" must be one of {!s}'.format(AVAILABLE_ALGORITHMS)
        )

    if algorithm is None:
        algorithm = 'sha256'

    if algorithm not in AVAILABLE_ALGORITHMS:
        _bad_algorithm()

    _hash_function = getattr(hashlib, algorithm, None)
    if not _hash_function:
        _bad_algorithm()

    if maxbytes is not None:
        _msg_bad_maxbytes = 'Expected "maxbytes" to be a positive integer'
        if not isinstance(maxbytes, int):
            raise TypeError(_msg_bad_maxbytes)
        if maxbytes <= 0:
            raise ValueError(_msg_bad_maxbytes)
    _maxbytes = maxbytes

    hasher = _hash_function()
    try:
        _bytesread = 0
        with open(file_path, 'rb', buffering=0) as fh:
            for b in iter(lambda: fh.read(CHUNK_SIZE), b''):
                if _maxbytes:
                    _bytesread += len(b)
                    if _bytesread >= _maxbytes:
                        break

                hasher.update(b)

            return hasher.hexdigest()

    except OSError as e:
        raise exceptions.FilesystemError(e)


def sha256digest(file_path):
    return hashlib_digest(file_path, algorithm='sha256')


def sha1digest(file_path):
    return hashlib_digest(file_path, algorithm='sha1')


def md5digest(file_path):
    return hashlib_digest(file_path, algorithm='md5')


def partial_sha256digest(file_path):
    return hashlib_digest(file_path, algorithm='sha256', maxbytes=PARTIAL_SIZE)


def partial_sha1digest(file_path):
    return hashlib_digest(file_path, algorithm='sha1', maxbytes=PARTIAL_SIZE)


def partial_md5digest(file_path):
    return hashlib_digest(file_path, algorithm='md5', maxbytes=PARTIAL_SIZE)
