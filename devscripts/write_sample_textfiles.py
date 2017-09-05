#!/usr/bin/env python3
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

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
DEST_PATH = os.path.join(_THIS_DIR, 'sample_textfiles')


if not os.path.isdir(DEST_PATH):
    try:
        os.makedirs(DEST_PATH)
    except OSError as e:
        print('Unable to create destination directory; {!s}'.format(e))
        exit(1)


def write_alphanumeric_characters(out, codec, num_chars=512):
    for i in range(num_chars):
        try:
            uni_char = str(i)
            if uni_char.isalnum():
                bytes_ = uni_char.encode(codec)
                out.write(bytes_)
        except Exception as e:
            print('ERROR: {!s}'.format(e))
            pass
    out.write(b'\n')


CODECS = ['ascii', 'cp437', 'cp858', 'cp1252', 'iso-8859-1', 'macroman',
          'utf-8', 'utf-16']

for codec in CODECS:
    _dest_path = os.path.join(DEST_PATH, 'alnum_{}.txt'.format(codec))
    with open(_dest_path, 'wb') as fh:
        write_alphanumeric_characters(fh, codec, num_chars=512)

