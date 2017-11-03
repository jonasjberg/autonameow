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
import sys

'''
Utility script for getting the next free (unused) TODO-list entry identifier.
'''

TODO_BASENAME = 'TODO.md'
DONE_BASENAME = 'done.md'
TODO_IDENTIFIER_FORMAT = '[TD{:04d}]'
RE_TODO_IDENTIFIER = re.compile(r'(?![Rr]e(lated|fers?)).*\[TD(\d{4})\]')
SOURCEFILE_EXTENSIONS = ['.py', '.sh']

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
AUTONAMEOW_SRC_ROOT = os.path.normpath(os.path.join(_THIS_DIR, os.pardir))

todo_path = os.path.join(AUTONAMEOW_SRC_ROOT, TODO_BASENAME)
done_path = os.path.join(AUTONAMEOW_SRC_ROOT, DONE_BASENAME)


def is_readable_file(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


for _path in (todo_path, done_path):
    if not is_readable_file(_path):
        sys.exit('File does not exist or is not readable: "{!s}"'.format(_path))


def get_source_files(paths):
    def _recurse(path):
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                try:
                    extension = os.path.splitext(filename)[1]
                except (IndexError, OSError):
                    continue
                else:
                    if extension in SOURCEFILE_EXTENSIONS:
                        matches.append(
                            os.path.realpath(os.path.join(root, filename))
                        )
        return matches

    files = []
    for path in paths:
        if not os.path.exists(path):
            continue
        files.extend(_recurse(path))
    return files


def find_todo_ids_in_file(file_path):
    _found_ids = set()
    for line in open(file_path, 'r', encoding='utf8'):
        for match in re.finditer(RE_TODO_IDENTIFIER, line):
            _found_ids.add(match.group(2))
    return _found_ids


def get_next_todo_id():
    found_ids = set()
    found_ids.update(find_todo_ids_in_file(todo_path))
    found_ids.update(find_todo_ids_in_file(done_path))

    if found_ids:
        last_id = sorted(found_ids, reverse=True)[0]
        next_unused_id = TODO_IDENTIFIER_FORMAT.format(int(last_id) + 1)
        return next_unused_id
    else:
        return None


def check_todo_done_does_not_contain_same_id():
    ids_todolist = find_todo_ids_in_file(todo_path)
    ids_done = find_todo_ids_in_file(done_path)

    ids_in_both_todolist_and_done = ids_todolist & ids_done
    if not ids_in_both_todolist_and_done:
        return True

    print('''
FAILED Check #1
===============
Expected the TODO-list and the list of completed items
to contain only mutually exclusive identifiers.
Found {} IDs used in both the TODO-list and DONE-list:

{}
'''.format(len(ids_in_both_todolist_and_done),
           '\n'.join([TODO_IDENTIFIER_FORMAT.format(int(i))
                      for i in ids_in_both_todolist_and_done])))
    return False


def do_check():
    def check_sources_does_not_contain_ids_not_in_todo():
        ids_todolist = find_todo_ids_in_file(todo_path)
        if found_ids.issubset(ids_todolist):
            # All IDs in the sources are also in the TODO-list.
            return True

        ids_only_in_sources = [i for i in found_ids
                               if i not in ids_todolist]
        print('''
FAILED Check #2
===============
Expected the sources to only contain identifiers used in the
TODO-list.
Found {} IDs in the sources that are not in the TODO-list:

{}
'''.format(len(ids_only_in_sources),
           '\n'.join([TODO_IDENTIFIER_FORMAT.format(int(i))
                      for i in ids_only_in_sources])))
        return False

    def check_sources_does_not_contain_ids_in_done():
        ids_done = find_todo_ids_in_file(done_path)
        if not found_ids.intersection(ids_done):
            # None of the IDs in the sources are in the DONE-list.
            return True

        ids_in_sources_and_done = [i for i in found_ids if i in ids_done]
        print('''
FAILED Check #3
===============
Expected the sources to not contain any "completed" identifiers,
I.E. also contained in the DONE-list.
Found {} IDs used in both the sources and the DONE-list:

{}
'''.format(len(ids_in_sources_and_done),
           '\n'.join([TODO_IDENTIFIER_FORMAT.format(int(i))
                      for i in ids_in_sources_and_done])))
        return False

    _source_files = get_source_files([AUTONAMEOW_SRC_ROOT])
    found_ids = set()
    for _file in _source_files:
        found_ids.update(find_todo_ids_in_file(_file))

    if not found_ids:
        print('[WARNING] Unable to find any IDs (!)')
        return False

    ok = True
    ok &= check_todo_done_does_not_contain_same_id()
    ok &= check_sources_does_not_contain_ids_not_in_todo()
    ok &= check_sources_does_not_contain_ids_in_done()
    return ok


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='autonameow TODO-tool',
        epilog='Utility for managing TODO-list item identifiers '
               'used in the autonameow sources.'
    )
    parser.add_argument(
        '-n', '--next',
        dest='do_get_next_todo_id',
        action='store_true',
        default=True,
        help='[DEFAULT] Print the next free (unused) TODO-list entry '
             'identifier.'
    )
    parser.add_argument(
        '-c', '--check',
        dest='do_check',
        action='store_true',
        default=False,
        help='Checks that the sources does not contain completed TODO-list '
             'entries or entries that are not in the TODO-list. And also that '
             'entry IDs in the TODO- and DONE-list are mutually exclusive. '
             'Exits silently with status code 0 if all checks pass.'
    )

    exit_status = EXIT_SUCCESS

    opts = parser.parse_args(sys.argv[1:])
    if opts.do_check:
        _checks_pass = do_check()
        if not _checks_pass:
            exit_status &= EXIT_FAILURE

    elif opts.do_get_next_todo_id:
        _next_id = get_next_todo_id()
        if not _next_id:
            print(_next_id)
        else:
            exit_status &= EXIT_FAILURE

    sys.exit(exit_status)
