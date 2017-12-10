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

import unit.utils as uu
from core.config.configuration import Configuration
from core.config.config_parser import ConfigurationParser
from core.config.default_config import DEFAULT_CONFIG


uu.init_provider_registry()
uu.init_session_repository()


class TestConfigurationParser(TestCase):
    def test_behaves_as_old_configuration(self):
        # TODO: Temporary test! Remove once configuration is refactored.
        old = Configuration(DEFAULT_CONFIG)

        parser = ConfigurationParser()
        new = parser.parse(DEFAULT_CONFIG)

        self.assertEqual(old.options, new.options)
        self.assertEqual(old.reusable_nametemplates, new.reusable_nametemplates)
        self.assertEqual(old.referenced_meowuris, new.referenced_meowuris)
        self.assertEqual(old.rules, new.rules)
        self.assertEqual(old.version, new.version)
        self.assertEqual(old.name_templates, new.name_templates)

    def test_string_representation_same_as_old_configuration(self):
        self.maxDiff = None

        # TODO: Temporary test! Remove once configuration is refactored.
        old = Configuration(DEFAULT_CONFIG)

        parser = ConfigurationParser()
        new = parser.parse(DEFAULT_CONFIG)

        self.assertEqual(str(old), str(new))
