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
        self.assertIsNotNone(C.EXIT_ERROR)
        self.assertTrue(isinstance(C.EXIT_ERROR, int))
        self.assertIsNotNone(C.EXIT_WARNING)
        self.assertTrue(isinstance(C.EXIT_WARNING, int))
        self.assertIsNotNone(C.EXIT_SUCCESS)
        self.assertTrue(isinstance(C.EXIT_SUCCESS, int))

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

    def test_constants_contains_default_filesystem_options(self):
        self.assertIsNotNone(C.DEFAULT_FILESYSTEM_SANITIZE_FILENAME)
        self.assertTrue(
            isinstance(C.DEFAULT_FILESYSTEM_SANITIZE_FILENAME, bool)
        )
        self.assertIsNotNone(C.DEFAULT_FILESYSTEM_SANITIZE_STRICT)
        self.assertTrue(
            isinstance(C.DEFAULT_FILESYSTEM_SANITIZE_STRICT, bool)
        )

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
