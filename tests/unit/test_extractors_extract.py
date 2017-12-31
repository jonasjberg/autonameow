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
from unittest.mock import (
    MagicMock,
    patch
)

import unit.utils as uu
from core import constants as C
from extractors import extract


class TestStandaloneExtract(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = [uu.abspath_testfile('magic_txt.txt')]
        cls.input_fileobject = uu.fileobject_testfile('magic_txt.txt')

    def test_exits_with_exit_success_if_not_given_any_input_paths(self):
        with self.assertRaises(SystemExit) as e:
            extract.main()
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)

    @patch('extractors.extract.logs', MagicMock())
    def test_exits_with_exit_success_if_not_specifying_actions(self):
        _options = {'input_paths': self.input_paths}
        with self.assertRaises(SystemExit) as e:
            extract.main(_options)
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)

    @patch('extractors.extract.logs', MagicMock())
    @patch('extractors.extract.do_extract_text')
    def test_extract_text(self, mock_do_extract_text):
        _options = {'input_paths': self.input_paths,
                    'extract_text': True}
        extract.main(_options)
        mock_do_extract_text.assert_called_once_with(self.input_fileobject)

    @patch('extractors.extract.logs', MagicMock())
    @patch('extractors.extract.do_extract_metadata')
    def test_extract_metadata(self, mock_do_extract_metadata):
        _options = {'input_paths': self.input_paths,
                    'extract_metadata': True}
        extract.main(_options)
        mock_do_extract_metadata.assert_called_once_with(self.input_fileobject)

    @patch('extractors.extract.logs', MagicMock())
    @patch('extractors.extract.do_extract_text')
    @patch('extractors.extract.do_extract_metadata')
    def test_extract_text_and_metadata(self, mock_do_extract_metadata,
                                       mock_do_extract_text):
        _options = {'input_paths': self.input_paths,
                    'extract_metadata': True,
                    'extract_text': True}
        extract.main(_options)
        mock_do_extract_metadata.assert_called_once_with(self.input_fileobject)
        mock_do_extract_text.assert_called_once_with(self.input_fileobject)
