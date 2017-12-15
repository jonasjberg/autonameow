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

from unittest import TestCase

from core import constants as C
import unit.utils as uu


class TestConstants(TestCase):
    def test_constants_contains_program_exit_codes(self):
        def _assert_defined_and_int(test_input):
            self.assertIsNotNone(test_input)
            self.assertIsInstance(test_input, int)

        _assert_defined_and_int(C.EXIT_SUCCESS)
        _assert_defined_and_int(C.EXIT_WARNING)
        _assert_defined_and_int(C.EXIT_SANITYFAIL)
        _assert_defined_and_int(C.EXIT_ERROR)

    def test_constants_contains_default_rule_ranking_bias(self):
        self.assertIsNotNone(C.DEFAULT_RULE_RANKING_BIAS)
        self.assertTrue(isinstance(C.DEFAULT_RULE_RANKING_BIAS, float))

    def test_constants_contains_default_file_tags_options(self):
        self.assertIsNotNone(C.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR)
        self.assertTrue(
            uu.is_internalstring(C.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR)
        )
        self.assertIsNotNone(C.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR)
        self.assertTrue(
            uu.is_internalstring(C.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR)
        )

    def test_constants_contains_default_postprocessing_options(self):
        def _assert_defined_and_bool(test_input):
            self.assertIsNotNone(test_input)
            self.assertIsInstance(test_input, bool)

        _assert_defined_and_bool(C.DEFAULT_POSTPROCESS_SANITIZE_FILENAME)
        _assert_defined_and_bool(C.DEFAULT_POSTPROCESS_SANITIZE_STRICT)
        _assert_defined_and_bool(C.DEFAULT_POSTPROCESS_LOWERCASE_FILENAME)
        _assert_defined_and_bool(C.DEFAULT_POSTPROCESS_UPPERCASE_FILENAME)

    def test_constants_contains_python_version(self):
        self.assertIsNotNone(C.STRING_PYTHON_VERSION)
        self.assertTrue(uu.is_internalstring(C.STRING_PYTHON_VERSION))

    def test_constants_contains_analysis_results_fields(self):
        self.assertIsNotNone(C.ANALYSIS_RESULTS_FIELDS)
        self.assertTrue(isinstance(C.ANALYSIS_RESULTS_FIELDS, list))

    def test_default_cache_path(self):
        p = C.DEFAULT_PERSISTENCE_DIR_ABSPATH
        self.assertTrue(uu.is_internalbytestring(p))
        self.assertTrue(uu.is_abspath(p))
        self.assertFalse(uu.file_exists(p))

    def test_default_history_path(self):
        p = C.DEFAULT_HISTORY_FILE_ABSPATH
        self.assertTrue(uu.is_internalbytestring(p))
        self.assertTrue(uu.is_abspath(p))
        self.assertFalse(uu.dir_exists(p))
