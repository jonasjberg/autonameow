# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
from unittest.mock import patch

import unit.utils as uu
from core.view.cli.common import colorize
from core.view.cli.common import colorize_quoted
from core.view.cli.common import ColumnFormatter
from core.view.cli.common import msg
from core.view.cli.common import msg_columnate
from core.view.cli.common import msg_possible_rename
from core.view.cli.common import msg_rename
from core.view.cli.common import _colorize_string_diff


class TestColoramaIsAvailable(TestCase):
    def test_successfully_imported_colorama(self):
        try:
            import colorama
        except ImportError:
            self.fail('Failed to import vendored module "colorama"')


ANSI_RESET_FG = '\x1b[39m'
ANSI_RESET_BG = '\x1b[49m'


class TestMsg(TestCase):
    def _check_msg(self, *args, **kwargs):
        expected = kwargs.pop('expected')
        with uu.capture_stdout() as captured_stdout:
            msg(*args, **kwargs)
        self.assertIn(expected, captured_stdout.getvalue())

    def test_raises_exception_given_byte_string_message(self):
        with self.assertRaises(AssertionError):
            msg(b'foo')

    def test_msg_no_keyword_arguments(self):
        self._check_msg('text printed by msg()',
                        expected='text printed by msg()')

    def test_msg_style_info(self):
        self._check_msg('text printed by msg() with style="info"', style='info',
                        expected='text printed by msg() with style="info"')

    def test_msg_style_color_quoted(self):
        with uu.capture_stdout() as out:
            msg('msg() text with style="color_quoted" no "yes" no',
                style='color_quoted')

        self.assertIn('msg() text with style=', out.getvalue().strip())
        self.assertIn('color_quoted', out.getvalue().strip())
        self.assertIn('no', out.getvalue().strip())
        self.assertIn('yes', out.getvalue().strip())

    # NOTE(jonas): This will likely fail on some platforms!
    def test_msg_style_color_quoted_including_escape_sequences(self):
        # ANSI_COLOR must match actual color. Currently 'LIGHTGREEN_EX'
        ANSI_COLOR = '\x1b[92m'

        def __check_color_quoted_msg(given, expect):
            assert isinstance(given, str)
            assert isinstance(expect, str)
            expected_with_ansi_escapes = expect.format(COL=ANSI_COLOR, RES=ANSI_RESET_FG)
            self._check_msg(given, style='color_quoted', expected=expected_with_ansi_escapes)

        __check_color_quoted_msg(
            given='msg() text with style="color_quoted" no "yes" no',
            expect='msg() text with style="{COL}color_quoted{RES}" no "{COL}yes{RES}" no\n'
        )
        __check_color_quoted_msg(
            given='no "yes" no',
            expect='no "{COL}yes{RES}" no\n'
        )
        __check_color_quoted_msg(
            given='no "yes yes" no',
            expect='no "{COL}yes yes{RES}" no\n'
        )
        __check_color_quoted_msg(
            given='Word "1234-56 word" -> "1234-56 word"',
            expect='Word "{COL}1234-56 word{RES}" -> "{COL}1234-56 word{RES}"\n'
        )
        __check_color_quoted_msg(
            given='Word "word 1234-56" -> "1234-56 word"',
            expect='Word "{COL}word 1234-56{RES}" -> "{COL}1234-56 word{RES}"\n'
        )
        __check_color_quoted_msg(
            given='A "b 123" -> A "b 123"',
            expect='A "{COL}b 123{RES}" -> A "{COL}b 123{RES}"\n'
        )

    def test_msg_style_heading(self):
        self._check_msg('text printed by msg() with style="heading"', style='heading',
                        expected='''

[1mtext printed by msg() with style="heading"[0m
[2m==========================================[0m
''')

    def test_msg_style_section(self):
        self._check_msg('text printed by msg() with style="section"', style='section',
                        expected='''
[1mtext printed by msg() with style="section"[0m
''')


