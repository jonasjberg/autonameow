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

from core import constants as C
from core import (
    config,
    disk,
    exceptions,
    util
)
from core.util import enc
import unit_utils as uu


class RegressionTestError(exceptions.AutonameowException):
    """Error caused by an invalid regression test."""


# TODO: [TD0117] Implement automated regression tests


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
    BASENAME_YAML_CONFIG = b'config.yaml'
    BASENAME_YAML_OPTIONS = b'options.yaml'
    BASENAME_YAML_ASSERTS = b'asserts.yaml'

    def __init__(self, abspath):
        self.abspath = abspath

    def _get_test_setup_dict_from_file(self):
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

        return {
            'description': _description.strip(),
            'options': _options,
            'asserts': _asserts
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
            _testfile_basename = path.replace('$TESTFILES/', '')
            _testfile_abspath = uu.abspath_testfile(_testfile_basename)
            if not os.path.isfile(_testfile_abspath):
                raise RegressionTestError(
                    'Invalid path in "input_paths": "{!s}"'.format(path)
                )
            _fixed_paths.append(_testfile_abspath)

        options['input_paths'] = _fixed_paths
        return options

    @staticmethod
    def _set_config_path(options):
        _config_path = options.get('config_path')
        if not _config_path or not _config_path.startswith('$TESTFILES/'):
            return options

        _config_basename = _config_path.replace('$TESTFILES/', '')
        _config_abspath = uu.abspath_testfile(_config_basename)
        if not os.path.isfile(_config_abspath):
            raise RegressionTestError(
                'Invalid "config_path": "{!s}"'.format(_config_path)
            )

        options['config_path'] = enc.normpath(_config_abspath)
        return options

    def _joinpath(self, leaf):
        return os.path.join(enc.syspath(self.abspath), enc.syspath(leaf))

    def load(self):
        _setup_dict = self._get_test_setup_dict_from_file()
        return _setup_dict


REGRESSIONTESTS_ROOT_ABSPATH = None


def get_regressiontests_rootdir():
    global REGRESSIONTESTS_ROOT_ABSPATH
    if not REGRESSIONTESTS_ROOT_ABSPATH:
        _rootdir = os.path.join(
            C.AUTONAMEOW_SRCROOT_DIR, 'test_files', 'regression'
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
