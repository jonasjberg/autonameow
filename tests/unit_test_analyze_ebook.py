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

import unittest

from analyzers import analyze_ebook

import unit_utils as uu

try:
    import isbnlib
except (ModuleNotFoundError, ImportError):
    isbnlib = None


def get_ebook_analyzer(file_object):
    return analyze_ebook.EbookAnalyzer(
        file_object,
        add_results_callback=uu.mock_add_results_callback,
        request_data_callback=uu.mock_request_data_callback
    )


@unittest.skipIf(isbnlib is None, 'Failed to import required module "isbnlib"')
class TestEbookAnalyzer(unittest.TestCase):
    def setUp(self):
        self.file_object = uu.get_named_file_object('2010-01-31_161251.jpg')
        self.analyzer = get_ebook_analyzer(self.file_object)

    def test_setup(self):
        self.assertIsNotNone(self.file_object)
        self.assertIsNotNone(self.analyzer)
