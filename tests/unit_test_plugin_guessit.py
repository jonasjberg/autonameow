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

import unit_utils as uu
from plugins.guessit_plugin import GuessitPlugin


class TestGuessitPlugin(TestCase):
    def test_guessit_plugin_class_can_be_instantiated(self):
        plugin_instance = GuessitPlugin()
        self.assertIsNotNone(plugin_instance)

    def test_test_init_returns_true_if_guessit_is_available(self):
        plugin_instance = GuessitPlugin()

        guessit_available = uu.is_importable('guessit')
        if guessit_available:
            self.assertTrue(plugin_instance.test_init())
        else:
            self.assertFalse(plugin_instance.test_init())
