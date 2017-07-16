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
import re

'''
Utility script for getting the next free (unused) TODO-list entry identifier.
'''

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
AUTONAMEOW_SRC_ROOT = os.path.normpath(os.path.join(_THIS_DIR, os.pardir))

TODO_BASENAME = 'TODO.md'
DONE_BASENAME = 'done.md'
RE_TODO_ID = re.compile(r'\[TD(\d{4})\]')


def find_todo_ids_in_file(file_path):
    for line in open(file_path, 'r', encoding='utf8'):
        for match in re.finditer(RE_TODO_ID, line):
            found_ids.add(match.group(1))


found_ids = set()

todo_path = os.path.join(AUTONAMEOW_SRC_ROOT, TODO_BASENAME)
done_path = os.path.join(AUTONAMEOW_SRC_ROOT, DONE_BASENAME)

find_todo_ids_in_file(todo_path)
find_todo_ids_in_file(done_path)

if found_ids:
    last_id = sorted(found_ids, reverse=True)[0]
    next_unused_id = '[TD{:04d}]'.format(int(last_id) + 1)

    print(next_unused_id)
