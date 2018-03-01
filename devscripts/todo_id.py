#!/usr/bin/env python3
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

import os
import re
import sys

# TODO: Ugly path hacks ..
SELF_ABSPATH = os.path.realpath(os.path.abspath(__file__))
PARENT_PATH = os.path.normpath(
    os.path.join(SELF_ABSPATH, os.path.pardir, os.path.pardir, 'autonameow')
)
sys.path.insert(0, PARENT_PATH)

from core.view import ColumnFormatter


'''
Helper utility for listing and verifying TODO-list item identifiers
used in the autonameow project.
'''

TODO_BASENAME = 'TODO.md'
DONE_BASENAME = 'done.md'
TODO_IDENTIFIER_FORMAT = '[TD{:04d}]'
RE_TODO_IDENTIFIER = re.compile(r'\[TD(\d{4})\]')
RE_TODO_IGNORED = re.compile(r'[Rr]e(lated|fers?)')
SOURCEFILE_EXTENSIONS = ['.py', '.sh']
SOURCEFILE_IGNORED = ['test_todo_id.py', 'test_update_changelog.py']

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SELFNAME = str(os.path.basename(__file__))
_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
AUTONAMEOW_SRC_ROOT = os.path.normpath(os.path.join(_THIS_DIR, os.pardir))

TODO_PATH = os.path.join(AUTONAMEOW_SRC_ROOT, TODO_BASENAME)
DONE_PATH = os.path.join(AUTONAMEOW_SRC_ROOT, DONE_BASENAME)


def is_readable_file(file_path):
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)


def get_source_files(paths):
    def _recurse(_path):
        matches = []
        for root, dirnames, filenames in os.walk(_path):
            for filename in filenames:
                if filename in SOURCEFILE_IGNORED:
                    continue

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


def find_todo_ids_in_line(string):
    matches = list()

    if re.search(RE_TODO_IGNORED, string):
        return matches

    for match in re.finditer(RE_TODO_IDENTIFIER, string):
        todo_text = re.split(RE_TODO_IDENTIFIER, string)[-1:][0]
        matches.append({'id': match.group(1),
                        'text': todo_text.strip()})
    return matches


def find_todo_ids_in_file(file_path):
    found_ids = list()
    for line in open(file_path, 'r', encoding='utf8'):
        found_ids.extend(find_todo_ids_in_line(line))
    return found_ids


def find_todo_ids_in_source_files():
    _source_files = get_source_files([AUTONAMEOW_SRC_ROOT])
    ids_in_sources = set()
    for _file in _source_files:
        todos = find_todo_ids_in_file(_file)
        for todo in todos:
            ids_in_sources.add(todo['id'])
    return ids_in_sources


def find_todos_in_source_files():
    _source_files = get_source_files([AUTONAMEOW_SRC_ROOT])
    file_todos = dict()
    for _file in _source_files:
        todos = find_todo_ids_in_file(_file)
        if todos:
            file_todos[_file] = todos
    return file_todos


def find_todo_ids_in_todo_file():
    todos = find_todo_ids_in_file(TODO_PATH)
    return {todo['id'] for todo in todos}


def find_todo_ids_in_done_file():
    todos = find_todo_ids_in_file(DONE_PATH)
    return {todo['id'] for todo in todos}


def get_next_todo_id():
    used_ids = set()
    used_ids.update(find_todo_ids_in_todo_file())
    used_ids.update(find_todo_ids_in_done_file())

    last_id = 0
    if used_ids:
        last_id = int(sorted(used_ids, reverse=True)[0])

    return TODO_IDENTIFIER_FORMAT.format(last_id + 1)


