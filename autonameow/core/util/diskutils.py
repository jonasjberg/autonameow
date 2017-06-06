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
import re
import itertools


# Needed by 'sanitize_filename' for sanitizing filenames in restricted mode.
ACCENT_CHARS = dict(zip('ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ',
                        itertools.chain('AAAAAA', ['AE'], 'CEEEEIIIIDNOOOOOOO', ['OE'], 'UUUUUYP', ['ss'],
                                        'aaaaaa', ['ae'], 'ceeeeiiiionooooooo', ['oe'], 'uuuuuypy')))


def sanitize_filename(s, restricted=False, is_id=False):
    """Sanitizes a string so it could be used as part of a filename.
    If restricted is set, use a stricter subset of allowed characters.
    Set is_id if this is not an arbitrary string, but an ID that should be kept
    if possible.

    NOTE:  This function was lifted as-is from the "youtube-dl" project.

           https://github.com/rg3/youtube-dl/blob/master/youtube_dl/utils.py
           Commit: b407d8533d3956a7c27ad42cbde9a877c36df72c
    """
    def replace_insane(char):
        if restricted and char in ACCENT_CHARS:
            return ACCENT_CHARS[char]
        if char == '?' or ord(char) < 32 or ord(char) == 127:
            return ''
        elif char == '"':
            return '' if restricted else '\''
        elif char == ':':
            return '_-' if restricted else ' -'
        elif char in '\\/|*<>':
            return '_'
        if restricted and (char in '!&\'()[]{}$;`^,#' or char.isspace()):
            return '_'
        if restricted and ord(char) > 127:
            return '_'
        return char

    # Handle timestamps
    s = re.sub(r'[0-9]+(?::[0-9]+)+', lambda m: m.group(0).replace(':', '_'), s)
    result = ''.join(map(replace_insane, s))
    if not is_id:
        while '__' in result:
            result = result.replace('__', '_')
        result = result.strip('_')
        # Common case of "Foreign band name - English song title"
        if restricted and result.startswith('-_'):
            result = result[2:]
        if result.startswith('-'):
            result = '_' + result[len('-'):]
        result = result.lstrip('.')
        if not result:
            result = '_'
    return result




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