class TestColorize(TestCase):

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
        for given in ['', ' ', 'foo']:
            self.assertEqual(given, colorize(given))

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
    ANSI_COL_FROM = '\x1b[37m'
    ANSI_COL_DEST = '\x1b[92m'

    def setUp(self):
        self.maxDiff = None

    def test_can_be_called_with_valid_unicode_strings(self):
        for _dry_run_enabled in (True, False):
            with self.subTest(dry_run=_dry_run_enabled):
                with uu.capture_stdout() as _:
                    msg_rename('foo', 'bar', _dry_run_enabled)

    def _assert_raises(self, given_from, given_dest):
        for _dry_run_enabled in (True, False):
            with self.subTest(dry_run=_dry_run_enabled):
                with uu.capture_stdout() as _:
                    with self.assertRaises(AssertionError):
                        msg_rename(given_from, given_dest, _dry_run_enabled)

    def test_raises_exception_if_called_with_bytes_string_dest(self):
        self._assert_raises('foo', b'bar')

    def test_raises_exception_if_called_with_bytes_string_from(self):
        self._assert_raises(b'foo', 'bar')

    def test_raises_exception_if_called_with_bytes_strings_dest_and_from(self):
        self._assert_raises(b'foo', b'bar')

    def __check_msg_rename(self, given_from, given_dest, dry_run, expect):
        with uu.capture_stdout() as out:
            msg_rename(given_from, given_dest, dry_run)
            _expected = expect.format(
                CF=self.ANSI_COL_FROM, CD=self.ANSI_COL_DEST, R=ANSI_RESET_FG
            )
            self.assertEqual(_expected, out.getvalue().strip())

    def test_valid_args_dry_run_true_gives_expected_output(self):
        self.__check_msg_rename(
            given_from='smulan.jpg',
            given_dest='2010-0131T161251 a cat lying on a rug.jpg',
            dry_run=True,
            expect='''Would have renamed  "{CF}smulan.jpg{R}"
                ->  "{CD}2010-0131T161251 a cat lying on a rug.jpg{R}"''',
        )

    def test_valid_args_dry_run_false_gives_expected_output(self):
        self.__check_msg_rename(
            given_from='smulan.jpg',
            given_dest='2010-0131T161251 a cat lying on a rug.jpg',
            dry_run=False,
            expect='''Renamed  "{CF}smulan.jpg{R}"
     ->  "{CD}2010-0131T161251 a cat lying on a rug.jpg{R}"''',
        )


class TestMsgPossibleRename(TestCase):
    def test_can_be_called_with_valid_unicode_strings(self):
        with uu.capture_stdout() as _:
            msg_possible_rename('foo', 'bar')

    def _assert_raises(self, given_from, given_dest):
        with uu.capture_stdout() as _:
            with self.assertRaises(AssertionError):
                msg_possible_rename(given_from, given_dest)

    def test_raises_exception_if_called_with_bytes_string_dest(self):
        self._assert_raises('foo', b'bar')

    def test_raises_exception_if_called_with_bytes_string_from(self):
        self._assert_raises(b'foo', 'bar')

    def test_raises_exception_if_called_with_bytes_strings_dest_and_from(self):
        self._assert_raises(b'foo', b'bar')


class TestColorizeStringDiff(TestCase):
    def _assert_given(self, given, expect):
        expect_a, expect_b = expect
        given_a, given_b = given

        def _mock_colorize(string, color):
            # Use strings instead of ANSI escape codes.
            #   Primary color start: 'C1'
            # Secondary color start: 'C2'
            #     Color end (reset): 'CR'
            return color + string + 'CR'

        actual_a, actual_b = _colorize_string_diff(
            given_a, given_b, color='C1', secondary_color='C2',
            colorize_=_mock_colorize
        )
        self.assertEqual(expect_a, actual_a, 'Given A: "{}"'.format(given_a))
        self.assertEqual(expect_b, actual_b, 'Given B: "{}"'.format(given_b))

    def test_returns_empty_strings_as_is(self):
        self._assert_given(['', ''], expect=['', ''])

    def test_returns_whitespace_strings_as_is(self):
        self._assert_given((' ', ' '), expect=(' ', ' '))

    def test_returns_identical_strings_as_is(self):
        self._assert_given(['a', 'a'], expect=['a', 'a'])

    def test_colorizes_one_character_difference(self):
        self._assert_given(['a', 'b'], expect=['C1aCR', 'C1bCR'])

    def test_colorizes_case_difference_with_secondary_color(self):
        self._assert_given(['a', 'A'], expect=['C2aCR', 'C2ACR'])

    def test_colorizes_both_case_difference_and_character_difference(self):
        self._assert_given(['foo a', 'bar A'], expect=['C1fooCR C2aCR', 'C1barCR C2ACR'])


