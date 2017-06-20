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

from unittest import util
from unittest import TestCase

from core.util import cli
from core.util.cli import colorize
from unit_utils import capture_stdout


class TestMsg(TestCase):
    def setUp(self):
        self.maxDiff = None
        util._MAX_LENGTH = 2000

    def test_msg_is_defined_and_available(self):
        self.assertIsNotNone(cli.msg)

    def test_msg_no_keyword_arguments(self):
        with capture_stdout() as out:
            cli.msg('text printed by msg()')

        self.assertIn('text printed by msg()', out.getvalue().strip())

    def test_msg_type_info(self):
        with capture_stdout() as out:
            cli.msg('text printed by msg() with type="info"', style='info')

        self.assertIn('text printed by msg() with type="info"',
                      out.getvalue().strip())

    def test_msg_type_info_log_true(self):
        with capture_stdout() as out:
            cli.msg('text printed by msg() with type="info", log=True',
                    style='info', log=True)

        self.assertIn('text printed by msg() with type="info", log=True',
                      out.getvalue().strip())

    def test_msg_type_color_quoted(self):
        with capture_stdout() as out:
            cli.msg('msg() text with type="color_quoted" no "yes" no',
                    style='color_quoted')

        self.assertIn('msg() text with type=', out.getvalue().strip())
        self.assertIn('color_quoted', out.getvalue().strip())
        self.assertIn('no', out.getvalue().strip())
        self.assertIn('yes', out.getvalue().strip())

    def test_msg_type_color_quoted_including_escape_sequences(self):
        # NOTE:  This will likely fail on some platforms!

        with capture_stdout() as out:
            cli.msg('msg() text with type="color_quoted" no "yes" no',
                    style='color_quoted')

            self.assertEqual('msg() text with type="\x1b[92mcolor_quoted\x1b[39m" no "\x1b[92myes\x1b[39m" no',
                             out.getvalue().strip())

        with capture_stdout() as out:
            cli.msg('no "yes" no', style='color_quoted')

            self.assertEqual('no "\x1b[92myes\x1b[39m" no',
                             out.getvalue().strip())

        with capture_stdout() as out:
            cli.msg('no "yes yes" no', style='color_quoted')
            self.assertEqual('no "\x1b[92myes yes\x1b[39m" no',
                             out.getvalue().strip())

        with capture_stdout() as out:
            cli.msg('Word "1234-56 word" -> "1234-56 word"',
                    style='color_quoted')
            self.assertEqual('Word "\x1b[92m1234-56 word\x1b[39m" -> "\x1b[92m1234-56 word\x1b[39m"',
                             out.getvalue().strip())

        with capture_stdout() as out:
            cli.msg('Word "word 1234-56" -> "1234-56 word"',
                    style='color_quoted')
            self.assertEqual('Word "\x1b[92mword 1234-56\x1b[39m" -> "\x1b[92m1234-56 word\x1b[39m"',
                             out.getvalue().strip())

        with capture_stdout() as out:
            cli.msg('A "b 123" -> A "b 123"', style='color_quoted')
            self.assertEqual('A "\x1b[92mb 123\x1b[39m" -> A "\x1b[92mb 123\x1b[39m"',
                             out.getvalue().strip())


class TestColorize(TestCase):
    # NOTE:  This will likely fail on some platforms!

    def test_colorize_returns_expected(self):
        self.assertEqual(colorize('foo'), 'foo')

    def test_colorize_returns_expected_with_fore_red(self):
        self.assertEqual(colorize('foo', fore='RED'),
                         '\x1b[31mfoo\x1b[39m')

    def test_colorize_returns_expected_with_fore_green(self):
        self.assertEqual(colorize('foo', fore='GREEN'),
                         '\x1b[32mfoo\x1b[39m')

    def test_colorize_returns_expected_with_fore_blue(self):
        self.assertEqual(colorize('foo', fore='BLUE'),
                         '\x1b[34mfoo\x1b[39m')

    def test_colorize_returns_expected_with_back_red(self):
        self.assertEqual(colorize('foo', back='RED'),
                         '\x1b[41mfoo\x1b[49m')

    def test_colorize_returns_expected_with_back_green(self):
        self.assertEqual(colorize('foo', back='GREEN'),
                         '\x1b[42mfoo\x1b[49m')

    def test_colorize_returns_expected_with_back_blue(self):
        self.assertEqual(colorize('foo', back='BLUE'),
                         '\x1b[44mfoo\x1b[49m')

    def test_colorize_returns_expected_with_style_normal(self):
        self.assertEqual(colorize('foo', style='NORMAL'),
                         '\x1b[22mfoo\x1b[0m')

    def test_colorize_returns_expected_with_style_dim(self):
        self.assertEqual(colorize('foo', style='DIM'),
                         '\x1b[2mfoo\x1b[0m')

    def test_colorize_returns_expected_with_style_bright(self):
        self.assertEqual(colorize('foo', style='BRIGHT'),
                         '\x1b[1mfoo\x1b[0m')

    def test_colorize_returns_expected_with_fore_red_back_red(self):
        self.assertEqual(colorize('foo', fore='RED', back='RED'),
                         '\x1b[31m\x1b[41mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_green_back_red(self):
        self.assertEqual(colorize('foo', fore='GREEN', back='RED'),
                         '\x1b[32m\x1b[41mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_blue_back_red(self):
        self.assertEqual(colorize('foo', fore='BLUE', back='RED'),
                         '\x1b[34m\x1b[41mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_red_back_green(self):
        self.assertEqual(colorize('foo', fore='RED', back='GREEN'),
                         '\x1b[31m\x1b[42mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_green_back_green(self):
        self.assertEqual(colorize('foo', fore='GREEN', back='GREEN'),
                         '\x1b[32m\x1b[42mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_blue_back_green(self):
        self.assertEqual(colorize('foo', fore='BLUE', back='GREEN'),
                         '\x1b[34m\x1b[42mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_red_back_blue(self):
        self.assertEqual(colorize('foo', fore='RED', back='BLUE'),
                         '\x1b[31m\x1b[44mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_green_back_blue(self):
        self.assertEqual(colorize('foo', fore='GREEN', back='BLUE'),
                         '\x1b[32m\x1b[44mfoo\x1b[49m\x1b[39m')

    def test_colorize_returns_expected_with_fore_blue_back_blue(self):
        self.assertEqual(colorize('foo', fore='BLUE', back='BLUE'),
                         '\x1b[34m\x1b[44mfoo\x1b[49m\x1b[39m')
