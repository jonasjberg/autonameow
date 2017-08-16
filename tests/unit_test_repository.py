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

from core.repository import Repository


class TestRepository(TestCase):
    def setUp(self):
        self.r = Repository()

    def test_setup(self):
        self.r.initialize()
        self.assertTrue(isinstance(self.r._query_string_source_map, dict))


class TestRepositoryMethodResolvable(TestCase):
    def setUp(self):
        self.r = Repository()
        self.r.initialize()

    def test_empty_query_string_returns_false(self):
        self.assertFalse(self.r.resolvable(None))
        self.assertFalse(self.r.resolvable(''))

    def test_bad_query_string_returns_false(self):
        self.assertFalse(self.r.resolvable('not.a.valid.source.surely'))

    def test_good_query_string_returns_true(self):
        self.assertTrue(self.r.resolvable('metadata.exiftool.PDF:CreateDate'))
        self.assertTrue(self.r.resolvable('metadata.exiftool'))

        # TODO: [TD0053] Fix special case of collecting data from 'FileObject'.
        # self.assertTrue(self.r.resolvable('filesystem.basename.full'))
        # self.assertTrue(self.r.resolvable('filesystem.basename.extension'))
        # self.assertTrue(self.r.resolvable('contents.mime_type'))