class _CaseColumnFormatter(object):
    def setUp(self):
        self.cf = ColumnFormatter()
        self.padding = self.cf.PADDING_CHAR * self.cf.COLUMN_PADDING
        assert isinstance(self.padding, str), 'sanity check'

    def _addrow(self, *args):
        self.cf.addrow(*args)

    def _setalignment(self, *args):
        self.cf.setalignment(*args)

    def _assert_column_widths(self, *expected):
        self.assertEqual(list(expected), self.cf.column_widths)

    def _assert_number_of_columns(self, expected):
        assert isinstance(expected, int), 'sanity check'
        self.assertEqual(expected, self.cf.number_columns)

    def _assert_formatted_output(self, expected):
        assert isinstance(expected, str), 'sanity check'
        expected_with_padding = expected.format(p=self.padding)

        actual = str(self.cf)
        self.assertIsInstance(actual, str)
        self.assertEqual(expected_with_padding, actual)

    def _set_max_total_width(self, max_width):
        self.cf.max_total_width = max_width


class TestColumnFormatter(_CaseColumnFormatter, TestCase):
    def test_column_counter(self):
        self._assert_number_of_columns(0)
        self._addrow('foo')
        self._assert_number_of_columns(1)
        self._addrow('foo')
        self._assert_number_of_columns(1)
        self._addrow('foo', 'bar')
        self._assert_number_of_columns(2)
        self._addrow('foo')
        self._assert_number_of_columns(2)
        self._addrow('foo', 'bar', 'baz')
        self._assert_number_of_columns(3)

    def test_column_widths(self):
        self._assert_column_widths()
        self._addrow('foo')
        self._assert_column_widths(3)
        self._addrow('foo')
        self._assert_column_widths(3)
        self._addrow('foo', 'bar')
        self._assert_column_widths(3, 3)
        self._addrow('oof', 'rab')
        self._assert_column_widths(3, 3)
        self._addrow('AAAAHH')
        self._assert_column_widths(6, 3)
        self._addrow('foo', 'bar', 'baz')
        self._assert_column_widths(6, 3, 3)
        self._addrow('a', 'b', 'MJAOOOOAJM')
        self._assert_column_widths(6, 3, 10)


class TestColumnFormatterOneColumn(_CaseColumnFormatter, TestCase):
    def test_formats_single_column(self):
        self._addrow('foo')
        self._addrow('bar')
        self._addrow('baz')
        self._assert_number_of_columns(1)
        self._assert_column_widths(3)
        self._assert_formatted_output('foo\nbar\nbaz')

    def test_formats_single_column_with_empty_strings(self):
        self._addrow('foo')
        self._addrow(' ')
        self._addrow('baz')
        self._assert_number_of_columns(1)
        self._assert_column_widths(3)
        self._assert_formatted_output('foo\n\nbaz')

    def test_formats_single_column_with_none_elements(self):
        self._addrow('foo')
        self._addrow(None)
        self._addrow('baz')
        self._assert_number_of_columns(1)
        self._assert_column_widths(3)
        self._assert_formatted_output('foo\n\nbaz')

    def test_limits_width_of_single_line(self):
        self._addrow('123456')
        self._set_max_total_width(3)
        self._assert_formatted_output('123')

    def test_limits_width_of_two_lines_of_equal_length(self):
        self._addrow('123456')
        self._addrow('abcdef')
        self._set_max_total_width(3)
        self._assert_formatted_output('123\nabc')

    def test_truncates_longest_of_two_lines(self):
        self._addrow('123456789')
        self._addrow('abcdef')
        self._set_max_total_width(6)
        self._assert_formatted_output('123456\nabcdef')


