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
from unittest.mock import Mock

from analyzers.analyze_filesystem import FilesystemAnalyzer
import unit_utils as uu


def get_filesystem_analyzer(fileobject):
    mock_config = Mock()

    return FilesystemAnalyzer(
        fileobject,
        mock_config,
        request_data_callback=uu.mock_request_data_callback
    )


class TestFilesystemAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        self.fo = uu.get_mock_fileobject('inode/x-empty')
        self.fsa = get_filesystem_analyzer(self.fo)

    def get_datetime_source(self, field_name):
        return filter(lambda dt: dt['source'] == field_name,
                      self.fsa.get_datetime())

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fsa)

    def test_get_title_raises_not_implemented_error(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.fsa.get_title())

    def test_get_author_raises_not_implemented_error(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.fsa.get_author())

    def test_get_tags_raises_not_implemented_error(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.fsa.get_tags())
