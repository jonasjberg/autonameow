# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import logging
import os
import platform
import re
from datetime import datetime

import colorama

from core import constants as C
from util import coercers
from util import process


colorama.init()
log = logging.getLogger(__name__)

BE_QUIET = False


def print_version_info(verbose):
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    def divider_string(length):
        return colorize('-' * length, fore='LIGHTBLACK_EX', style='DIM')

    if verbose:
        _commit_info = process.git_commit_hash()
        if _commit_info:
            # NOTE(jonas): git rev-parse --short HEAD returns different length.
            # Hash string is one extra character on MacOS (git version 2.15.1)
            # compared to Linux (git version 2.7.4).
            _commit = '(commit {!s:7.7})'.format(_commit_info)
        else:
            _commit = ''

        _release_date = 'Released {}'.format(C.STRING_PROGRAM_RELEASE_DATE)

        cf = ColumnFormatter()
        cf.addrow(C.STRING_PROGRAM_NAME, C.STRING_COPYRIGHT_NOTICE)
        cf.addrow('version {}'.format(C.STRING_PROGRAM_VERSION),
                  C.STRING_AUTHOR_EMAIL)
        cf.addrow(_release_date, C.STRING_URL_MAIN)
        cf.addrow(_commit, C.STRING_URL_REPO)
        cf.setalignment('left', 'right')
        columnated_text = str(cf)
        columnated_text_width = cf.max_column_width()

        # TODO: [hardcoded] Uses fixed spaces for alignment.
        # Passing colored texts with ANSI escape sequences messes
        # up the text width detected by the the 'ColumnFormatter' ..
        program_name = colorize(
            '  {}  '.format(C.STRING_PROGRAM_NAME), back='BLUE', fore='BLACK'
        )
        program_slogan = colorize(
            '    Automagic File Renamer by Cats for Cats', fore='BLUE'
        )

        print_stdout('')
        print_stdout(program_name + program_slogan)
        print_stdout(divider_string(columnated_text_width))
        print_stdout(columnated_text)
        print_stdout(divider_string(columnated_text_width))
        print_stdout('')
    else:
        print_stdout('{}'.format(C.STRING_PROGRAM_VERSION))


def print_start_info():
    """
    Prints information on program startup; current date/time, user and platform.
    """
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    user = os.environ.get('USER')
    plat = ' '.join(platform.uname()[:3])
    i = colorize('Started at {d} by {u} on {p}'.format(d=date, u=user, p=plat),
                 style='DIM')
    print_stdout(i)

    log.debug('Started %s version %s', C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION)
    log.debug('Running on Python %s', C.STRING_PYTHON_VERSION)
    log.debug('Hostname: %s', ' '.join(platform.uname()[:3]))
    log.debug('Process ID: %s', os.getpid())


def print_exit_info(exit_code, elapsed_time):
    """
    Prints information on program exit; total execution time and exit code.

    Args:
        exit_code: Program exit status, for display only.
        elapsed_time: Program execution time in seconds.
    """
    # TODO: Show execution time in hours, minutes and seconds if > 60 seconds
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    i = colorize('Finished at {d} after {t:.6f} seconds with exit code '
                 '{c}'.format(d=date, t=elapsed_time, c=exit_code),
                 style='DIM')
    print_stdout(i)


def colorize(text, fore=None, back=None, style=None):
    """
    Adds ANSI formatting to text strings with "colorama".

    The text is returned as-is if no options are specified.

    Args:
        text: The text to colorize.
        fore: Optional foreground color as a string. Available options:
              BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
              LIGHTBLACK_EX, LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX
              LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
        back: Optional background color as a string. Available options:
              BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
              LIGHTBLACK_EX, LIGHTRED_EX LIGHTGREEN_EX, LIGHTYELLOW_EX,
              LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
        style: Optional style settings as a string. Available options:
               DIM, NORMAL, BRIGHT, RESET_ALL

    Returns:
        The given string with the specified coloring and style options applied.
        An empty string is returned if "text" is None.
    """
    if text is None:
        return ''
    if not (fore or back or style):
        return text

    buffer = list()

    if fore:
        fore = fore.upper()
        # assert fore in ('BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA',
        #                 'CYAN', 'WHITE', 'LIGHTBLACK_EX', 'LIGHTRED_EX',
        #                 'LIGHTGREEN_EX', 'LIGHTYELLOW_EX' 'LIGHTBLUE_EX',
        #                 'LIGHTMAGENTA_EX', 'LIGHTCYAN_EX', 'LIGHTWHITE_EX'), (
        #     'Invalid foreground color'
        # )
        buffer.append(getattr(colorama.Fore, fore, None))
    if back:
        back = back.upper()
        buffer.append(getattr(colorama.Back, back, None))
    if style:
        style = style.upper()
        buffer.append(getattr(colorama.Style, style, None))

    buffer.append(text)

    if style:
        buffer.append(colorama.Style.RESET_ALL)
    if back:
        buffer.append(colorama.Back.RESET)
    if fore:
        buffer.append(colorama.Fore.RESET)

    return ''.join(buffer)


