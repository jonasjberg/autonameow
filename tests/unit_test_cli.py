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

from core.util import cli
from unit_utils import capture_stdout


class TestMsg(TestCase):
    def test_msg_is_defined_and_available(self):
        self.assertIsNotNone(cli.msg)

    def test_msg_no_keyword_arguments(self):
        with capture_stdout() as out:
            cli.msg('text printed by msg()')

        self.assertIn('text printed by msg()', out.getvalue().strip())

    def test_msg_type_info(self):
        with capture_stdout() as out:
            cli.msg('text printed by msg() with type="info"', type='info')

        self.assertIn('text printed by msg() with type="info"',
                      out.getvalue().strip())

    def test_msg_type_info_log_true(self):
        with capture_stdout() as out:
            cli.msg('text printed by msg() with type="info", log=True',
                    type='info', log=True)

        self.assertIn('text printed by msg() with type="info", log=True',
                      out.getvalue().strip())

    def test_msg_type_color_quoted(self):
        with capture_stdout() as out:
            cli.msg('msg() text with type="color_quoted" no "yes" no',
                    type='color_quoted')

        # self.assertIn('msg() text with type="color_quoted" no "yes" no',
        #               out.getvalue().strip())
        self.assertIn('msg() text with type=', out.getvalue().strip())
        self.assertIn('color_quoted', out.getvalue().strip())
        self.assertIn('no', out.getvalue().strip())
        self.assertIn('yes', out.getvalue().strip())

