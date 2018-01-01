# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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


class TestTemporaryStuff(TestCase):
    # def test_temporary_write_testdata(self):
    #     from core.disk import write_yaml_file
    #     _asserts = {
    #         'exit_code': 0,
    #         'renames': {
    #             'gmail.pdf': '2016-01-11T124132 gmail.pdf',
    #             'foo': 'bar'
    #         }
    #     }
    #     write_yaml_file(b'/tmp/test_asserts.yaml', _asserts)

    # def test_temporary_write_options(self):
    #     from core.disk import write_yaml_file
    #     _opts = {'debug': False, 'verbose': True, 'quiet': False, 'show_version': False, 'dump_config': False, 'dump_options': False, 'dump_meowuris': False, 'list_all': True, 'mode_batch': True, 'mode_automagic': True, 'mode_interactive': False, 'config_path': None, 'dry_run': True, 'recurse_paths': False, 'input_paths': ['/Users/jonas/PycharmProjects/autonameow.git/test_files/gmail.pdf']}
    #     write_yaml_file(b'/tmp/test_options.yaml', _opts)

    def test_noop(self):
        self.assertTrue(True)