def colorize_re_match(text, regex, color=None):
    _re_type = coercers.BUILTIN_REGEX_TYPE
    assert regex and isinstance(regex, _re_type), (
        'Expected type {!s}. Got {!s}'.format(type(_re_type), type(regex))
    )

    if color is not None:
        _color = color
    else:
        _color = 'LIGHTGREEN_EX'

    replacements = list()
    match_iter = regex.findall(text)
    if not match_iter:
        return text

    for match in match_iter:
        replacements.append((match, colorize(match, fore=_color)))

    out = ''
    for old, new in replacements:
        # Find position of the first match:  text = a "B" b "B"
        #                                              ^
        # Work on a bit at a time to avoid replacing the same match.
        # Store from start to the first match + 1 (catch ") in 'temp_text'.
        #
        #          text = 'a "B" b "B"'
        #                     ^
        #     temp_text = 'a "B"'
        #
        # Do replacement in temp_text, append to 'out'. Continue to work
        # on the rest of the text:  text = ' b "B"'
        old_pos = text.find(old)
        strip_to = old_pos + len(old) + 1
        temp_text = text[:strip_to]

        temp_text = temp_text.replace(old, new, 1)
        out = out + temp_text

        text = text[strip_to:]

    if text:
        out = out + text

    return out


RE_ANYTHING_QUOTED = re.compile(r'"([^"]+)"')


def colorize_quoted(text, color=None):
    # TODO: This is still buggy. See unit tests for case that fails.
    return colorize_re_match(text, RE_ANYTHING_QUOTED, color)


def print_stdout(string):
    # NOTE(jonas): colorama has problems with piping to pager ..
    try:
        print(string)
    except BrokenPipeError:
        pass


def msg(message, style=None, ignore_quiet=False):
    """
    Displays a message to the user optionally using preset formatting options.

    Args:
        message: The raw text message to print as a Unicode string.
        style: Optional message type as a Unicode string.
               Should be one of 'info', 'heading', 'section', 'color_quoted'
               or 'highlight'.
        ignore_quiet: Whether to ignore the global quiet ('--quiet') option.

    Raises:
        EncodingBoundaryViolation: Given message is not a Unicode string.
    """
    if not ignore_quiet:
        global BE_QUIET
        if BE_QUIET:
            return

    def _print_default_msg(text):
        colored_text = colorize(text)
        print_stdout(colored_text)

    def _print_info_msg(text):
        prefix = colorize('[info]', fore='LIGHTBLACK_EX')
        colored_text = colorize(text)
        print_stdout(prefix + ' ' + colored_text)

    assert isinstance(message, str)
    if not message:
        return

    if not style:
        _print_default_msg(message)

    elif style == 'info':
        _print_info_msg(message)

    elif style == 'heading':
        heading_underline = C.CLI_MSG_HEADING_CHAR * len(message.strip())
        colored_heading_underline = colorize(heading_underline, style='DIM')
        colored_heading_text = colorize(message, style='BRIGHT')
        print_stdout('\n\n' + colored_heading_text + '\n' + colored_heading_underline)

    elif style == 'section':
        colored_section_text = colorize(message, style='BRIGHT')
        print_stdout('\n' + colored_section_text)

    elif style == 'color_quoted':
        print_stdout(colorize_quoted(message, color='LIGHTGREEN_EX'))

    elif style == 'highlight':
        colored_message = colorize(message, fore='LIGHTWHITE_EX')
        print_stdout(colored_message)

    else:
        log.warning('Unknown message style "%s"', style)
        _print_default_msg(message)


def msg_rename(from_basename, dest_basename, dry_run):
    """
    Displays a message about a rename operation to the user.

    Args:
        from_basename: Original basename of the file to be renamed,
                       as a Unicode string.
        dest_basename: New basename of the file to be renamed, as a Unicode
                       string.
        dry_run: True if the operation was a "dry run"/simulation.

    Raises:
        EncodingBoundaryViolation: Given message is not a Unicode string.
    """
    assert isinstance(from_basename, str)
    assert isinstance(dest_basename, str)

    _name_old = colorize_quoted('"{!s}"'.format(from_basename),
                                color='WHITE')
    _name_new = colorize_quoted('"{!s}"'.format(dest_basename),
                                color='LIGHTGREEN_EX')

    cf = ColumnFormatter(align='right')
    if dry_run:
        cf.addrow('Would have renamed', '{!s}')
    else:
        cf.addrow('Renamed', '{!s}')

    cf.addrow('->', '{!s}')
    column_template = str(cf)
    msg(column_template.format(_name_old, _name_new), ignore_quiet=True)