class TestColumnFormatterTwoColumns(_CaseColumnFormatter, TestCase):
    def test_formats_two_columns(self):
        self._addrow('foo_A', 'foo_B')
        self._addrow('bar_A', 'bar_B')
        self._addrow('baz_A', 'baz_B')
        self._assert_number_of_columns(2)
        self._assert_column_widths(5, 5)
        self._assert_formatted_output('foo_A{p}foo_B\nbar_A{p}bar_B\nbaz_A{p}baz_B')

    def test_format_two_columns_expands_width(self):
        self._addrow('A')
        self._assert_column_widths(1)
        self._addrow('tuna', 'MJAAAAOOOOOOOOOO')
        self._assert_column_widths(4, 16)
        self._addrow('OOOOOOOOOOAAAAJM', 'B')
        self._assert_column_widths(16, 16)
        self._assert_formatted_output('''
A
tuna            {p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B'''.lstrip('\n'))

    def test_format_two_columns_align_all_left(self):
        self._addrow('a',    'bbb')
        self._addrow('cccc', 'd')
        self._setalignment('left', 'left', 'left')
        self._assert_formatted_output('a   {p}bbb\ncccc{p}d')

    def test_format_two_columns_align_all_right(self):
        self._addrow('A',    'B')
        self._addrow('a',    'bbb')
        self._addrow('cccc', 'd')
        self._setalignment('right', 'right', 'right')
        self._assert_formatted_output('''
   A{p}  B
   a{p}bbb
cccc{p}  d'''.lstrip('\n'))

    def test_limits_width_of_single_line_columns_equal_width(self):
        self._addrow('1234567890', 'abcdefghij')
        # Expect 2 character padding: '1234567890  abcdefghij'  (22 chars wide)
        self._set_max_total_width(20)
        self._assert_formatted_output('123456789  abcdefghi')

    def test_limits_width_of_two_lines_of_equal_length(self):
        self._addrow('123456', 'abcdef')
        self._addrow('XXzzzz', 'YYzzzz')
        self._set_max_total_width(6)
        self._assert_formatted_output('12  ab\nXX  YY')

    def test_truncates_longest_of_two_lines(self):
        self._addrow('123456789', 'a')
        self._addrow('b', 'abcdef')
        self._set_max_total_width(6)
        self._assert_formatted_output('12  a\nb   ab')

    def test_truncates_longest_of_three_lines(self):
        self._addrow('123456789', 'a')
        self._addrow('b', 'abcdef')
        self._addrow('cc', '1234567')
        self._set_max_total_width(6)
        self._assert_formatted_output('12  a\nb   ab\ncc  12')


class TestColumnFormatterThreeColumns(_CaseColumnFormatter, TestCase):
    def test_format_three_columns(self):
        self._addrow('A1', 'BB1', 'CC11')
        self._addrow('A2', 'BB2', 'CC22')
        self._addrow('A3', 'BB3', 'CC33')
        self._assert_number_of_columns(3)
        self._assert_column_widths(2, 3, 4)
        self._assert_formatted_output('A1{p}BB1{p}CC11\nA2{p}BB2{p}CC22\nA3{p}BB3{p}CC33')

    def test_format_three_columns_expands_width(self):
        self._addrow('A')
        self._assert_column_widths(1)
        self._addrow('tuna', 'MJAAAAOOOOOOOOOO')
        self._assert_column_widths(4, 16)
        self._addrow('OOOOOOOOOOAAAAJM', 'B')
        self._assert_column_widths(16, 16)
        self._addrow('42', '0x4E4F4F42')
        self._addrow('C', 'D', 'E')
        self._assert_formatted_output('''
A
tuna            {p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B
42              {p}0x4E4F4F42
C               {p}D               {p}E'''.lstrip('\n'))

    def test_format_three_columns_align_all_left(self):
        self._addrow('A')
        self._addrow('tuna', 'MJAAAAOOOOOOOOOO')
        self._addrow('OOOOOOOOOOAAAAJM', 'B')
        self._addrow('42', '0x4E4F4F42')
        self._addrow('C', 'D', 'E')
        self._setalignment('left', 'left', 'left')
        self._assert_formatted_output('''
A
tuna            {p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B
42              {p}0x4E4F4F42
C               {p}D               {p}E'''.lstrip('\n'))

    def test_format_three_columns_align_all_right(self):
        self._addrow('A')
        self._addrow('tuna', 'MJAAAAOOOOOOOOOO')
        self._addrow('OOOOOOOOOOAAAAJM', 'B')
        self._addrow('42', '0x4E4F4F42')
        self._addrow('C', 'D', 'E')
        self._setalignment('right', 'right', 'right')
        self._assert_formatted_output('''
               A
            tuna{p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}               B
              42{p}      0x4E4F4F42
               C{p}               D{p}E'''.lstrip('\n'))

    def test_format_three_columns_align_mixed(self):
        self._addrow('A')
        self._addrow('tuna', 'MJAAAAOOOOOOOOOO')
        self._addrow('OOOOOOOOOOAAAAJM', 'B')
        self._addrow('42', '0x4E4F4F42')
        self._addrow('C', 'D', 'E')
        self._setalignment('right', 'left', 'right')
        self._assert_formatted_output('''
               A
            tuna{p}MJAAAAOOOOOOOOOO
OOOOOOOOOOAAAAJM{p}B
              42{p}0x4E4F4F42
               C{p}D               {p}E'''.lstrip('\n'))