def do_all_checks():
    def check_todo_done_does_not_contain_same_id():
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

    def check_sources_does_not_contain_ids_not_in_todo():
        if ids_in_sources.issubset(ids_todolist):
            # All IDs in the sources are also in the TODO-list.
            return True

        ids_only_in_sources = sorted(
            [i for i in ids_in_sources if i not in ids_todolist]
        )
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
        if not ids_in_sources.intersection(ids_done):
            # None of the IDs in the sources are in the DONE-list.
            return True

        ids_in_sources_and_done = sorted(
            [i for i in ids_in_sources if i in ids_done]
        )
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

    ids_in_sources = find_todo_ids_in_source_files()
    if not ids_in_sources:
        print('[WARNING] Unable to find any IDs (!)')

    ids_todolist = find_todo_ids_in_todo_file()
    ids_done = find_todo_ids_in_done_file()

    ok = True
    ok &= check_todo_done_does_not_contain_same_id()
    ok &= check_sources_does_not_contain_ids_not_in_todo()
    ok &= check_sources_does_not_contain_ids_in_done()
    return ok


def list_orphaned():
    ids_in_sources = find_todo_ids_in_source_files()
    if not ids_in_sources:
        return

    ids_todolist = find_todo_ids_in_todo_file()
    ids_in_todo_but_not_sources = sorted(
        [i for i in ids_todolist if i not in ids_in_sources]
    )
    print('''
Found {} IDs in the TODO-list that are not in the sources:

{}
'''.format(len(ids_in_todo_but_not_sources),
           '\n'.join([TODO_IDENTIFIER_FORMAT.format(int(i))
                      for i in ids_in_todo_but_not_sources])))


def list_todos_in_sources():
    """
    Prints TODOs in the source files, along with any text and the file path,
    sorted by the id.
    """
    files_todos = find_todos_in_source_files()
    if not files_todos:
        return

    result_lines = list()
    for _filepath, _todos in files_todos.items():
        for t in _todos:
            result_lines.append((_filepath, t['id'], t['text']))

    _common_path_prefix = os.path.commonprefix([p for p, _, _ in result_lines])

    cf = ColumnFormatter()
    for line in sorted(result_lines, key=lambda x: x[1]):
        _filepath, _id, _text = line
        _short_filepath = _filepath.split(_common_path_prefix)[1]
        cf.addrow(_id, _short_filepath, _text)

    print(str(cf))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog=SELFNAME,
        epilog='"{}" -- Utility for listing and verifying TODO-list item '
               'identifiers used in the autonameow project.'.format(SELFNAME)
    )

    argument_group_actions = parser.add_mutually_exclusive_group()
    argument_group_actions.add_argument(
        '-n', '--next',
        dest='do_get_next_todo_id',
        action='store_true',
        default=True,
        help='Print the next free (unused) TODO-list entry '
             'identifier. (DEFAULT)'
    )
    argument_group_actions.add_argument(
        '-c', '--check',
        dest='do_check',
        action='store_true',
        default=False,
        help='Checks that the sources does not contain completed TODO-list '
             'entries or entries that are not in the TODO-list. And that '
             'IDs used in the TODO- and DONE-list are mutually exclusive. '
             'Exits silently with status code 0 if all checks pass.'
    )
    argument_group_actions.add_argument(
        '--orphaned',
        dest='do_list_orphaned',
        action='store_true',
        default=False,
        help='Print entries that are in the TODO-list but not in the sources.'
    )
    argument_group_actions.add_argument(
        '--list-in-sources',
        dest='do_list_todos_in_sources',
        action='store_true',
        default=False,
        help='Print TODOs in the sources along in columns with the id, '
             'file path and any TODO text, sorted by id.'
    )
    opts = parser.parse_args(sys.argv[1:])

    # Make sure that both the TODO-list and DONE-list exist.
    for _path in (TODO_PATH, DONE_PATH):
        if not is_readable_file(_path):
            m = 'File does not exist or is not readable: "{!s}"'.format(_path)
            print(m, file=sys.stderr)
            sys.exit(EXIT_FAILURE)

    exit_status = EXIT_SUCCESS
    if opts.do_check:
        _checks_pass = do_all_checks()
        if not _checks_pass:
            exit_status |= EXIT_FAILURE

    elif opts.do_list_orphaned:
        list_orphaned()

    elif opts.do_list_todos_in_sources:
        list_todos_in_sources()

    elif opts.do_get_next_todo_id:
        _next_id = get_next_todo_id()
        if _next_id:
            print(_next_id)
        else:
            exit_status |= EXIT_FAILURE

    sys.exit(exit_status)
