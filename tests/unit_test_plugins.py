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

import plugins
import unit_utils as uu


class TestFindPluginSourceFiles(TestCase):
    def setUp(self):
        pass

    def test_find_plugin_files_is_defined(self):
        self.assertIsNotNone(plugins.find_plugin_files)

    def test_find_plugin_files_returns_expected_type(self):
        actual = plugins.find_plugin_files()
        self.assertTrue(isinstance(actual, list))

    def test_find_plugin_files_returns_expected_files(self):
        actual = plugins.find_plugin_files()

        # TODO: [hardcoded] Likely to break; requires manual updates.
        self.assertIn('microsoft_vision.py', actual)
        self.assertNotIn('__init__.py', actual)


class TestGetPluginClasses(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.klasses = plugins.get_plugin_classes()

    def test_get_plugin_classes_returns_expected_type(self):
        self.assertTrue(isinstance(self.klasses, list))

    def test_get_plugin_classes_returns_class_objects(self):
        for klass in self.klasses:
            self.assertTrue(hasattr(klass, '__class__'))
            self.assertTrue(uu.is_class(klass))

    def test_get_plugin_classes_returns_subclasses_of_baseplugin(self):
        for klass in self.klasses:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, plugins.BasePlugin))

    def test_get_plugin_classes_does_not_include_abstract_classes(self):
        self.assertNotIn(plugins.BasePlugin, self.klasses)

