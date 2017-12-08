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

import logging
import os
import platform
import re
from datetime import datetime

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

from core import constants as C
from core import (
    types,
    version
)
import util
from util import encoding as enc


log = logging.getLogger(__name__)
BE_QUIET = False


def print_version_info(verbose):
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    def divider_string(length):
        return colorize('-' * length, fore='LIGHTBLACK_EX', style='DIM')

    if verbose:
        print('')
        print(
            colorize('  {}  '.format(C.STRING_PROGRAM_NAME),
                     back='BLUE', fore='BLACK') +
            colorize('  Automagic File Renamer by Cats for Cats', fore='BLUE')
        )

        _commit_info = util.git_commit_hash()
        if _commit_info:
            _commit = '(commit {!s})'.format(_commit_info)
        else:
            _commit = ''

        cf = ColumnFormatter()
        cf.addrow(C.STRING_PROGRAM_NAME, version.__copyright__)
        cf.addrow('version {}'.format(C.STRING_PROGRAM_VERSION),
                  version.__email__)
        cf.addrow(_commit, version.__url__)
        cf.addrow('', version.__url_repo__)
        cf.setalignment('left', 'right')
        columnated_text = str(cf)
        columnated_text_width = cf.max_column_width()

        print(divider_string(columnated_text_width))
        print(columnated_text)
        print(divider_string(columnated_text_width))
        print('')
    else:
        print('{}'.format(C.STRING_PROGRAM_VERSION))


def print_start_info():
    """
    Prints information on program startup; current date/time, user and platform.
    """
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    user = os.environ.get('USER')
    plat = ' '.join(platform.uname()[:3])
    i = colorize('Started at {d} by {u} on {p}'.format(d=date, u=user, p=plat),
                 style='DIM')
    print(i)

    log.debug('Started {} version {}'.format(C.STRING_PROGRAM_NAME,
                                             C.STRING_PROGRAM_VERSION))
    log.debug('Running on Python {}'.format(C.STRING_PYTHON_VERSION))
    log.debug('Hostname: {}'.format(' '.join(platform.uname()[:3])))
    log.debug('Process ID: {}'.format(os.getpid()))


def print_exit_info(exit_code, elapsed_time):
    """
    Prints information on program exit; total execution time and exit code.

    Args:
        exit_code: Program exit status, for display only.
        elapsed_time: Program execution time in seconds.
    """

    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    # TODO: Format the execution time to minutes and seconds if it exceeds
    #       60 seconds, hours, minutes and seconds if it exceeds 60 minutes ..

    i = colorize('Finished at {d} after {t:.6f} seconds with exit code '
                 '{c}'.format(d=date, t=elapsed_time, c=exit_code),
                 style='DIM')
    print(i)


def colorize(text, fore=None, back=None, style=None):
    """
    Adds ANSI formatting to text strings with "colorama".

    The text is returned as-is if the top-level import of "colorama" failed.

    Refer the "colorama" library documentation for additional information;
        https://pypi.python.org/pypi/colorama

    Args:
        text: The text to colorize.
        fore: Optional foreground color as a string. Available options;
              BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
              LIGHTBLACK_EX, LIGHTRED_EX, LIGHTGREEN_EX, LIGHTYELLOW_EX
              LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
        back: Optional background color as a string. Available options;
              BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
              LIGHTBLACK_EX, LIGHTRED_EX LIGHTGREEN_EX, LIGHTYELLOW_EX,
              LIGHTBLUE_EX, LIGHTMAGENTA_EX, LIGHTCYAN_EX, LIGHTWHITE_EX
        style: Optional style settings as a string. Available options;
               DIM, NORMAL, BRIGHT, RESET_ALL

    Returns:
        The given string with the specified coloring and style options applied.
        If no options are specified or if "colorama" is not available, the
        text is returned as-is. If "text" is None, an empty string is returned.
    """
    if text is None:
        return ''
    if not (fore or back or style) or not colorama:
        return text

    buffer = []

    if fore:
        buffer.append(getattr(colorama.Fore, fore.upper(), None))
    if back:
        buffer.append(getattr(colorama.Back, back.upper(), None))
    if style:
        buffer.append(getattr(colorama.Style, style.upper(), None))

    buffer.append(text)

    if style:
        buffer.append(colorama.Style.RESET_ALL)
    if back:
        buffer.append(colorama.Back.RESET)
    if fore:
        buffer.append(colorama.Fore.RESET)

    return ''.join(buffer)


def colorize_re_match(text, regex, color=None):
    _re_type = types.BUILTIN_REGEX_TYPE
    assert regex and isinstance(regex, _re_type), (
           'Expected type {!s}. Got {!s}'.format(type(_re_type), type(regex)))

    if color is not None:
        _color = color
    else:
        _color = 'LIGHTGREEN_EX'

    replacements = []
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


