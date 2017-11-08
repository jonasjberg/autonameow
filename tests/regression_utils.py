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

import logging
import os
import re

from core import constants as C
from core import (
    disk,
    exceptions,
    types,
    util
)
import unit_utils as uu
import unit_utils_constants as uuconst


log = logging.getLogger(__name__)


class RegressionTestError(exceptions.AutonameowException):
    """Error caused by an invalid regression test."""


def read_plaintext_file(file_path):
    try:
        with open(file_path, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            contents = fh.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        raise RegressionTestError(e)
    else:
        return contents


class RegressionTestLoader(object):
    BASENAME_DESCRIPTION = b'description'
    BASENAME_SKIP = b'skip'
    BASENAME_YAML_CONFIG = b'config.yaml'
    BASENAME_YAML_OPTIONS = b'options.yaml'
    BASENAME_YAML_ASSERTS = b'asserts.yaml'

    def __init__(self, abspath):
        assert type(abspath) == bytes
        self.abspath = abspath
        self.skiptest = False

    def _get_test_setup_dict_from_files(self):
        _abspath_desc = self._joinpath(self.BASENAME_DESCRIPTION)
        _description = read_plaintext_file(_abspath_desc)

        _abspath_opts = self._joinpath(self.BASENAME_YAML_OPTIONS)
        try:
            _options = disk.load_yaml_file(_abspath_opts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError(e)

        _options = self._set_testfile_path(_options)
        _options = self._set_config_path(_options)

        _abspath_asserts = self._joinpath(self.BASENAME_YAML_ASSERTS)
        try:
            _asserts = disk.load_yaml_file(_abspath_asserts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError(e)

        _abspath_skip = self._joinpath(self.BASENAME_SKIP)
        if uu.file_exists(_abspath_skip):
            _skiptest = True
        else:
            _skiptest = False

        return {
            'asserts': _asserts,
            'description': _description.strip(),
            'options': _options,
            'skiptest': _skiptest
        }

    @staticmethod
    def _set_testfile_path(options):
        """
        Replaces '$TESTFILES' with the full absolute path to the 'test_files'
        directory.
        For instance; '$TESTFILES/foo.txt' --> '$SRCROOT/test_files/foo.txt',
        where '$SRCROOT' is the full absolute path to the autonameow sources.
        """
        if 'input_paths' not in options:
            return options

        _fixed_paths = []
        for path in options['input_paths']:
            if path == '$TESTFILES':
                # Substitute "variable".
                _abspath = uuconst.TEST_FILES_DIR
            elif path.startswith('$TESTFILES/'):
                # Substitute "variable".
                _basename = path.replace('$TESTFILES/', '')
                _abspath = uu.abspath_testfile(_basename)
            else:
                # Normalize path.
                try:
                    _abspath_bytes = types.AW_PATH.normalize(path)
                except types.AWTypeError as e:
                    raise RegressionTestError('Invalid path in "input_paths":'
                                              '"{!s}" :: {!s}'.format(path, e))
                else:
                    # NOTE(jonas): Iffy ad-hoc string coercion..
                    _abspath = types.force_string(_abspath_bytes)

            # Allow non-existent but not empty paths.
            if not _abspath.strip():
                raise RegressionTestError(
                    'Path is empty after processing: "{!s}"'.format(path)
                )
            _fixed_paths.append(_abspath)

        options['input_paths'] = _fixed_paths
        return options

    def _set_config_path(self, options):
        """
        Modifies the 'config_path' entry in the options dict.

        If the 'config_path' entry..

          * .. is missing, the path of the default (unit test) config is used.

               --> 'config_path': (Path to the default config)

          * .. starts with '$TESTFILES/', the full absolute path to the
               'test_files' directory is inserted in place of '$TESTFILES/'.

                   'config_path': '$TESTFILES/config.yaml'
               --> 'config_path': '$SRCROOT/test_files/config.yaml'

          * .. starts with '$THISTEST/', the full absolute path to the current
               regression test directory is inserted in place of '$THISTEST/'.

                   'config_path': '$THISTEST/config.yaml'
               --> 'config_path': 'self.abspath/config.yaml'
        """
        _options = dict(options)

        _path = types.force_string(_options.get('config_path'))
        if not _path:
            # Use default config.
            _abspath = uu.abspath_testfile(
                uuconst.DEFAULT_YAML_CONFIG_BASENAME
            )
        elif _path.startswith('$TESTFILES/'):
            # Substitute "variable".
            _basename = _path.replace('$TESTFILES/', '').strip()
            _abspath = uu.abspath_testfile(_basename)
        elif _path.startswith('$THISTEST/'):
            # Substitute "variable".
            _basename = _path.replace('$THISTEST/', '').strip()
            try:
                _bytes_basename = types.AW_PATHCOMPONENT(_basename)
            except types.AWTypeError as e:
                raise RegressionTestError(e)
            _abspath = self._joinpath(_bytes_basename)
        else:
            # Assume absolute path.
            _abspath = _path

        if not uu.file_exists(_abspath):
            raise RegressionTestError(
                'Invalid "config_path": "{!s}"'.format(_path)
            )

        log.debug('Set config_path "{!s}" to "{!s}"'.format(_path, _abspath))
        _options['config_path'] = util.enc.normpath(_abspath)
        return _options

    def _joinpath(self, leaf):
        assert type(leaf) == bytes
        return os.path.join(
            util.enc.syspath(self.abspath), util.enc.syspath(leaf)
        )

    def load(self):
        _setup_dict = self._get_test_setup_dict_from_files()
        _setup_dict['test_abspath'] = self.abspath
        _setup_dict['test_dirname'] = os.path.basename(
            util.enc.syspath(self.abspath)
        )
        return _setup_dict


class AutonameowWrapper(object):
    """
    Autonameow class wrapper used by the regression tests.

    Wraps an instance of the 'Autonameow' class and overrides ("monkey-patches")
    some of its methods in order to capture data needed to evaluate the tests.
    """
    def __init__(self, opts=None):
        if opts:
            assert isinstance(opts, dict)
            self.opts = opts
        else:
            self.opts = {}

        self.captured_exitcode = None
        self.captured_stderr = None
        self.captured_stdout = None
        self.captured_renames = dict()
        self.captured_runtime_secs = None

    def mock_exit_program(self, exitcode):
        self.captured_exitcode = exitcode

    def mock_do_rename(self, from_path, new_basename, dry_run=True):
        # NOTE(jonas): Iffy ad-hoc string coercion..
        _from_basename = types.force_string(disk.file_basename(from_path))

        # Check for collisions that might cause erroneous test results.
        if _from_basename in self.captured_renames:
            _existing_new_basename = self.captured_renames[_from_basename]
            raise RegressionTestError(
                'Already captured rename: "{!s}" -> "{!s}" (Now "{!s}")'.format(
                    _from_basename, _existing_new_basename, new_basename
                )
            )
        self.captured_renames[_from_basename] = new_basename

    def __call__(self):
        from core.autonameow import Autonameow
        Autonameow.exit_program = self.mock_exit_program
        Autonameow.do_rename = self.mock_do_rename

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            with Autonameow(self.opts) as ameow:
                ameow.run()
                self.captured_runtime_secs = ameow.runtime_seconds

        self.captured_stdout = stdout.getvalue()
        self.captured_stderr = stderr.getvalue()


REGRESSIONTESTS_ROOT_ABSPATH = None


def get_regressiontests_rootdir():
    global REGRESSIONTESTS_ROOT_ABSPATH
    if not REGRESSIONTESTS_ROOT_ABSPATH:
        _rootdir = os.path.join(
            C.AUTONAMEOW_SRCROOT_DIR, 'tests', 'regression'
        )
        REGRESSIONTESTS_ROOT_ABSPATH = util.enc.normpath(_rootdir)

    assert disk.isdir(REGRESSIONTESTS_ROOT_ABSPATH)
    return REGRESSIONTESTS_ROOT_ABSPATH


def regtest_abspath(basename):
    _root = get_regressiontests_rootdir()
    try:
        _abspath = os.path.join(
            util.enc.syspath(_root),
            util.enc.syspath(basename)
        )
        _normalized_abspath = util.enc.normpath(_abspath)
    except Exception:
        raise AssertionError

    assert disk.isdir(_normalized_abspath)
    return _normalized_abspath


RE_REGRESSIONTEST_DIRNAME = re.compile(rb'\d{4}(_[\w]+)?')


def get_regressiontest_dirs():
    _tests_root_dir = get_regressiontests_rootdir()
    _dirs = [
        regtest_abspath(d)
        for d in os.listdir(_tests_root_dir)
        if RE_REGRESSIONTEST_DIRNAME.match(d)
    ]

    return _dirs


def load_regressiontests():
    out = []

    _paths = get_regressiontest_dirs()
    for p in _paths:
        try:
            loaded_test = RegressionTestLoader(p).load()
        except RegressionTestError as e:
            print('Unable to load test case :: ' + str(e))
        else:
            out.append(loaded_test)

    return out


def check_renames(actual, expected):
    if not isinstance(actual, dict):
        raise RegressionTestError('Expected argument "actual" of type dict')
    if not isinstance(expected, dict):
        raise RegressionTestError('Expected argument "expected" of type dict')

    if not actual and not expected:
        # Did not expect anything and nothing happened.
        return True
    elif actual and not expected:
        # Something unexpected happened.
        return False
    elif expected and not actual:
        # Expected something to happened but it didn't.
        return False

    return bool(expected == actual)
