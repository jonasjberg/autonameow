# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import TestCase

import unit.utils as uu
from core.datastore.query import QueryResponseFailure


class TestQueryResponseFailure(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_fo = uu.get_mock_fileobject()
        cls.mock_uri = uu.get_meowuri()

    def test_evaluates_false(self):
        response = QueryResponseFailure()
        self.assertFalse(response)

    def test___str__without_any_args(self):
        response = QueryResponseFailure()
        actual = str(response)
        self.assertIsInstance(actual, str)

    def _check_str(self, response, expect_start, expect_end):
        actual = str(response)
        self.assertIsInstance(actual, str)
        # Ignore the middle part with the FileObject hash.
        self.assertTrue(
            actual.startswith(expect_start),
            '”{!s}" does not start with "{!s}"'.format(actual, expect_start)
        )
        self.assertTrue(
            actual.endswith(expect_end),
            '”{!s}" does not end with "{!s}"'.format(actual, expect_end)
        )

    def test___str__with_arg_fileobject(self):
        self._check_str(
            QueryResponseFailure(fileobject=self.mock_fo),
            expect_start='Failed query ',
            expect_end='->[unspecified MeowURI]'
        )

    def test___str__with_arg_uri(self):
        self._check_str(
            QueryResponseFailure(uri=self.mock_uri),
            expect_start='Failed query (Unknown FileObject',
            expect_end='->[{!s}]'.format(self.mock_uri)
        )

    def test___str__with_arg_msg(self):
        self._check_str(
            QueryResponseFailure(msg='foo Bar'),
            expect_start='Failed query (Unknown FileObject',
            expect_end='->[unspecified MeowURI] :: foo Bar'
        )

    def test___str__with_args_fileobject_uri(self):
        self._check_str(
            QueryResponseFailure(fileobject=self.mock_fo, uri=self.mock_uri),
            expect_start='Failed query ',
            expect_end='->[{!s}]'.format(self.mock_uri)
        )

    def test___str__with_args_fileobject_msg(self):
        self._check_str(
            QueryResponseFailure(fileobject=self.mock_fo, msg='foo Bar'),
            expect_start='Failed query ',
            expect_end='->[unspecified MeowURI] :: foo Bar'
        )

    def test___str__with_args_uri_msg(self):
        self._check_str(
            QueryResponseFailure(uri=self.mock_uri, msg='foo Bar'),
            expect_start='Failed query (Unknown FileObject',
            expect_end='->[{!s}] :: foo Bar'.format(self.mock_uri)
        )

    def _check_repr(self, response, expect_end):
        actual = repr(response)
        self.assertIsInstance(actual, str)
        # Ignore the part with the FileObject hash.
        self.assertTrue(
            actual.endswith(expect_end),
            '"{!s}" does not end with "{!s}"'.format(actual, expect_end)
        )

    def test___repr__with_arg_fileobject(self):
        self._check_repr(
            QueryResponseFailure(fileobject=self.mock_fo),
            expect_end='->[unspecified MeowURI]'
        )

    def test___repr__with_arg_uri(self):
        self._check_repr(
            QueryResponseFailure(uri=self.mock_uri),
            expect_end='->[{!s}]'.format(self.mock_uri)
        )

    def test___repr__with_arg_msg(self):
        self._check_repr(
            QueryResponseFailure(msg='foo Bar'),
            expect_end='->[unspecified MeowURI] :: foo Bar'
        )

    def test___repr__with_args_fileobject_uri(self):
        self._check_repr(
            QueryResponseFailure(fileobject=self.mock_fo, uri=self.mock_uri),
            expect_end='->[{!s}]'.format(self.mock_uri)
        )

    def test___repr__with_args_fileobject_msg(self):
        self._check_repr(
            QueryResponseFailure(fileobject=self.mock_fo, msg='foo Bar'),
            expect_end='->[unspecified MeowURI] :: foo Bar'
        )

    def test___repr__with_args_uri_msg(self):
        self._check_repr(
            QueryResponseFailure(uri=self.mock_uri, msg='foo Bar'),
            expect_end='->[{!s}] :: foo Bar'.format(self.mock_uri)
        )
