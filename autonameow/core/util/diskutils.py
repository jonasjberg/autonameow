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

import os

MAGIC_TYPE_LOOKUP = {'bmp':   ['image/x-ms-bmp'],
                     'gif':   ['image/gif'],
                     'jpg':   ['image/jpeg'],
                     'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'pdf':   ['application/pdf'],
                     'png':   ['image/png'],
                     'txt':   ['text/plain'],
                     'empty': ['inode/x-empty']}


def split_filename(file_path):
    """
    Split file name of the file located in "file_path" into two components;
    "name" and "suffix/extension".
    :param file_path: path to the file to split
    :return: tuple of the file "name" and "extension/suffix"
    """
    base, ext = os.path.splitext(os.path.basename(file_path))

    # Split "base" twice to make compound suffix out of the two extensions.
    if ext.lower() in ['.bz2', '.gz', '.lz', '.lzma', '.lzo', '.xz', '.z']:
        ext = os.path.splitext(base)[1] + ext
        base = os.path.splitext(base)[0]

    ext = ext.lstrip('.')
    if ext and ext.strip():
        return base, ext
    else:
        return base, None


def file_suffix(file_path, make_lowercase=True):
    """
    Get file suffix/extension for the file located in "file_path".
    Handles some special cases, for instance "basename.tar.gz" returns
    the suffix "tar.gz" and not just the extension "gz".
    :param file_path: path to the file from which to get extension.
    :param make_lowercase: make the extension lowercase, defaults to True
    :return: the file suffix/extension if found, else None
    """
    _, ext = split_filename(file_path)

    if ext and make_lowercase:
        ext = ext.lower()

    return ext


def file_base(file_path):
    """
    Get file basename without extension/suffix for the file located in
    "file_path".
    :param file_path: path to the file from which to get extension.
    :return: the file basename without extension if not empty, else None
    """
    base, _ = split_filename(file_path)
    return base if base else None
