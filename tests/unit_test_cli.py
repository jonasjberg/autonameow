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
import unit_utils as uu


class TestMsg(TestCase):
    def setUp(self):
        self.maxDiff = None
        util._MAX_LENGTH = 2000

    def test_msg_is_defined_and_available(self):
        self.assertIsNotNone(cli.msg)

    def test_msg_no_keyword_arguments(self):
        with uu.capture_stdout() as out:
            cli.msg('text printed by msg()')

        self.assertIn('text printed by msg()', out.getvalue().strip())

    def test_msg_type_info(self):
        with uu.capture_stdout() as out:
            cli.msg('text printed by msg() with type="info"', style='info')

        self.assertIn('text printed by msg() with type="info"',
                      out.getvalue().strip())

    def test_msg_type_info_log_true(self):
        with uu.capture_stdout() as out:
            cli.msg('text printed by msg() with type="info", add_info_log=True',
                    style='info', add_info_log=True)

        self.assertIn(
            'text printed by msg() with type="info", add_info_log=True',
            out.getvalue().strip()
        )

    def test_msg_type_color_quoted(self):
        with uu.capture_stdout() as out:
            cli.msg('msg() text with type="color_quoted" no "yes" no',
                    style='color_quoted')

        self.assertIn('msg() text with type=', out.getvalue().strip())
        self.assertIn('color_quoted', out.getvalue().strip())
        self.assertIn('no', out.getvalue().strip())
        self.assertIn('yes', out.getvalue().strip())

    def test_msg_type_color_quoted_including_escape_sequences(self):
        # NOTE:  This will likely fail on some platforms!

        with uu.capture_stdout() as out:
            cli.msg('msg() text with type="color_quoted" no "yes" no',
                    style='color_quoted')

            self.assertEqual('msg() text with type="\x1b[92mcolor_quoted\x1b[39m" no "\x1b[92myes\x1b[39m" no',
                             out.getvalue().strip())

        with uu.capture_stdout() as out:
            cli.msg('no "yes" no', style='color_quoted')

            self.assertEqual('no "\x1b[92myes\x1b[39m" no',
                             out.getvalue().strip())

        with uu.capture_stdout() as out:
            cli.msg('no "yes yes" no', style='color_quoted')
            self.assertEqual('no "\x1b[92myes yes\x1b[39m" no',
                             out.getvalue().strip())

        with uu.capture_stdout() as out:
            cli.msg('Word "1234-56 word" -> "1234-56 word"',
                    style='color_quoted')
            self.assertEqual('Word "\x1b[92m1234-56 word\x1b[39m" -> "\x1b[92m1234-56 word\x1b[39m"',
                             out.getvalue().strip())

        with uu.capture_stdout() as out:
            cli.msg('Word "word 1234-56" -> "1234-56 word"',
                    style='color_quoted')
            self.assertEqual('Word "\x1b[92mword 1234-56\x1b[39m" -> "\x1b[92m1234-56 word\x1b[39m"',
                             out.getvalue().strip())

        with uu.capture_stdout() as out:
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


