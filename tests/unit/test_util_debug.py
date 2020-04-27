# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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


def test_collect_callstack_info_to_results_list():
    from util.debug import collect_callstack_info

    results = list()
    stack_size = 3

    @collect_callstack_info(results_list=results, stack_size=stack_size)
    def _dummy_func_c(x):
        return x + 101

    def _dummy_func_b(x):
        return _dummy_func_c(x)

    def _dummy_func_a():
        return _dummy_func_b(565)

    _dummy_func_a()
    assert len(results) == stack_size

    assert results[0].index == 2
    assert results[0].module == 'unit.test_util_debug'
    assert results[0].name == '_dummy_func_a'
    assert results[1].index == 1
    assert results[1].module == 'unit.test_util_debug'
    assert results[1].name == '_dummy_func_b'
    assert results[2].index == 0
    assert results[2].module == 'unit.test_util_debug'
    assert results[2].name == '_dummy_func_c'


def test_collect_callstack_info_with_printer():
    from util.debug import collect_callstack_info

    results = list()
    stack_size = 3
    printer_called_with = list()

    def _printer(s):
        printer_called_with.append(s)

    @collect_callstack_info(results, printer=_printer, stack_size=stack_size)
    def _dummy_func_c(x):
        return x + 101

    def _dummy_func_b(x):
        return _dummy_func_c(x)

    def _dummy_func_a():
        return _dummy_func_b(565)

    _dummy_func_a()

    assert len(printer_called_with) == 1
    assert printer_called_with[0] == """
LEVEL :          MODULE          : NAME
--------------------------------------------------
    2 :   unit.test_util_debug   : _dummy_func_a
    1 :   unit.test_util_debug   : _dummy_func_b
    0 :   unit.test_util_debug   : _dummy_func_c
"""
