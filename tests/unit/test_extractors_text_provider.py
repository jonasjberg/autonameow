# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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
from extractors.text_provider import could_get_plain_text_from
from extractors.text_provider import get_plain_text


class TestTextProvider(TestCase):
    def _assert_could_get_plain_text_from(self, fileobject):
        actual = could_get_plain_text_from(fileobject)
        self.assertTrue(actual)

    def test_could_get_plain_text_from_file_with_mime_type_text_plain(self):
        f = uu.fileobject_from_samplefile('magic_txt.txt')
        self._assert_could_get_plain_text_from(f)

    def test_get_plain_text_from_plain_text_file_with_mime_type_text_plain(self):
        f = uu.fileobject_from_samplefile('magic_txt.txt')
        actual = get_plain_text(f)
        self.assertIsInstance(actual, str)

    def test_get_plain_text_from_file_with_mime_type_application_pdf(self):
        f = uu.fileobject_from_samplefile('magic_pdf.pdf')
        actual = get_plain_text(f)
        self.assertIsInstance(actual, str)
