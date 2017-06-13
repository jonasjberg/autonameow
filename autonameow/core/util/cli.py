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

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

from core import (
    version,
    constants
)


def print_ascii_banner():
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    # TODO: Text alignment depends on manually hardcoding spaces! FIX!

    ascii_banner = colorize(
           '''
   ###   ### ### ####### #####  ###  ##   ###   ##   ## ####### #####  ### ###
  #####  ### ###   ###  ### ### #### ##  #####  # # ### ####   ####### ### ###
 ### ### ### ###   ###  ### ### ####### ### ### ####### ###### ### ### #######
 ####### #######   ###  ####### ### ### ####### ### ### ####   ### ### ### ###
 ### ###  ### ##   ###   #####  ### ### ### ### ### ### ####### #####  ##   ##
    ''', fore='LIGHTBLUE_EX')

    print(ascii_banner)

    colortitle = colorize(' ' + version.__title__.lower() + ' ',
                          back='BLUE', fore='BLACK')
    toplineleft = ' {title}  version {ver}'.format(title=colortitle,
                                                   ver=version.__version__)
    toplineright = version.__copyright__
    print(('{:<}{:>50}'.format(toplineleft, toplineright)))
    print(('{:>78}'.format(version.__url__)))
    print(('{:>78}'.format(version.__email__)))
    print('')


def print_start_info():
    """
    Prints information on program startup; current date/time, user and platform.
    """
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    user = os.environ.get('USER')
    plat = ' '.join(platform.uname()[:3])
    i = colorize('Started at {d} by {u} on {p}'.format(d=date, u=user, p=plat),
                 fore='LIGHTBLACK_EX')
    print(i)

    logging.debug('Started {} version {}'.format(version.__title__,
                                                 version.__version__))
    logging.debug('Running on Python {}'.format(constants.PYTHON_VERSION))
    logging.debug('Hostname: {}'.format(' '.join(platform.uname()[:3])))
    logging.debug('Process ID: {}'.format(os.getpid()))


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
                 fore='LIGHTBLACK_EX')
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
        text is returned as-is.
    """
    if colorama:
        buffer = []
        if fore:
            buffer.append(getattr(colorama.Fore, fore.upper(), None))
        if back:
            buffer.append(getattr(colorama.Back, back.upper(), None))
        if style:
            buffer.append(getattr(colorama.Style, style.upper(), None))

        buffer.append(text)
        # buffer = filter(None, buffer)
        buffer.append(colorama.Fore.RESET + colorama.Back.RESET + colorama.Style.RESET_ALL)
        return ''.join(buffer)
    else:
        return text


def msg(message, type=None, log=False):
    """
    Displays a message to the user using preset formatting options.

    Args:
        message: The raw text message to print as a string.
        type: Optional message type.
        log: Displays and logs the message if True. Defaults to False.
    """
    def print_default_msg(text):
        print(colorize(text))

    def print_info_msg(text):
        prefix = colorize('[info]', fore='LIGHTBLACK_EX')
        colored_text = colorize(text)
        print(prefix + ' ' + colored_text)

    def colorize_quoted(text):
        # match_iter = re.findall(r'"(.*?)"', text)
        # TODO: Fix this! Does not work for string like;
        #       'Would do "Word.word" -> "1234-56-78 Word.word" ..'
        match_iter = re.findall(r'"([^"]*)"', text)

        replacements = []
        for match in match_iter:
            replacements.append((match, colorize(match, fore='LIGHTGREEN_EX')))

        for old, new in replacements:
            text = text.replace(old, new, 1)

        return text

    # TODO: Respect '--quiet' option. Suppress output.

    if not message:
        return

    if not type:
        print_default_msg(message)
        if log:
            logging.info(message)
    elif type == 'info':
        print_info_msg(message)
        if log:
            logging.info(message)
    elif type == 'heading':
        print_default_msg(message)
        print_default_msg('=' * len(message))
        print_default_msg('')
    elif type == 'color_quoted':
        print(colorize_quoted(message))
    else:
        print_default_msg(message)
        if log:
            logging.info(message)


if __name__ == '__main__':
    msg('text printed by msg()')
    msg('text printed by msg() with type="info"', type='info')
    msg('text printed by msg() with type="info", log=True',
        type='info', log=True)
    msg('text printed by msg() with type="color_quoted" no "yes" no',
        type='color_quoted')
