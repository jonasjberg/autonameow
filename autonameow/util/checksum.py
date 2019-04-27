# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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


def hashlib_digest(filepath, algorithm=None, maxbytes=None):
    if algorithm is None:
        algorithm = 'sha256'

    assert algorithm in AVAILABLE_ALGORITHMS, (
        'Argument "algorithm" must be one of "AVAILABLE_ALGORITHMS"'
    )

    _hashlib_attribute = getattr(hashlib, algorithm, None)
    assert _hashlib_attribute, (
        'Unable to get hashlib attribute for the given "algorithm"'
    )

    if maxbytes is not None:
        assert isinstance(maxbytes, int) and maxbytes > 0, (
            'Argument "maxbytes" must be a positive integer or None'
        )
    _num_bytes_read_limit = maxbytes

    hasher = _hashlib_attribute()
    _num_bytes_read = 0
    try:
        with open(filepath, 'rb', buffering=0) as fh:
            for b in iter(lambda: fh.read(CHUNK_SIZE), b''):
                if _num_bytes_read_limit:
                    _num_bytes_read += len(b)
                    if _num_bytes_read >= _num_bytes_read_limit:
                        break

                hasher.update(b)

            return hasher.hexdigest()

    except (OSError, TypeError) as e:
        raise exceptions.FilesystemError(e)


def sha256digest(filepath):
    return hashlib_digest(filepath, algorithm='sha256')


def sha1digest(filepath):
    return hashlib_digest(filepath, algorithm='sha1')


def md5digest(filepath):
    return hashlib_digest(filepath, algorithm='md5')


def partial_sha256digest(filepath):
    return hashlib_digest(filepath, algorithm='sha256', maxbytes=PARTIAL_SIZE)


def partial_sha1digest(filepath):
    return hashlib_digest(filepath, algorithm='sha1', maxbytes=PARTIAL_SIZE)


def partial_md5digest(filepath):
    return hashlib_digest(filepath, algorithm='md5', maxbytes=PARTIAL_SIZE)
