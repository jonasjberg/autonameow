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

import analyzers
from core import analysis
import unit_utils as uu
import unit_utils_constants as uuconst


class TestAnalysis(TestCase):
    def setUp(self):
        uu.init_provider_registry()
        uu.init_session_repository()
        self.fo = uu.get_mock_fileobject()
        self.config = uu.get_default_config()

    def test_analysis_start_requires_fileobject_argument(self):
        for _bad_arg in [None, 'foo', object()]:
            with self.assertRaises(AssertionError):
                analysis.start(_bad_arg, self.config)

    def test_analysis_start_requires_config_argument(self):
        for _bad_arg in [None, 'foo', object()]:
            with self.assertRaises(AssertionError):
                analysis.start(self.fo, _bad_arg)

    def test__instantiate_analyzers_returns_expected_type(self):
        analyzer_classes = analyzers.get_analyzer_classes()
        actual = analysis._instantiate_analyzers(
            self.fo, analyzer_classes, self.config
        )

        self.assertTrue(isinstance(actual, list))
        for ac in actual:
            self.assertTrue(uu.is_class_instance(ac))
            self.assertTrue(issubclass(ac.__class__, analyzers.BaseAnalyzer))

    def test_collects_valid_results(self):
        analysis.collect_results(
            self.fo,
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            'image/jpeg'
        )


class TestAnalysisRunQueue(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.q = analysis.AnalysisRunQueue()

    def test_init(self):
        self.assertIsNotNone(self.q)

    def test_len_initial(self):
        self.assertEqual(len(self.q), 0)

    def test_len_after_enqueueing_analyzer(self):
        self.q.enqueue(uu.get_mock_analyzer())
        self.assertEqual(len(self.q), 1)
        self.q.enqueue(uu.get_mock_analyzer())
        self.assertEqual(len(self.q), 2)

    def test_enqueue_single_analyzer(self):
        ma = next(uu.get_mock_analyzer())
        self.q.enqueue(ma)

        for a in self.q:
            self.assertEqual(ma, a)

    def test_enqueue_multiple_analyzers(self):
        enqueued = []

        for ma in uu.get_mock_analyzer():
            enqueued.append(ma)
            self.q.enqueue(ma)

        for dequeued in self.q:
            self.assertTrue(dequeued in enqueued)
