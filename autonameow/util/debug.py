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


def print_callstack_names(stack_size=100):
    """
    Decorator that prints the call stack leading up to the decorated functions,
    going back max 'stack_size' items.

    Modified version of this:  https://stackoverflow.com/a/31796710
    """
    def wrapper(fn):
        def inner(*args, **kwargs):
            stack = inspect.stack()

            stack_index_min = 1
            stack_index_max = min(stack_size, len(stack))
            modules = [
                (index, inspect.getmodule(stack[index][0]))
                for index in reversed(range(stack_index_min, stack_index_max))
            ]

            module_name_lengths = [len(module.__name__)
                                   for _, module in modules]
            s = '{index:>5} : {module:^%i} : {name}' % (max(module_name_lengths) + 4)
            callers = [
                '',
                s.format(index='level', module='module', name='name'),
                '-' * 50
            ]

            for index, module in modules:
                callers.append(s.format(
                    index=index,
                    module=module.__name__,
                    name=stack[index][3]
                ))

            callers.append(s.format(
                index=0,
                module=fn.__module__,
                name=fn.__name__
            ))
            callers.append('')
            print('\n'.join(callers))

            return fn(*args, **kwargs)
        return inner
    return wrapper
