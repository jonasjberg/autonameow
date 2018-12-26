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

import logging
import os

from core.persistence import get_persistence
from util import coercers


_this_dir = os.path.abspath(os.path.dirname(__file__))
PERSISTENCE_DIR_ABSPATH = coercers.coerce_to_normalized_path(_this_dir)
PERSISTENCE_BASENAME_PREFIX = '.regressionrunner'


log = logging.getLogger('regression_runner')


def _get_persistence(file_prefix=PERSISTENCE_BASENAME_PREFIX,
                     persistence_dir_abspath=PERSISTENCE_DIR_ABSPATH):
    persistence_mechanism = get_persistence(file_prefix, persistence_dir_abspath)
    if not persistence_mechanism:
        log.critical('Unable to retrieve any mechanism for persistent storage')
    return persistence_mechanism


def write_captured_runtime(testsuite, runtime):
    assert isinstance(runtime, float)

    persistent_storage = _get_persistence()
    if not persistent_storage:
        return

    try:
        captured_runtimes = persistent_storage.get('captured_runtimes')
    except KeyError:
        captured_runtimes = dict()

    assert isinstance(captured_runtimes, dict)
    captured_runtimes[testsuite] = runtime
    persistent_storage.set('captured_runtimes', captured_runtimes)


def load_captured_runtime(testsuite):
    persistent_storage = _get_persistence()
    if persistent_storage:
        try:
            captured_runtimes = persistent_storage.get('captured_runtimes')
        except KeyError:
            pass
        else:
            if captured_runtimes:
                assert isinstance(captured_runtimes, dict)
                return captured_runtimes.get(testsuite)

    return None


def load_run_results_history():
    persistent_storage = _get_persistence()
    if persistent_storage:
        try:
            run_results = persistent_storage.get('history')
        except KeyError:
            pass
        else:
            if run_results:
                assert isinstance(run_results, list)
                return run_results

    return list()


def write_run_results_history(run_results, max_entry_count=59):
    assert isinstance(max_entry_count, int)

    run_results_history = load_run_results_history()
    assert isinstance(run_results_history, list)

    run_results_history.insert(0, run_results)
    run_results_history = run_results_history[:max_entry_count]

    persistent_storage = _get_persistence()
    if persistent_storage:
        persistent_storage.set('history', run_results_history)


def write_failed_testsuites(testsuites):
    persistent_storage = _get_persistence()
    if persistent_storage:
        persistent_storage.set('lastrun', {'failed': list(testsuites)})


def load_failed_testsuites():
    persistent_storage = _get_persistence()
    if persistent_storage:
        try:
            lastrun = persistent_storage.get('lastrun')
        except KeyError:
            pass
        else:
            if lastrun:
                assert isinstance(lastrun, dict)
                testsuites_failed_last_run = lastrun.get('failed', list())
                assert isinstance(testsuites_failed_last_run, list)
                return testsuites_failed_last_run

    return list()
