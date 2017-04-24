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

import os

from unittest import TestCase

from core.evaluate.matcher import RuleMatcher
from core.fileobject import FileObject
from core import config_defaults
from utils import abspath_testfile

RULES = config_defaults.rules


class TestRuleMatcher(TestCase):
    def setUp(self):
        pass

    def test_setup(self):
        pass

    def test_rule_matches_record_my_desktop(self):
        _file = abspath_testfile('recordmydesktop.ogv')
        self.assertTrue(os.path.isfile(_file))

        fo = FileObject(_file)
        self.assertIsNotNone(fo)

        rm = RuleMatcher(fo, RULES)
        self.assertEqual('record_my_desktop', rm._active_rule_key)

    def test_rule_matches_screencapture(self):
        _file = abspath_testfile('screencapture-github-com-jonasjberg-shell-scripts-blob-master-convert-video-to-mp4-1464459165038.png')
        fo = FileObject(_file)

        rm = RuleMatcher(fo, RULES)
        self.assertEqual('filetagsscreenshot', rm._active_rule_key)
