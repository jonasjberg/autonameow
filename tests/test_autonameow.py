# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from unittest import TestCase

from core.autonameow import Autonameow


class TestAutonameow(TestCase):
    def setUp(self):
        self.autonameow = Autonameow('')

    def test_setup(self):
        self.assertIsNotNone(self.autonameow)

    # def test__check_file(self):
    #     self.assertFalse(self.autonameow._check_file(self, 'dummy'))
