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

from core import constants


class TestConstants(TestCase):
    def test_constants_contains_program_exit_codes(self):
        self.assertIsNotNone(constants.EXIT_ERROR)
        self.assertTrue(isinstance(constants.EXIT_ERROR, int))
        self.assertIsNotNone(constants.EXIT_WARNING)
        self.assertTrue(isinstance(constants.EXIT_WARNING, int))
        self.assertIsNotNone(constants.EXIT_SUCCESS)
        self.assertTrue(isinstance(constants.EXIT_SUCCESS, int))

    def test_constants_contains_default_file_mime_type(self):
        self.assertIsNotNone(constants.MAGIC_TYPE_UNKNOWN)
        self.assertTrue(isinstance(constants.MAGIC_TYPE_UNKNOWN, str))

    def test_constants_contains_list_of_valid_data_sources(self):
        self.assertIsNotNone(constants.VALID_DATA_SOURCES)
        self.assertTrue(isinstance(constants.VALID_DATA_SOURCES, list))

    def test_constants_contains_default_rule_ranking_bias(self):
        self.assertIsNotNone(constants.DEFAULT_RULE_RANKING_BIAS)
        self.assertTrue(isinstance(constants.DEFAULT_RULE_RANKING_BIAS, float))

    def test_constants_contains_default_file_tags_options(self):
        self.assertIsNotNone(constants.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR)
        self.assertTrue(
            isinstance(constants.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR, str)
        )
        self.assertIsNotNone(constants.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR)
        self.assertTrue(
            isinstance(constants.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR, str)
        )

    def test_constants_contains_default_filesystem_options(self):
        self.assertIsNotNone(constants.DEFAULT_FILESYSTEM_SANITIZE_FILENAME)
        self.assertTrue(
            isinstance(constants.DEFAULT_FILESYSTEM_SANITIZE_FILENAME, bool)
        )
        self.assertIsNotNone(constants.DEFAULT_FILESYSTEM_SANITIZE_STRICT)
        self.assertTrue(
            isinstance(constants.DEFAULT_FILESYSTEM_SANITIZE_STRICT, bool)
        )

    def test_constants_contains_python_version(self):
        self.assertIsNotNone(constants.PYTHON_VERSION)
        self.assertTrue(isinstance(constants.PYTHON_VERSION, str))

    def test_constants_contains_analysis_results_fields(self):
        self.assertIsNotNone(constants.ANALYSIS_RESULTS_FIELDS)
        self.assertTrue(isinstance(constants.ANALYSIS_RESULTS_FIELDS, list))

    def test_constants_contains_results_data_structure(self):
        self.assertIsNotNone(constants.RESULTS_DATA_STRUCTURE)
        self.assertTrue(isinstance(constants.RESULTS_DATA_STRUCTURE, dict))

    def test_constants_contains_legal_name_template_fields(self):
        self.assertIsNotNone(constants.NAME_TEMPLATE_FIELDS)
        self.assertTrue(isinstance(constants.NAME_TEMPLATE_FIELDS, list))
