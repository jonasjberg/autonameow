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

import unittest
from unittest import TestCase

from core.ui.cli.common import (
    colorize,
    ColumnFormatter,
    msg,
    msg_rename
)
import unit_utils as uu


ANSI_RESET_FG = '\x1b[39m'
ANSI_RESET_BG = '\x1b[49m'


class TestMsg(TestCase):
    def setUp(self):
        self.maxDiff = None
        unittest.util._MAX_LENGTH = 2000

    def test_msg_no_keyword_arguments(self):
        with uu.capture_stdout() as out:
            msg('text printed by msg()')

        self.assertIn('text printed by msg()', out.getvalue().strip())

    def test_msg_type_info(self):
        with uu.capture_stdout() as out:
            msg('text printed by msg() with type="info"', style='info')

        self.assertIn('text printed by msg() with type="info"',
                      out.getvalue().strip())

    def test_msg_type_info_log_true(self):
        with uu.capture_stdout() as out:
            msg('text printed by msg() with type="info", add_info_log=True',
                style='info', add_info_log=True)

        self.assertIn(
            'text printed by msg() with type="info", add_info_log=True',
            out.getvalue().strip()
        )

    def test_msg_type_color_quoted(self):
        with uu.capture_stdout() as out:
            msg('msg() text with type="color_quoted" no "yes" no',
                style='color_quoted')

        self.assertIn('msg() text with type=', out.getvalue().strip())
        self.assertIn('color_quoted', out.getvalue().strip())
        self.assertIn('no', out.getvalue().strip())
        self.assertIn('yes', out.getvalue().strip())

    # NOTE(jonas): This will likely fail on some platforms!
    def test_msg_type_color_quoted_including_escape_sequences(self):
        # ANSI_COLOR must match actual color. Currently 'LIGHTGREEN_EX'
        ANSI_COLOR = '\x1b[92m'

        def __check_output(given, expect):
            assert isinstance(given, str)
            assert isinstance(expect, str)
            with uu.capture_stdout() as _stdout:
                msg(given, style='color_quoted')
                self.assertEqual(
                    expect.format(COL=ANSI_COLOR, RES=ANSI_RESET_FG),
                    _stdout.getvalue().strip()
                )

        __check_output(
            given='msg() text with type="color_quoted" no "yes" no',
            expect='msg() text with type="{COL}color_quoted{RES}" no "{COL}yes{RES}" no'
        )
        __check_output(
            given='no "yes" no',
            expect='no "{COL}yes{RES}" no'
        )
        __check_output(
            given='no "yes yes" no',
            expect='no "{COL}yes yes{RES}" no'
        )
        __check_output(
            given='Word "1234-56 word" -> "1234-56 word"',
            expect='Word "{COL}1234-56 word{RES}" -> "{COL}1234-56 word{RES}"'
        )
        __check_output(
            given='Word "word 1234-56" -> "1234-56 word"',
            expect='Word "{COL}word 1234-56{RES}" -> "{COL}1234-56 word{RES}"'
        )
        __check_output(
            given='A "b 123" -> A "b 123"',
            expect='A "{COL}b 123{RES}" -> A "{COL}b 123{RES}"'
        )


class TestColorize(TestCase):
    # NOTE:  This will likely fail on some platforms!

    COLORIZE_FOREGROUND_ANSI_LOOKUP = {
        'RED': '\x1b[31m',
        'GREEN': '\x1b[32m',
        'BLUE': '\x1b[34m',
    }
    COLORIZE_BACKGROUND_ANSI_LOOKUP = {
        'RED': '\x1b[41m',
        'GREEN': '\x1b[42m',
        'BLUE': '\x1b[44m',
    }

    def __check_colorize(self, text, expect,
                         fore=None, back=None):
        actual = colorize(text, fore, back)

        _ansi_fg = self.COLORIZE_FOREGROUND_ANSI_LOOKUP.get(fore, '')
        _ansi_bg = self.COLORIZE_BACKGROUND_ANSI_LOOKUP.get(back, '')
        _expected = expect.format(
            BGCOL=_ansi_bg, FGCOL=_ansi_fg, FGRES=ANSI_RESET_FG,
            BGRES=ANSI_RESET_BG
        )
        self.assertEqual(actual, _expected)

    def test_colorize_pass_through_with_no_fore_no_back_no_style(self):
        self.assertEqual(colorize(''), '')
        self.assertEqual(colorize(' '), ' ')
        self.assertEqual(colorize('foo'), 'foo')

    def test_colorize_returns_expected_with_fore_red(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}foo{FGRES}',
                              fore='RED')

    def test_colorize_returns_expected_with_fore_green(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}foo{FGRES}',
                              fore='GREEN')

    def test_colorize_returns_expected_with_fore_blue(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}foo{FGRES}',
                              fore='BLUE')

    def test_colorize_returns_expected_with_back_red(self):
        self.__check_colorize(text='foo',
                              expect='{BGCOL}foo{BGRES}',
                              back='RED')

    def test_colorize_returns_expected_with_back_green(self):
        self.__check_colorize(text='foo',
                              expect='{BGCOL}foo{BGRES}',
                              back='GREEN')

    def test_colorize_returns_expected_with_back_blue(self):
        self.__check_colorize(text='foo',
                              expect='{BGCOL}foo{BGRES}',
                              back='BLUE')

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
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='RED', back='RED')

    def test_colorize_returns_expected_with_fore_green_back_red(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='GREEN', back='RED')

    def test_colorize_returns_expected_with_fore_blue_back_red(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='BLUE', back='RED')

    def test_colorize_returns_expected_with_fore_red_back_green(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='RED', back='GREEN')

    def test_colorize_returns_expected_with_fore_green_back_green(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='GREEN', back='GREEN')

    def test_colorize_returns_expected_with_fore_blue_back_green(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='BLUE', back='GREEN')

    def test_colorize_returns_expected_with_fore_red_back_blue(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='RED', back='BLUE')

    def test_colorize_returns_expected_with_fore_green_back_blue(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='GREEN', back='BLUE')

    def test_colorize_returns_expected_with_fore_blue_back_blue(self):
        self.__check_colorize(text='foo',
                              expect='{FGCOL}{BGCOL}foo{BGRES}{FGRES}',
                              fore='BLUE', back='BLUE')


