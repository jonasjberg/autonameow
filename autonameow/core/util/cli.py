#!/usr/bin/env python3
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

import os
import re
import platform
from datetime import datetime
import logging

from core.util import sanity

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

import core
from core import (
    util,
    types
)
from core import constants as C


log = logging.getLogger(__name__)


BE_QUIET = False


def print_ascii_banner():
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    # TODO: [hardcoded] Text alignment depends on manually hardcoding spaces.

    ascii_banner = colorize(
        '''
   ###   ### ### ####### #####  ###  ##   ###   ##   ## ####### #####  ### ###
  #####  ### ###   ###  ### ### #### ##  #####  # # ### ####   ####### ### ###
 ### ### ### ###   ###  ### ### ####### ### ### ####### ###### ### ### #######
 ####### #######   ###  ####### ### ### ####### ### ### ####   ### ### ### ###
 ### ###  ### ##   ###   #####  ### ### ### ### ### ### ####### #####  ##   ##
    ''', fore='LIGHTBLUE_EX')

    print(ascii_banner)

    colortitle = colorize(' ' + C.STRING_PROGRAM_NAME + ' ',
                          back='BLUE', fore='BLACK')
    toplineleft = ' {title}  version {v}'.format(title=colortitle,
                                                 v=C.STRING_PROGRAM_VERSION)
    toplineright = core.version.__copyright__
    print(('{:<}{:>49}'.format(toplineleft, toplineright)))
    print(('{:>78}'.format(core.version.__email__)))
    print(('{:>78}'.format(core.version.__url__)))
    print(('{:>78}'.format(core.version.__url_repo__)))
    print('')


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
    sanity.check_isinstance(regex, types.BUILTIN_REGEX_TYPE)

    if color is not None:
        _color = color
    else:
        _color = 'LIGHTGREEN_EX'

    replacements = []
    match_iter = regex.findall(text)
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


RE_ANYTHING_QUOTED = re.compile(r'"([^"]*)"')


def colorize_quoted(text, color=None):
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
        print(colorize_quoted(message))

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
        '"{!s}"'.format(util.displayable_path(from_basename)),
        color='WHITE'
    )
    _name_new = colorize_quoted(
        '"{!s}"'.format(util.displayable_path(dest_basename)),
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


class ColumnFormatter(object):
    """
    Utility formatter for printing columns of string.
    All column widths are set to the widest entry in any column.
    """
    COLUMN_PADDING = 2

    def __init__(self, align='left'):
        self._columns = 0
        self._data = []
        self._column_widths = []
        self._align = 'ljust' if align == 'left' else 'rjust'

    @property
    def number_columns(self):
        return self._columns

    def _update_number_columns(self, count):
        if isinstance(count, int) and count > self._columns:
            self._columns = count

    def addrow(self, *args):
        maybe_strings = list(args)

        strings = self._check_types_replace_none(maybe_strings)

        self._update_number_columns(len(strings))
        self._update_column_widths(strings)
        self._data.append(strings)

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

        out = []
        for row in self._data:
            out.append(
                "".join(getattr(word, self._align)(width + self.COLUMN_PADDING)
                        for word, width in zip(row, self._column_widths))
            )

        return '\n'.join(s.rstrip() for s in out if s.strip())


def silence():
    global BE_QUIET
    log.disabled = True
    BE_QUIET = True


def unsilence():
    global BE_QUIET
    log.disabled = False
    BE_QUIET = False


if __name__ == '__main__':
    msg('text printed by msg()')
    msg('text printed by msg() with type="info"', style='info')
    msg('text printed by msg() with type="info", log=True',
        style='info', add_info_log=True)
    msg('text printed by msg() with type="color_quoted" no "yes" no',
        style='color_quoted')

    msg('Word "1234-56 word" -> "1234-56 word"', style='color_quoted')
    msg('Word "word 1234-56" -> "1234-56 word"', style='color_quoted')

    msg('A "b 123" -> A "b 123"', style='color_quoted')
    print(colorize('foo', fore='RED'))
    print(colorize('foo', fore='GREEN'))
    print(colorize('foo', fore='BLUE'))
    print(colorize('foo', back='RED'))
    print(colorize('foo', back='GREEN'))
    print(colorize('foo', back='BLUE'))

    print(colorize('foo', style='NORMAL'))
    print(colorize('foo', style='DIM'))
    print(colorize('foo', style='BRIGHT'))

    print(colorize('foo', fore='RED', back='RED'))
    print(colorize('foo', fore='GREEN', back='RED'))
    print(colorize('foo', fore='BLUE', back='RED'))
    print(colorize('foo', fore='RED', back='GREEN'))
    print(colorize('foo', fore='GREEN', back='GREEN'))
    print(colorize('foo', fore='BLUE', back='GREEN'))
    print(colorize('foo', fore='RED', back='BLUE'))
    print(colorize('foo', fore='GREEN', back='BLUE'))
    print(colorize('foo', fore='BLUE', back='BLUE'))
