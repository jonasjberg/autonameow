# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from unittest import TestCase

from core.evaluate.matcher import RuleMatcher
from core.fileobject import FileObject
from core import config_defaults

RULES = config_defaults.rules


class TestRuleMatcher(TestCase):
    def setUp(self):
        pass

    def test_rule_matches_record_my_desktop(self):
        fo = FileObject('../test_files/recordmydesktop.ogv')
        rm = RuleMatcher(fo, RULES)
        self.assertEqual('record_my_desktop', rm._active_rule_key)

    def test_rule_matches_screencapture(self):
        fo = FileObject('../test_files/screencapture-github-com-jonasjberg-shell-scripts-blob-master-convert-video-to-mp4-1464459165038.png')
        rm = RuleMatcher(fo, RULES)
        self.assertEqual('screencapture', rm._active_rule_key)
