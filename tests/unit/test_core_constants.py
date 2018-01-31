# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

import unit.utils as uu
from core import constants as C


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

    def test_program_exit_codes(self):
        self._is_defined_type(int, C.EXIT_SUCCESS)
        self._is_defined_type(int, C.EXIT_WARNING)
        self._is_defined_type(int, C.EXIT_SANITYFAIL)
        self._is_defined_type(int, C.EXIT_ERROR)

    def test_default_rule_ranking_bias(self):
        self._is_defined_type(float, C.DEFAULT_RULE_RANKING_BIAS)

    def test_default_file_tags_options(self):
        self._is_defined_internal_string(
            C.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR
        )
        self._is_defined_internal_string(
            C.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR
        )

    def test_default_postprocessing_options(self):
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_SANITIZE_FILENAME)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_SANITIZE_STRICT)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_LOWERCASE_FILENAME)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_UPPERCASE_FILENAME)
        self._is_defined_type(bool, C.DEFAULT_POSTPROCESS_SIMPLIFY_UNICODE)

    def test_python_version_string(self):
        self._is_defined_internal_string(C.STRING_PYTHON_VERSION)

    def test_analysis_results_fields(self):
        self._is_defined_type(list, C.ANALYSIS_RESULTS_FIELDS)

    def test_default_persistence_path(self):
        self._is_defined_absolute_path(C.DEFAULT_PERSISTENCE_DIR_ABSPATH)

    def test_default_history_path(self):
        self._is_defined_type(bytes, C.DEFAULT_HISTORY_FILE_BASENAME)
        self._is_defined_absolute_path(C.DEFAULT_HISTORY_FILE_ABSPATH)

    def test_default_cache_max_filesize(self):
        self._is_defined_type(int, C.DEFAULT_CACHE_MAX_FILESIZE)

    def test_default_datetime_formats(self):
        self._is_defined_internal_string(C.DEFAULT_DATETIME_FORMAT_DATETIME)
        self._is_defined_internal_string(C.DEFAULT_DATETIME_FORMAT_DATE)
        self._is_defined_internal_string(C.DEFAULT_DATETIME_FORMAT_TIME)

    def test_default_filesystem_ignores(self):
        self._is_defined_type(frozenset, C.DEFAULT_FILESYSTEM_IGNORE)
        self._is_defined_type(frozenset, C.DEFAULT_FILESYSTEM_IGNORE_VCS)
        self._is_defined_type(frozenset, C.DEFAULT_FILESYSTEM_IGNORE_DARWIN)
        self._is_defined_type(frozenset, C.DEFAULT_FILESYSTEM_IGNORE_LINUX)
        self._is_defined_type(frozenset, C.DEFAULT_FILESYSTEM_IGNORE_WINDOWS)

    def test_default_year_limits(self):
        from datetime import datetime
        self._is_defined_type(datetime, C.YEAR_UPPER_LIMIT)
        self._is_defined_type(datetime, C.YEAR_LOWER_LIMIT)

    def test_meowuri_constants(self):
        self._is_defined_internal_string(C.MEOWURI_NODE_GENERIC)
        self._is_defined_internal_string(C.UNDEFINED_MEOWURI_PART)
        self._is_defined_internal_string(C.MEOWURI_SEPARATOR)
        self._is_defined_internal_string(C.RE_ALLOWED_MEOWURI_PART_CHARS)
        self._is_defined_internal_string(C.MEOWURI_ROOT_SOURCE_ANALYZERS)
        self._is_defined_internal_string(C.MEOWURI_ROOT_SOURCE_EXTRACTORS)
        self._is_defined_internal_string(C.MEOWURI_ROOT_SOURCE_PLUGINS)
        self._is_defined_internal_string(C.MEOWURI_ROOT_GENERIC)

        self._is_defined_type(frozenset, C.MEOWURI_ROOTS_SOURCES)
        self._is_defined_type(frozenset, C.MEOWURI_ROOTS)

    def test_string_constants(self):
        self._is_defined_internal_string(C.STRING_PROGRAM_VERSION)
        self._is_defined_internal_string(C.STRING_PROGRAM_RELEASE_DATE)
        self._is_defined_internal_string(C.STRING_PROGRAM_NAME)
        self._is_defined_internal_string(C.STRING_AUTHOR_EMAIL)
        self._is_defined_internal_string(C.STRING_COPYRIGHT_NOTICE)
        self._is_defined_internal_string(C.STRING_URL_MAIN)
        self._is_defined_internal_string(C.STRING_URL_REPO)
