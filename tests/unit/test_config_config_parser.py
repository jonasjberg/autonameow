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

import sys
from unittest import (
    skipIf,
    TestCase
)

try:
    import yaml
except ImportError:
    yaml = None
    print('Missing required module "yaml". '
          'Make sure "pyyaml" is available before running this program.',
          file=sys.stderr)

import unit.utils as uu
import unit.constants as uuconst
from core.config.config_parser import ConfigurationParser
from core.exceptions import EncodingBoundaryViolation


def yaml_unavailable():
    return yaml is None, 'Failed to import "yaml"'


class TestConfigurationParser(TestCase):
    # TODO: ..
    pass


@skipIf(*yaml_unavailable())
class TestDefaultConfigFromFile(TestCase):
    def setUp(self):
        self.config_parser = ConfigurationParser()

        self.config_path_unicode = uu.abspath_testfile(
            uuconst.DEFAULT_YAML_CONFIG_BASENAME
        )
        uu.file_exists(self.config_path_unicode)
        uu.path_is_readable(self.config_path_unicode)
        self.assertTrue(uu.is_internalstring(self.config_path_unicode))

        self.config_path_bytestring = uu.normpath(self.config_path_unicode)
        uu.file_exists(self.config_path_bytestring)
        uu.path_is_readable(self.config_path_bytestring)
        self.assertTrue(uu.is_internalbytestring(self.config_path_bytestring))

    def test_loads_default_config_from_bytestring_path(self):
        config = self.config_parser.from_file(self.config_path_bytestring)
        self.assertIsNotNone(config)

    def test_loading_unicode_path_raises_exception(self):
        with self.assertRaises(EncodingBoundaryViolation):
            _ = self.config_parser.from_file(self.config_path_unicode)
