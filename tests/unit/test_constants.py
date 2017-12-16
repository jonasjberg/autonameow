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
    def _is_defined_type(self, type_, test_input):
        self.assertIsNotNone(test_input)
        self.assertIsInstance(test_input, type_)

    def _is_defined_internal_string(self, test_input):
        self.assertIsNotNone(test_input)
        self.assertTrue(uu.is_internalstring(test_input))

    def _is_defined_absolute_path(self, test_input):
        self.assertIsNotNone(test_input)
        self.assertTrue(uu.is_internalbytestring(test_input))
        self.assertTrue(uu.is_abspath(test_input))

    def test_constants_contains_program_exit_codes(self):
        self._is_defined_type(int, C.EXIT_SUCCESS)
        self._is_defined_type(int, C.EXIT_WARNING)
        self._is_defined_type(int, C.EXIT_SANITYFAIL)
        self._is_defined_type(int, C.EXIT_ERROR)

    def test_constants_contains_default_rule_ranking_bias(self):
        self._is_defined_type(float, C.DEFAULT_RULE_RANKING_BIAS)

    def test_constants_contains_default_file_tags_options(self):
        self._is_defined_internal_string(
            C.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR
        )
        self._is_defined_internal_string(
            C.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR
        )

    def test_constants_contains_default_postprocessing_options(self):
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_SANITIZE_FILENAME)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_SANITIZE_STRICT)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_LOWERCASE_FILENAME)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_UPPERCASE_FILENAME)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_SIMPLIFY_UNICODE)

    def test_constants_contains_python_version(self):
        self._is_defined_internal_string(C.STRING_PYTHON_VERSION)

    def test_constants_contains_analysis_results_fields(self):
        self._is_defined_type(list, C.ANALYSIS_RESULTS_FIELDS)

    def test_default_cache_path(self):
        self._is_defined_absolute_path(C.DEFAULT_PERSISTENCE_DIR_ABSPATH)

    def test_default_history_path(self):
        self._is_defined_absolute_path(C.DEFAULT_HISTORY_FILE_ABSPATH)

    def test_default_cache_max_filesize(self):
        self._is_defined_type(int, C.DEFAULT_CACHE_MAX_FILESIZE)
