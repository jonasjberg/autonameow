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

import extractors
from core import (
    extraction,
    exceptions
)
from core.extraction import Extraction
import unit_utils as uu


def dummy_collect_data(file_object, label, data):
    pass


def dummy_request_data(file_object, label):
    pass


class TestExtraction(TestCase):
    def setUp(self):
        self.e = Extraction(uu.get_mock_fileobject(), dummy_collect_data)
        self.sources = ['text.py', 'metadata.py']

    def test_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_initial_results_data_len_is_zero(self):
        self.skipTest('TODO: Fix or remove result count tally.')
        self.assertEqual(len(self.e.data), 0)

    def test_raises_exception_For_invalid_results(self):
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.e.collect_results(None, 'image/jpeg')
            self.e.collect_results(1, 'image/jpeg')
            self.e.collect_results(False, 'image/jpeg')

    def test_collects_valid_results(self):
        self.e.collect_results('contents.mime_type', 'image/jpeg')

    def test_collecting_valid_results_increments_data_len(self):
        self.skipTest('TODO: Fix or remove result count tally.')
        self.e.collect_results('contents.mime_type', 'image/jpeg')
        self.assertEqual(len(self.e.data), 1)
        self.e.collect_results('filesystem.basename.extension', 'jpg')
        self.assertEqual(len(self.e.data), 2)

    def test_collecting_results_with_empty_data_does_not_increment_len(self):
        self.skipTest('TODO: Fix or remove result count tally.')
        self.e.collect_results('contents.mime_type', None)
        self.assertEqual(len(self.e.data), 0)
        self.e.collect_results('filesystem.basename.extension', None)
        self.assertEqual(len(self.e.data), 0)

    def test_has_method__instantiate_extractors(self):
        self.assertIsNotNone(self.e._instantiate_extractors)

    def test__instantiate_extractors_returns_expected_type(self):
        extractor_classes = extractors.get_extractor_classes(self.sources)
        actual = self.e._instantiate_extractors(extractor_classes)

        self.assertTrue(isinstance(actual, list))
        for ec in actual:
            self.assertTrue(uu.is_class_instance(ec))
            self.assertTrue(issubclass(ec.__class__, extractors.BaseExtractor))

    def test_has_method__execute_run_queue(self):
        self.assertIsNotNone(self.e._execute_run_queue)


class _DummyExtractor(object):
    is_slow = False


class _DummySlowExtractor(object):
    is_slow = True


class TestKeepSlowExtractorsIfRequiredWithSlowExtractor(TestCase):
    def setUp(self):
        self.fast = _DummyExtractor
        self.slow = _DummySlowExtractor

        self.input = [self.fast, self.fast, self.slow]

    def test_keep_slow_extractors_if_required_is_defined(self):
        self.assertIsNotNone(extraction.keep_slow_extractors_if_required)

    def test_slow_extractor_are_excluded_if_not_required(self):
        actual = extraction.keep_slow_extractors_if_required(self.input, [])

        self.assertNotIn(self.slow, actual,
                         'Slow extractor class should be excluded')
        self.assertNotEqual(len(self.input), len(actual),
                            'Expect one less extractor class in the output')

    def test_slow_extractor_are_included_if_required(self):
        required = [self.slow]
        actual = extraction.keep_slow_extractors_if_required(self.input,
                                                             required)
        self.assertIn(self.slow, actual,
                      'Slow extractor class is kept when required')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')


class TestKeepSlowExtractorsIfRequired(TestCase):
    def setUp(self):
        self.fast = _DummyExtractor
        self.slow = _DummySlowExtractor

        self.input = [self.fast, self.fast, self.fast]

    def test_keep_slow_extractors_if_required_is_defined(self):
        self.assertIsNotNone(extraction.keep_slow_extractors_if_required)

    def test_slow_extractor_are_excluded_if_not_required(self):
        actual = extraction.keep_slow_extractors_if_required(self.input, [])

        self.assertNotIn(self.slow, actual,
                         'Slow extractor class should be excluded')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')

    def test_slow_extractor_are_included_if_required(self):
        required = [self.slow]
        actual = extraction.keep_slow_extractors_if_required(self.input,
                                                             required)
        self.assertNotIn(self.slow, actual,
                         'There was no slow extractor class to start with')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')