class TestMsgRename(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_msg_rename_is_defined(self):
        self.assertIsNotNone(cli.msg_rename)

    def test_can_be_called_with_valid_args_dry_run_true(self):
        cli.msg_rename('smulan.jpg',
                       '2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=True)

    def test_can_be_called_with_valid_args_dry_run_false(self):
        cli.msg_rename('smulan.jpg',
                       '2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=False)

    def test_can_be_called_with_valid_bytestring_args_dry_run_true(self):
        cli.msg_rename(b'smulan.jpg',
                       b'2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=True)

    def test_can_be_called_with_valid_bytestring_args_dry_run_false(self):
        cli.msg_rename(b'smulan.jpg',
                       b'2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=False)

    def test_valid_args_dry_run_true_gives_expected_output(self):
        with uu.capture_stdout() as out:
            cli.msg_rename('smulan.jpg',
                           '2010-0131T161251 a cat lying on a rug.jpg',
                           dry_run=True)

            self.assertEqual('Would have renamed  "\x1b[37msmulan.jpg\x1b[39m"\n                  ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                             out.getvalue().strip())

    def test_valid_args_dry_run_false_gives_expected_output(self):
        with uu.capture_stdout() as out:
            cli.msg_rename('smulan.jpg',
                           '2010-0131T161251 a cat lying on a rug.jpg',
                           dry_run=False)
            self.assertEqual(
                'Renamed  "\x1b[37msmulan.jpg\x1b[39m"\n       ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                 out.getvalue().strip()
            )

    def test_valid_bytestring_args_dry_run_true_gives_expected_output(self):
        with uu.capture_stdout() as out:
            cli.msg_rename(b'smulan.jpg',
                           b'2010-0131T161251 a cat lying on a rug.jpg',
                           dry_run=True)

            self.assertEqual('Would have renamed  "\x1b[37msmulan.jpg\x1b[39m"\n                  ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                             out.getvalue().strip())

    def test_valid_bytestring_args_dry_run_false_gives_expected_output(self):
        with uu.capture_stdout() as out:
            cli.msg_rename(b'smulan.jpg',
                           b'2010-0131T161251 a cat lying on a rug.jpg',
                           dry_run=False)
            self.assertEqual(
                'Renamed  "\x1b[37msmulan.jpg\x1b[39m"\n       ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                out.getvalue().strip()
            )


class TestColumnFormatter(TestCase):
    def setUp(self):
        self.padding = ' ' * cli.ColumnFormatter.COLUMN_PADDING
        self.cf = cli.ColumnFormatter()
        self.cf.addrow('foo', 'fooooooooo')
        self.cf.addrow('a', 'b')
        self.cf.addrow('kjhdsfkjhsdfgkjhsdfg', 'mjao')
        self.cf.addrow('3', '666')
        print(self.cf)

    def test_column_counter(self):
        cf = cli.ColumnFormatter()
        self.assertEqual(cf.number_columns, 0)

        cf.addrow('foo')
        self.assertEqual(cf.number_columns, 1)
        cf.addrow('foo')
        self.assertEqual(cf.number_columns, 1)
        cf.addrow('foo', 'bar')
        self.assertEqual(cf.number_columns, 2)
        cf.addrow('foo')
        self.assertEqual(cf.number_columns, 2)
        cf.addrow('foo', 'bar', 'baz')
        self.assertEqual(cf.number_columns, 3)

    def test_column_widths(self):
        cf = cli.ColumnFormatter()
        self.assertEqual(cf.column_widths, [])

        cf.addrow('foo')
        self.assertEqual(cf.column_widths, [3])
        cf.addrow('foo')
        self.assertEqual(cf.column_widths, [3])
        cf.addrow('foo', 'bar')
        self.assertEqual(cf.column_widths, [3, 3])
        cf.addrow('AAAAHH')
        self.assertEqual(cf.column_widths, [6, 3])
        cf.addrow('foo', 'bar', 'baz')
        self.assertEqual(cf.column_widths, [6, 3, 3])
        cf.addrow('a', 'b', 'MJAOOOOAJM')
        self.assertEqual(cf.column_widths, [6, 3, 10])

    def test_formats_single_column(self):
        cf = cli.ColumnFormatter()
        cf.addrow('foo')
        cf.addrow('bar')
        cf.addrow('baz')

        actual = str(cf)
        # expected = 'foo  \nbar  \nbaz  '
        expected = 'foo\nbar\nbaz'
        self.assertEqual(actual, expected)

    def test_formats_single_column_with_empty_strings(self):
        cf = cli.ColumnFormatter()
        cf.addrow('foo')
        cf.addrow(' ')
        cf.addrow('baz')

        actual = str(cf)
        expected = 'foo\nbaz'.format(p=self.padding)
        self.assertEqual(actual, expected)

    def test_formats_single_column_with_none_elements(self):
        cf = cli.ColumnFormatter()
        cf.addrow('foo')
        cf.addrow(None)
        cf.addrow('baz')

        actual = str(cf)
        expected = 'foo\nbaz'.format(p=self.padding)
        self.assertEqual(actual, expected)

    def test_formats_two_columns(self):
        cf = cli.ColumnFormatter()
        cf.addrow('foo_A', 'foo_B')
        cf.addrow('bar_A', 'bar_B')
        cf.addrow('baz_A', 'baz_B')

        actual = str(cf)
        expect = 'foo_A{p}foo_B\nbar_A{p}bar_B\nbaz_A{p}baz_B'.format(
            p=self.padding
        )
        self.assertEqual(actual, expect)

    def test_format_two_columns_expands_width(self):
        cf = cli.ColumnFormatter()
        cf.addrow('foo_A')
        cf.addrow('bar_A', 'bar_B')
        cf.addrow('baz_A', 'baz_B')

        actual = str(cf)
        expected = 'foo_A\nbar_A{p}bar_B\nbaz_A{p}baz_B'.format(
            p=self.padding
        )
        self.assertEqual(actual, expected)

    def test_format_three_columns(self):
        cf = cli.ColumnFormatter()
        cf.addrow('A1', 'BB1', 'CC11')
        cf.addrow('A2', 'BB2', 'CC22')
        cf.addrow('A3', 'BB3', 'CC33')

        actual = str(cf)
        expected = 'A1{p}BB1{p}CC11\nA2{p}BB2{p}CC22\nA3{p}BB3{p}CC33'.format(
            p=self.padding
        )
        self.assertEqual(actual, expected)