def msg_possible_rename(from_basename, dest_basename):
    """
    Displays a message about a "possible" rename operation to the user.

    Args:
        from_basename: Original basename of the file that might be renamed,
                       as a Unicode string.
        dest_basename: New basename of the file that might renamed, as a
                       Unicode string.

    Raises:
        EncodingBoundaryViolation: Given message is not a Unicode string.
    """
    assert isinstance(from_basename, str)
    assert isinstance(dest_basename, str)

    _name_old = colorize_quoted('"{!s}"'.format(from_basename),
                                color='WHITE')
    _name_new = colorize_quoted('"{!s}"'.format(dest_basename),
                                color='LIGHTGREEN_EX')

    cf = ColumnFormatter(align='right')
    cf.addrow('About to rename', '{!s}')
    cf.addrow('->', '{!s}')
    column_template = str(cf)
    msg(column_template.format(_name_old, _name_new), ignore_quiet=True)


def _colorize_string_diff(a, b, color, secondary_color, colorize_=None):
    """
    Returns a pair of strings with any differences colorized.

    This function is stolen from 'beets/ui/__init__.py:_colordiff'.
    Copyright 2016, Adrian Sampson.
    """
    if colorize_ is None:
        colorize_ = colorize
    else:
        assert callable(colorize_)

    a_out = list()
    b_out = list()

    from difflib import SequenceMatcher
    matcher = SequenceMatcher(lambda x: False, a, b)
    for op, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        if op == 'equal':
            # In both strings.
            a_out.append(a[a_start:a_end])
            b_out.append(b[b_start:b_end])
        elif op == 'insert':
            # Right only.
            b_out.append(colorize_(b[b_start:b_end], color))
        elif op == 'delete':
            # Left only.
            a_out.append(colorize_(a[a_start:a_end], color))
        elif op == 'replace':
            # Right and left differ. Colorize with 'secondary_color'
            # if it's just a case change.
            if a[a_start:a_end].lower() != b[b_start:b_end].lower():
                c = color
            else:
                c = secondary_color
            a_out.append(colorize_(a[a_start:a_end], c))
            b_out.append(colorize_(b[b_start:b_end], c))
        else:
            assert False

    return ''.join(a_out), ''.join(b_out)


def msg_filename_replacement(before, after):
    _old, _new = _colorize_string_diff(
        before, after,
        C.REPLACEMENT_HIGHLIGHT_COLOR,
        C.REPLACEMENT_SECONDARY_HIGHLIGHT_COLOR
    )
    cf = ColumnFormatter(align='right')
    cf.addrow('Applied replacements:', '{!s}')
    cf.addrow('->', '{!s}')
    _message = str(cf).format(_old, _new)
    msg(_message)


