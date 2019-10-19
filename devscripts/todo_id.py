#!/usr/bin/env python3
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
SOURCEFILE_IGNORED = ['test_todo_id.py', 'test_generate_changelog.py']

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SELFNAME = str(os.path.basename(__file__))
_SELF_DIRPATH = os.path.abspath(os.path.dirname(__file__))
_SELF_DIRPATH_PARENT = os.path.normpath(os.path.join(_SELF_DIRPATH, os.pardir))

TODO_PATH = os.path.join(_SELF_DIRPATH_PARENT, TODO_BASENAME)
DONE_PATH = os.path.join(_SELF_DIRPATH_PARENT, DONE_BASENAME)


def is_readable_file(filepath):
    return os.path.isfile(filepath) and os.access(filepath, os.R_OK)


def get_source_files(paths):
    def _recurse(_path):
        matches = list()
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

    files = list()
    for path in paths:
        if not os.path.exists(path):
            continue
        files.extend(_recurse(path))
    return files


def find_todo_ids_in_line(strng):
    assert isinstance(strng, str)

    matches = list()
    if re.search(RE_TODO_IGNORED, strng):
        return matches

    for match in re.finditer(RE_TODO_IDENTIFIER, strng):
        todo_text = re.split(RE_TODO_IDENTIFIER, strng)[-1:][0]
        todo_text = todo_text.replace('`', '').strip()
        matches.append({
            'id': match.group(1),
            'text': todo_text,
        })
    return matches


class TodoPriority:
    UNKNOWN = None
    HIGH = 'High Priority'
    MEDIUM = 'Medium Priority'
    LOW = 'Low Priority'


def find_todo_ids_in_lines(lines):
    found_ids = list()

    if not lines:
        return found_ids

    current_priority_heading = TodoPriority.UNKNOWN

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line == 'High Priority':
            current_priority_heading = TodoPriority.HIGH
        elif line == 'Medium Priority':
            current_priority_heading = TodoPriority.MEDIUM
        elif line == 'Low Priority':
            current_priority_heading = TodoPriority.LOW
        elif 'Very Low Priority' in line:
            current_priority_heading = TodoPriority.LOW

        results = find_todo_ids_in_line(line)
        if not results:
            continue

        for result in results:
            result.update({'priority': current_priority_heading})

        found_ids.extend(results)

    return found_ids


def find_todo_ids_in_file(filepath):
    with open(filepath, 'r', encoding='utf8') as fh:
        file_contents = fh.readlines()

    return find_todo_ids_in_lines(file_contents)


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


def find_todo_id_priorities():
    todos = find_todo_ids_in_file(TODO_PATH)
    # unique_todo_ids = set(todo_id for todo_id in todos['id'])

    result = dict()
    for todo in todos:
        todo_id = todo['id']

        if todo_id in result:
            # Originally an assertion that kept failing due to references to
            # IDs with another priority in the text.
            # For now, just keep the highest seen priority.
            seen_todo_id_priority = result[todo_id]
            this_todo_id_priority = todo['priority']

            if seen_todo_id_priority is TodoPriority.HIGH:
                continue
            elif (seen_todo_id_priority is TodoPriority.MEDIUM
                  and this_todo_id_priority is TodoPriority.LOW):
                result[todo_id] = TodoPriority.MEDIUM
                continue

        result[todo_id] = todo['priority']

    return result


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


class TodoIdChecker(object):
    def __init__(self):
        self.ids_todolist = find_todo_ids_in_todo_file()
        self.ids_done = find_todo_ids_in_done_file()
        self.ids_in_sources = find_todo_ids_in_source_files()

        self.failure_messages = list()

    def check_todo_done_does_not_contain_same_id(self):
        ids_in_both_todolist_and_done = self.ids_todolist & self.ids_done
        if not ids_in_both_todolist_and_done:
            return True

        self.failure_messages.append('''
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

    def check_sources_does_not_contain_ids_not_in_todo(self):
        if self.ids_in_sources.issubset(self.ids_todolist):
            # All IDs in the sources are also in the TODO-list.
            return True

        ids_only_in_sources = sorted(
            [i for i in self.ids_in_sources if i not in self.ids_todolist]
        )
        self.failure_messages.append('''
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

    def check_sources_does_not_contain_ids_in_done(self):
        if not self.ids_in_sources.intersection(self.ids_done):
            # None of the IDs in the sources are in the DONE-list.
            return True

        ids_in_sources_and_done = sorted(
            [i for i in self.ids_in_sources if i in self.ids_done]
        )
        self.failure_messages.append('''
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

    def all_checks_passed(self):
        if not self.ids_in_sources:
            self.failure_messages.append(
                '[WARNING] Unable to find any IDs (!)'
            )

        ok = True
        ok &= self.check_todo_done_does_not_contain_same_id()
        ok &= self.check_sources_does_not_contain_ids_not_in_todo()
        ok &= self.check_sources_does_not_contain_ids_in_done()
        return ok


def list_orphaned():
    ids_in_sources = find_todo_ids_in_source_files()
    if not ids_in_sources:
        return

    ids_todolist = find_todo_ids_in_todo_file()
    ids_in_todo_but_not_sources = sorted(
        [i for i in ids_todolist if i not in ids_in_sources]
    )
    if ids_in_todo_but_not_sources:
        print('''
Found {} IDs in the TODO-list that are not in the sources:

{}
'''.format(len(ids_in_todo_but_not_sources),
           '\n'.join([TODO_IDENTIFIER_FORMAT.format(int(i))
                      for i in ids_in_todo_but_not_sources])))


def list_todos_in_sources():
    """
    Prints TODOs in the source files, along with any text, the file path
    and priority, sorted by the IDs.
    """
    files_todos = find_todos_in_source_files()
    if not files_todos:
        return

    todo_id_priorities = find_todo_id_priorities()

    result_lines = list()
    for filepath, todos in files_todos.items():
        for t in todos:
            t_id = t['id']
            t_priority = todo_id_priorities.get(t_id)
            result_lines.append((filepath, t_id, t['text'], t_priority))

    common_path_prefix = os.path.commonprefix([p for p, _, _, _ in result_lines])

    cf = ColumnFormatter()
    for line in sorted(result_lines, key=lambda x: x[1]):
        filepath, todo_id, text, priority = line
        short_filepath = filepath.split(common_path_prefix)[1]
        cf.addrow(todo_id, priority, short_filepath, text)

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
        checker = TodoIdChecker()
        if not checker.all_checks_passed():
            for message in checker.failure_messages:
                print(message)
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
