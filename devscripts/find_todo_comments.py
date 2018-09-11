#!/usr/bin/env python3

import logging
import os
import re
import sys

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

SELFNAME = str(os.path.basename(__file__))

LOG = logging.getLogger(SELFNAME)


def read_all_lines_from_file(filepath):
    with open(filepath, mode='r',
              encoding='utf8', errors='ignore') as fh:
        lines = fh.read()

    return lines


class FinderState:
    OUTSIDE = 'outside'
    INSIDE = 'inside'


def find_todo_comments_in_text(strng):
    assert isinstance(strng, str)

    results = list()
    todo_buffer = list()

    def _store_results_and_flush_buffer():
        if todo_buffer:
            results.append('\n'.join(todo_buffer))
        todo_buffer.clear()

    def _debug_log_state_change(state, linenumber):
        pass

    state = FinderState.OUTSIDE

    for linenumber, line in enumerate(strng.splitlines()):
        line = line.strip()

        if not line:
            if state == FinderState.INSIDE:
                _store_results_and_flush_buffer()

            state = FinderState.OUTSIDE
            continue

        if re.match(r'# TODO.*', line):
            if state == FinderState.INSIDE:
                # New block
                _store_results_and_flush_buffer()
                state = FinderState.INSIDE
            else:
                assert state == FinderState.OUTSIDE
                todo_buffer = [line]
                state = FinderState.INSIDE

        elif re.match('^#$', line) and state == FinderState.OUTSIDE:
            continue

        elif re.match('# .*', line):
            assert 'TODO' not in line
            todo_buffer.append(line)

        else:
            _store_results_and_flush_buffer()
            state = FinderState.OUTSIDE

    _store_results_and_flush_buffer()

    return results


def collect_python_files(filepaths):
    collected_files = set()

    for filepath in filepaths:
        if not filepath or not os.path.exists(filepath):
            continue

        fileabspath = os.path.realpath(filepath)
        if os.path.isfile(fileabspath) and fileabspath.endswith('.py'):
            fileabspath = os.path.realpath(fileabspath)
            collected_files.add(fileabspath)

        elif os.path.isdir(fileabspath):
            # TODO: Recurse directories if called with '-r'/'--recurse'.
            continue

    return collected_files


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog=SELFNAME,
        epilog='"{}" --- Finds multi-line comments with TOODOs.'.format(SELFNAME)
    )
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Enables verbose mode, prints additional information.'
    )
    parser.add_argument(
        dest='filepaths',
        metavar='FILEPATH',
        nargs='*',
        help='Path(s) to file(s) and/or directories of files to process. '
             'If the path is a directory, all files in the directory are '
             'included but any containing directories are not traversed. '
             'Use "--recurse" to enable recursive traversal. '
    )
    opts = parser.parse_args(sys.argv[1:])

    exit_status = EXIT_SUCCESS

    if not opts.filepaths:
        LOG.warning('No file path(s) specified..')
        sys.exit(exit_status)

    files_to_search = collect_python_files(opts.filepaths)
    for file_to_search in files_to_search:
        LOG.info('About to search "%s"', file_to_search)

        file_textlines = read_all_lines_from_file(file_to_search)
        todo_list = find_todo_comments_in_text(file_textlines)
        for todo in todo_list:
            print('\n' + todo)

    sys.exit(exit_status)