class ColumnFormatter(object):
    """
    Utility formatter for aligning columns of strings.
    The individual column widths are expanded dynamically when
    strings are added. New strings are added a column at a time.

    Each column width is as wide as the widest string contained
    in that column + 'COLUMN_PADDING'.

    Example Usage:    ColumnFormatter cf = ColumnFormatter()
                      cf.addrow('foo', 'bar')
                      cf.addrow('MJAO OAJM', 'baz')
                      cf.addrow('1337', '4E4F4F42')
                      print(str(cf))

    Which would print something like:              foo        bar
                                                   MJAO OAJM  baz
                                                   1337       4E4F4F42

    With 'cf.setalignment('right', 'left'):              foo  bar
                                                   MJAO OAJM  baz
                                                        1337  4E4F4F42
    """
    COLUMN_PADDING = 2
    PADDING_CHAR = ' '
    ALIGNMENT_STRINGS = {
        'left': 'ljust',
        'right': 'rjust'
    }

    def __init__(self, align='left'):
        self._default_align = self.ALIGNMENT_STRINGS.get(align, 'ljust')

        self._column_count = 0
        self._data = list()
        self._column_widths = list()
        self._column_align = list()
        self.max_total_width = None

    def setalignment(self, *args):
        maybe_strings = list(args)
        strings = self._check_types_replace_none(maybe_strings)
        if not strings:
            return

        _column_alignment = list()
        for i in range(0, self.number_columns):
            if i < len(strings) and [s in self.ALIGNMENT_STRINGS.keys() for s in strings]:
                _column_alignment.append(self.ALIGNMENT_STRINGS.get(strings[i]))
            else:
                _column_alignment.append(self._default_align)

        self._column_align = _column_alignment

    @property
    def alignment(self):
        if not self._column_align:
            out = list()
            out.extend(self._default_align for _ in range(self.number_columns))
            return out
        return self._column_align

    @property
    def number_columns(self):
        return self._column_count

    def _update_column_count(self, strings):
        self._column_count = max(self._column_count, len(strings))

    def addrow(self, *args):
        maybe_strings = list(args)

        strings = self._check_types_replace_none(maybe_strings)

        self._update_column_count(strings)
        self._update_column_widths(strings)
        self._data.append(strings)

    def addemptyrow(self):
        self.addrow(' ')

    def _update_column_widths(self, strings):
        new_widths = [len(s) for s in strings]

        if not self._column_widths:
            self._column_widths = new_widths
        else:
            new_column_count = len(new_widths)
            old_column_count = len(self._column_widths)

            # Use the longest array as the "base".
            if new_column_count > old_column_count:
                _max_widths = new_widths
            else:
                _max_widths = self._column_widths

            #   Array A:   [9]  [1]
            #   Array B:   [3]  [7]  [2]  [4]
            #       OUT:   [9]  [7]  [2]  [4]
            #
            # Compare array elements from index 0..len(A) and store the
            # maximum element value in the longer array.
            for i in range(0, min(new_column_count, old_column_count)):
                _max_widths[i] = max(new_widths[i], self._column_widths[i])

            self._column_widths = _max_widths

    @property
    def column_widths(self):
        return self._column_widths

    def max_column_width(self):
        max_width = ((self.number_columns * self.COLUMN_PADDING)
                     + sum(self.column_widths) - self.COLUMN_PADDING)
        return max_width

    @staticmethod
    def _check_types_replace_none(maybe_strings):
        out = list()

        if not maybe_strings:
            return out

        for element in maybe_strings:
            if element is None:
                out.append('')
            elif not isinstance(element, str):
                raise TypeError(
                    'Expected Unicode str. Got {!s}'.format(type(element))
                )
            else:
                out.append(element.strip())

        return out

    def __str__(self):
        if not self._data:
            return ''

        padding = self.PADDING_CHAR * self.COLUMN_PADDING
        adjusted_column_widths = list(self.column_widths)

        # Truncate column widths if 'self.max_total_width' is not None.
        if self.max_total_width:
            assert isinstance(self.max_total_width, int)

            # Padding between all but the last column.
            total_padding_width = len(padding) * (self.number_columns - 1)

            def _get_total_width():
                total_column_width = sum(adjusted_column_widths)
                return total_column_width + total_padding_width

            iteration_count = 0
            total_width = _get_total_width()
            while total_width > self.max_total_width:
                widest_column_width = max(w for w in adjusted_column_widths)

                width_decrement = ((total_width - self.max_total_width) // 5) or 1

                for i in range(0, self.number_columns):
                    if adjusted_column_widths[i] == widest_column_width:
                        adjusted_column_widths[i] -= width_decrement
                        break

                iteration_count += 1
                if iteration_count > 100:
                    break

                total_width = _get_total_width()

        output_lines = list()
        for row in self._data:
            row_columns = list()
            for row_column, column_width, column_alignment in zip(
                row, adjusted_column_widths, self.alignment
            ):
                aligned_row_column = getattr(row_column, column_alignment)(column_width)

                if column_alignment == 'ljust':
                    truncated_row_column = aligned_row_column[:column_width]
                elif column_alignment == 'rjust':
                    truncated_row_column = aligned_row_column[:column_width]
                else:
                    truncated_row_column = aligned_row_column

                row_columns.append(truncated_row_column)

            output_lines.append(padding.join(row_columns))

        return '\n'.join(line.rstrip() for line in output_lines)


def msg_columnate(column_names, row_data, alignment=None):
    cf = ColumnFormatter()
    if alignment:
        # cf.setalignment('right', 'left')
        cf.setalignment(*alignment)

    if column_names:
        cf.addrow(*column_names)

    for data in row_data:
        cf.addrow(*data)

    msg(str(cf) + '\n')


def silence():
    global BE_QUIET
    log.disabled = True
    BE_QUIET = True


def unsilence():
    global BE_QUIET
    log.disabled = False
    BE_QUIET = False