class TestColorizeQuoted(TestCase):
    def test_colorize_quoted(self):
        # ANSI_COLOR must match actual color. Currently 'LIGHTGREEN_EX'
        ANSI_COLOR = '\x1b[92m'

        def __unescape_ansi(s):
            u = s.replace(ANSI_COLOR, '{COL}').replace(ANSI_RESET_FG, '{RES}')
            return u

        def __check(given, expect):
            assert isinstance(given, str)
            assert isinstance(expect, str)
            actual = colorize_quoted(given)
            _expected = expect.format(COL=ANSI_COLOR, RES=ANSI_RESET_FG)
            self.assertEqual(
                _expected, actual,
                'Expected: {!s}  Actual: {!s}'.format(
                    __unescape_ansi(_expected), __unescape_ansi(actual)
                )
            )

        __check('', '')
        __check('foo', 'foo')
        __check('"', '"')
        __check('""', '""')
        __check(' ""', ' ""')
        __check('"" ', '"" ')
        __check(' "" ', ' "" ')
        __check('"foo', '"foo')
        __check('foo"', 'foo"')
        __check('"foo"', '"{COL}foo{RES}"')
        __check('"foo""', '"{COL}foo{RES}""')
        __check(' "foo', ' "foo')
        __check(' foo"', ' foo"')
        __check(' "foo"', ' "{COL}foo{RES}"')
        __check(' "foo""', ' "{COL}foo{RES}""')
        __check('"foo ', '"foo ')
        __check('foo" ', 'foo" ')
        __check('"foo" ', '"{COL}foo{RES}" ')
        __check('"foo"" ', '"{COL}foo{RES}"" ')
        __check(' "foo ', ' "foo ')
        __check(' foo" ', ' foo" ')
        __check(' "foo" ', ' "{COL}foo{RES}" ')
        __check(' "foo"" ', ' "{COL}foo{RES}"" ')
        __check(' "foo "bar"', ' "{COL}foo {RES}"bar"')
        __check(' foo"x"bar"', ' foo"{COL}x{RES}"bar"')
        __check(' foo"  "bar"', ' foo"{COL}  {RES}"bar"')

        # TODO: This case still fails ..
        # __check(' foo" "bar"', ' foo"{COL} {RES}"bar"')

        __check(' "foo" "bar"', ' "{COL}foo{RES}" "{COL}bar{RES}"')
        __check(' "foo"" "bar"', ' "{COL}foo{RES}""{COL} {RES}"bar"')
        __check(' "a"" ""b"', ' "{COL}a{RES}""{COL} {RES}""{COL}b{RES}"')


class TestMsgColumnate(TestCase):
    def _assert_msg_called_with(self, expected, column_names, row_data):
        with patch('core.view.cli.common.msg') as mock_msg:
            _ = msg_columnate(column_names, row_data)
        mock_msg.assert_called_once_with(expected)

    def test_two_column_names_empty_row_data(self):
        self._assert_msg_called_with(
            'A  B\n',
            column_names=['A', 'B'],
            row_data=[]
        )

    def test_empty_column_names_one_row_of_two_columns(self):
        self._assert_msg_called_with(
            'a  b\n',
            column_names=[],
            row_data=[('a', 'b')]
        )

    def test_empty_column_names_two_rows_of_two_columns(self):
        self._assert_msg_called_with(
            'a  b\nc  d\n',
            column_names=[],
            row_data=[('a', 'b'), ('c', 'd')]
        )

    def test_two_column_names_one_row_of_two_columns(self):
        self._assert_msg_called_with(
            'A  B\na  b\n',
            column_names=['A', 'B'],
            row_data=[('a', 'b')]
        )

    def test_two_column_names_two_rows_of_two_columns(self):
        self._assert_msg_called_with(
            'A  B\na  b\nc  d\n',
            column_names=['A', 'B'],
            row_data=[('a', 'b'), ('c', 'd')]
        )
