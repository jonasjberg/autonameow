# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import inspect
from collections import namedtuple


CallstackEntry = namedtuple('CallstackEntry', ('index', 'module', 'name'))


def _default_formatter(callstack_entries):
    max_module_name_length = max(len(callstack_entry.module)
                                 for callstack_entry in callstack_entries)
    fmt = '{index:>5} : {module:^%i} : {name}' % (max_module_name_length + 4)
    text_lines = [
        '',
        fmt.format(index='LEVEL', module='MODULE', name='NAME'),
        '-' * 50
    ]
    for index, module, name in callstack_entries:
        text_lines.append(fmt.format(
            index=index,
            module=module,
            name=name,
        ))

    text_lines.append('')
    return '\n'.join(text_lines)


def _tmp_file_writer():
    # NOTE(jonas): [hack] Resource-leak! File descriptor is never closed.
    fh = open('/tmp/callstack_names.txt', 'w', encoding='utf8')

    def _writelines(t):
        fh.writelines(t)

    return _writelines


def collect_callstack_info(results_list=None, formatter=_default_formatter,
                           printer=None, stack_size=100):
    """
    Decorator to collect call stack information leading up to the decorated
    callable, going back at most 'stack_size' items.

    Nothing is returned! Results are stored in the given 'results_list'.

    EXAMPLE USAGE --- Collecting results to a list:

        from util.debug import collect_callstack_info

        results_list = list()

        @collect_callstack_info(results_list)
        def foo(x):
            return x

        for result in results_list:
            print(result)

    EXAMPLE USAGE --- Printing results to stdout:

        from util.debug import collect_callstack_info

        @collect_callstack_info(list(), printer=print)
        def foo(x):
            return x

    Args:
        results_list (list): Results will be appended to this list.
        formatter (callable): Optional callable that accepts a list of
                              'CallstackEntry' and returns a Unicode string.
        printer: Optional callable that accepts a Unicode string.
                 Simply 'print' to print the formatted results to stdout or
                 maybe '_tmp_file_writer()' to write to a file.
                 Set to None to disable.
        stack_size (int): Maximum number of stack frames to traverse; backwards
                          up the call chain, from the decorated callable.
    """
    if results_list is None:
        results_list = list()
    assert isinstance(results_list, list)
    assert callable(formatter)
    assert stack_size > 0
    assert printer is None or callable(printer)

    def wrapper(fn):
        def inner(*args, **kwargs):
            stack = inspect.stack()

            stack_index_min = 1
            stack_index_max = min(stack_size, len(stack))

            modules = [
                (index, inspect.getmodule(stack[index][0]))
                for index in reversed(range(stack_index_min, stack_index_max))
            ]
            for index, module in modules:
                results_list.append(CallstackEntry(
                    index=index,
                    module=module.__name__,
                    name=stack[index][3]
                ))

            results_list.append(CallstackEntry(
                index=0,
                module=fn.__module__,
                name=fn.__name__
            ))

            if printer is not None:
                formatted_text = formatter(results_list)
                printer(formatted_text)

            return fn(*args, **kwargs)
        return inner

    return wrapper
