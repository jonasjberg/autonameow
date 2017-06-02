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
import platform
from datetime import datetime

from colorama import (
    Fore,
    Back
)

from core import version


def print_ascii_banner():
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    # TODO: Text alignment depends on manually hardcoding spaces! FIX!

    print(Fore.LIGHTBLUE_EX +
           '''
   ###   ### ### ####### #####  ###  ##   ###   ##   ## ####### #####  ### ###
  #####  ### ###   ###  ### ### #### ##  #####  # # ### ####   ####### ### ###
 ### ### ### ###   ###  ### ### ####### ### ### ####### ###### ### ### #######
 ####### #######   ###  ####### ### ### ####### ### ### ####   ### ### ### ###
 ### ###  ### ##   ###   #####  ### ### ### ### ### ### ####### #####  ##   ##
    ''' + Fore.RESET)
    colortitle = Back.LIGHTYELLOW_EX + Fore.YELLOW + \
        ' ' + version.__title__.lower() + ' ' + \
        Back.RESET + Fore.RESET
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
    print(Fore.LIGHTBLACK_EX +
          'Started at {date} by {user} on {platform}'.format(
              date=datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
              user=os.environ.get('USER'),
              platform=' '.join(platform.uname()[:3])) +
          Fore.RESET)


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

    print(Fore.LIGHTBLACK_EX +
          'Finished at {} after {:.6f} seconds '
          'with exit code {}'.format(date, elapsed_time, exit_code) +
          Fore.RESET)


def blue_text(text):
    return Fore.LIGHTBLACK_EX + text + Fore.RESET


def print_msg(message):
    out = blue_text()