class TestMsgRename(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_can_be_called_with_valid_args_dry_run_true(self):
        msg_rename('smulan.jpg',
                   '2010-0131T161251 a cat lying on a rug.jpg',
                   dry_run=True)

    def test_can_be_called_with_valid_args_dry_run_false(self):
        msg_rename('smulan.jpg',
                   '2010-0131T161251 a cat lying on a rug.jpg',
                   dry_run=False)

    def test_can_be_called_with_valid_bytestring_args_dry_run_true(self):
        msg_rename(b'smulan.jpg',
                   b'2010-0131T161251 a cat lying on a rug.jpg',
                   dry_run=True)

    def test_can_be_called_with_valid_bytestring_args_dry_run_false(self):
        msg_rename(b'smulan.jpg',
                   b'2010-0131T161251 a cat lying on a rug.jpg',
                   dry_run=False)

    def test_valid_args_dry_run_true_gives_expected_output(self):
        with uu.capture_stdout() as out:
            msg_rename('smulan.jpg',
                       '2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=True)
            self.assertEqual(
                'Would have renamed  "\x1b[37msmulan.jpg\x1b[39m"\n                ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                out.getvalue().strip()
            )

    def test_valid_args_dry_run_false_gives_expected_output(self):
        with uu.capture_stdout() as out:
            msg_rename('smulan.jpg',
                       '2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=False)
            self.assertEqual(
                'Renamed  "\x1b[37msmulan.jpg\x1b[39m"\n     ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                 out.getvalue().strip()
            )

    def test_valid_bytestring_args_dry_run_true_gives_expected_output(self):
        with uu.capture_stdout() as out:
            msg_rename(b'smulan.jpg',
                       b'2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=True)
            self.assertEqual(
                'Would have renamed  "\x1b[37msmulan.jpg\x1b[39m"\n                ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                out.getvalue().strip()
            )

    def test_valid_bytestring_args_dry_run_false_gives_expected_output(self):
        with uu.capture_stdout() as out:
            msg_rename(b'smulan.jpg',
                       b'2010-0131T161251 a cat lying on a rug.jpg',
                       dry_run=False)
            self.assertEqual(
                'Renamed  "\x1b[37msmulan.jpg\x1b[39m"\n     ->  "\x1b[92m2010-0131T161251 a cat lying on a rug.jpg\x1b[39m"',
                out.getvalue().strip()
            )


class TestColumnFormatter(TestCase):
    def setUp(self):
        self.padding = (ColumnFormatter.PADDING_CHAR
                        * ColumnFormatter.COLUMN_PADDING)

    def test_column_counter(self):
        cf = ColumnFormatter()
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
        cf = ColumnFormatter()
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


class TestColumnFormatterOneColumn(TestCase):
    def setUp(self):
        self.padding = (ColumnFormatter.PADDING_CHAR
                        * ColumnFormatter.COLUMN_PADDING)

    def test_formats_single_column(self):
        cf = ColumnFormatter()
        cf.addrow('foo')
        cf.addrow('bar')
        cf.addrow('baz')

        actual = str(cf)
        expected = 'foo\nbar\nbaz'
        self.assertEqual(actual, expected)

    def test_formats_single_column_with_empty_strings(self):
        cf = ColumnFormatter()
        cf.addrow('foo')
        cf.addrow(' ')
        cf.addrow('baz')

        actual = str(cf)
        expected = 'foo\n\nbaz'.format(p=self.padding)
        self.assertEqual(actual, expected)

    def test_formats_single_column_with_none_elements(self):
        cf = ColumnFormatter()
        cf.addrow('foo')
        cf.addrow(None)
        cf.addrow('baz')

        actual = str(cf)
        expected = 'foo\n\nbaz'.format(p=self.padding)
        self.assertEqual(actual, expected)


class TestColumnFormatterTwoColumns(TestCase):
    def setUp(self):
        self.padding = (ColumnFormatter.PADDING_CHAR
                        * ColumnFormatter.COLUMN_PADDING)

    def test_formats_two_columns(self):
        cf = ColumnFormatter()
        cf.addrow('foo_A', 'foo_B')
        cf.addrow('bar_A', 'bar_B')
        cf.addrow('baz_A', 'baz_B')

        actual = str(cf)
        expect = 'foo_A{p}foo_B\nbar_A{p}bar_B\nbaz_A{p}baz_B'.format(
            p=self.padding
        )
        self.assertEqual(actual, expect)

    def test_format_two_columns_expands_width(self):
        cf = ColumnFormatter()
        cf.addrow('A')
        cf.addrow('tuna', 'MJAAAAOOOOOOOOOO')
        cf.addrow('OOOOOOOOOOAAAAJM', 'B')
        actual = str(cf)

        expected = '''
A
tuna            {p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B'''.format(p=self.padding).lstrip('\n')
        self.assertEqual(actual, expected)

    def test_format_two_columns_align_all_left(self):
        cf = ColumnFormatter()
        cf.addrow('a',    'bbb')
        cf.addrow('cccc', 'd')
        cf.setalignment('left', 'left', 'left')
        actual = str(cf)

        expected = 'a   {p}bbb\ncccc{p}d'.format(p=self.padding)
        self.assertEqual(actual, expected)

    def test_format_two_columns_align_all_right(self):
        cf = ColumnFormatter()
        cf.addrow('A',    'B')
        cf.addrow('a',    'bbb')
        cf.addrow('cccc', 'd')
        cf.setalignment('right', 'right', 'right')
        actual = str(cf)

        expected = '''
   A{p}  B
   a{p}bbb
cccc{p}  d'''.format(p=self.padding).lstrip('\n')
        self.assertEqual(actual, expected)


class TestColumnFormatterThreeColumns(TestCase):
    def setUp(self):
        self.padding = (ColumnFormatter.PADDING_CHAR
                        * ColumnFormatter.COLUMN_PADDING)

    def test_format_three_columns(self):
        cf = ColumnFormatter()
        cf.addrow('A1', 'BB1', 'CC11')
        cf.addrow('A2', 'BB2', 'CC22')
        cf.addrow('A3', 'BB3', 'CC33')
        actual = str(cf)

        expected = 'A1{p}BB1{p}CC11\nA2{p}BB2{p}CC22\nA3{p}BB3{p}CC33'.format(
            p=self.padding
        )
        self.assertEqual(actual, expected)

    def test_format_three_columns_expands_width(self):
        cf = ColumnFormatter()
        cf.addrow('A')
        cf.addrow('tuna', 'MJAAAAOOOOOOOOOO')
        cf.addrow('OOOOOOOOOOAAAAJM', 'B')
        cf.addrow('42', '0x4E4F4F42')
        cf.addrow('C', 'D', 'E')
        actual = str(cf)

        expected = '''
A
tuna            {p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B
42              {p}0x4E4F4F42
C               {p}D               {p}E'''.format(p=self.padding).lstrip('\n')
        self.assertEqual(actual, expected)

    def test_format_three_columns_align_all_left(self):
        cf = ColumnFormatter()
        cf.addrow('A')
        cf.addrow('tuna', 'MJAAAAOOOOOOOOOO')
        cf.addrow('OOOOOOOOOOAAAAJM', 'B')
        cf.addrow('42', '0x4E4F4F42')
        cf.addrow('C', 'D', 'E')
        cf.setalignment('left', 'left', 'left')
        actual = str(cf)

        expected = '''
A
tuna            {p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B
42              {p}0x4E4F4F42
C               {p}D               {p}E'''.format(p=self.padding).lstrip('\n')
        self.assertEqual(actual, expected)

    def test_format_three_columns_align_all_right(self):
        cf = ColumnFormatter()
        cf.addrow('A')
        cf.addrow('tuna', 'MJAAAAOOOOOOOOOO')
        cf.addrow('OOOOOOOOOOAAAAJM', 'B')
        cf.addrow('42', '0x4E4F4F42')
        cf.addrow('C', 'D', 'E')
        cf.setalignment('right', 'right', 'right')
        actual = str(cf)

        expected = '''
               A
            tuna{p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}               B
              42{p}      0x4E4F4F42
               C{p}               D{p}E'''.format(p=self.padding).lstrip('\n')
        self.assertEqual(actual, expected)

    def test_format_three_columns_align_mixed(self):
        cf = ColumnFormatter()
        cf.addrow('A')
        cf.addrow('tuna', 'MJAAAAOOOOOOOOOO')
        cf.addrow('OOOOOOOOOOAAAAJM', 'B')
        cf.addrow('42', '0x4E4F4F42')
        cf.addrow('C', 'D', 'E')
        cf.setalignment('right', 'left', 'right')
        actual = str(cf)

        expected = '''
               A
            tuna{p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B
              42{p}0x4E4F4F42
               C{p}D               {p}E'''.format(p=self.padding).lstrip('\n')
        self.assertEqual(actual, expected)