def msg(message, style=None, add_info_log=False, ignore_quiet=False):
    """
    Displays a message to the user using preset formatting options.

    Args:
        message: The raw text message to print as a string.
        style: Optional message type.
        add_info_log: Displays and logs the message if True. Defaults to False.
    """
    if not ignore_quiet:
        global BE_QUIET
        if BE_QUIET:
            return

    def print_default_msg(text):
        print(colorize(text))

    def print_info_msg(text):
        prefix = colorize('[info]', fore='LIGHTBLACK_EX')
        colored_text = colorize(text)
        print(prefix + ' ' + colored_text)

    if not message:
        return

    if not style:
        print_default_msg(message)
        if add_info_log:
            log.info(message)

    elif style == 'info':
        print_info_msg(message)
        if add_info_log:
            log.info(message)

    elif style == 'heading':
        _heading_underline = C.CLI_MSG_HEADING_CHAR * len(message)
        _colored_heading_underline = colorize(_heading_underline, style='DIM')
        _colored_heading_text = colorize(message, style='BRIGHT')
        print('\n')
        print(_colored_heading_text)
        print(_colored_heading_underline)

    elif style == 'color_quoted':
        print(colorize_quoted(message, color='LIGHTGREEN_EX'))

    else:
        print_default_msg(message)
        if add_info_log:
            log.info(message)


def msg_rename(from_basename, dest_basename, dry_run):
    """
    Displays a message about a rename operation to the user.

    Args:
        from_basename: The original basename of the file to be renamed.
        dest_basename: The new basename of the file to be renamed.
        dry_run: True if the operation was a "dry run"/simulation.
    """
    _name_old = colorize_quoted(
        '"{!s}"'.format(enc.displayable_path(from_basename)),
        color='WHITE'
    )
    _name_new = colorize_quoted(
        '"{!s}"'.format(enc.displayable_path(dest_basename)),
        color='LIGHTGREEN_EX'
    )

    cf = ColumnFormatter(align='right')
    if dry_run:
        cf.addrow('Would have renamed', '{!s}')
    else:
        cf.addrow('Renamed', '{!s}')

    cf.addrow('->', '{!s}')
    _message = str(cf)
    msg(_message.format(_name_old, _name_new), ignore_quiet=True)


def _colorize_replacement(original, replacement, regex, color):
    _colored_replacement = colorize(replacement, fore=color)
    return re.sub(regex, _colored_replacement, original)


def displayable_replacement(original, replacement, regex, color):
    if re.sub(regex, replacement, original) == original:
        # Something was matched but replaced with the same string.
        return original, original

    colored_old = colorize_re_match(original, regex=regex, color=color)
    colored_new = _colorize_replacement(original, replacement, regex, color)
    return colored_old, colored_new


def msg_replacement(original, replacement, regex):
    _old, _new = displayable_replacement(original, replacement, regex,
                                         C.REPLACEMENT_HIGHLIGHT_COLOR)
    cf = ColumnFormatter(align='right')
    cf.addrow('Applied replacement:', '{!s}')
    cf.addrow('->', '{!s}')
    _message = str(cf)
    msg(_message.format(_old, _new), ignore_quiet=False)

    # TODO: [TD0096] Fix invalid colouring if the replacement is the last character.
    #
    # Applying custom replacement. Regex: "re.compile('\\.$')" Replacement: ""
    # Applying custom replacement: "2007-04-23_12-comments.png." -> "2007-04-23_12-comments.png"
    #                                                     ^   ^
    #                 Should not be colored red, but is --'   '-- Should be red, but isn't ..


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
        self._column_count = 0
        self._data = []
        self._column_widths = []
        self._default_align = self.ALIGNMENT_STRINGS.get(align, 'ljust')
        self._column_align = []

    def setalignment(self, *args):
        maybe_strings = list(args)
        strings = self._check_types_replace_none(maybe_strings)
        if not strings:
            return

        _column_alignment = []
        for i in range(0, self.number_columns):
            if i < len(strings) and [s in self.ALIGNMENT_STRINGS.keys() for s in strings]:
                _column_alignment.append(self.ALIGNMENT_STRINGS.get(strings[i]))
            else:
                _column_alignment.append(self._default_align)

        self._column_align = _column_alignment

    @property
    def alignment(self):
        if not self._column_align:
            out = []
            out.extend(self._default_align for _ in range(self.number_columns))
            return out
        else:
            return self._column_align

    @property
    def number_columns(self):
        return self._column_count

    def _update_number_columns(self, strings):
        count = len(strings)
        if count > self._column_count:
            self._column_count = count

    def addrow(self, *args):
        maybe_strings = list(args)

        strings = self._check_types_replace_none(maybe_strings)

        self._update_number_columns(strings)
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
        out = []

        if not maybe_strings:
            return out

        for _element in maybe_strings:
            if _element is None:
                out.append('')
            elif not isinstance(_element, str):
                raise TypeError(
                    'Expected Unicode str. Got "{!s}"'.format(type(_element))
                )
            else:
                out.append(_element.strip())

        return out

    def __str__(self):
        if not self._data:
            return ''

        padding = self.PADDING_CHAR * self.COLUMN_PADDING

        lines = []
        for row in self._data:
            lines.append(
                padding.join(
                    getattr(word, align)(width)
                    for word, width, align in zip(
                        row, self._column_widths,
                        self.alignment
                    )
                )
            )

        return '\n'.join(l.rstrip() for l in lines)


def silence():
    global BE_QUIET
    log.disabled = True
    BE_QUIET = True


def unsilence():
    global BE_QUIET
    log.disabled = False
    BE_QUIET = False
