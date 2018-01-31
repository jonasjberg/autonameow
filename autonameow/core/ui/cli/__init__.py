# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from . import options
from .argparser import get_argparser
from .common import (
    colorize,
    ColumnFormatter,
    colorize_re_match,
    colorize_quoted,
    msg,
    msg_possible_rename,
    msg_rename,
    msg_replacement,
    print_exit_info,
    print_start_info,
    print_version_info,
    silence,
    unsilence
)
from .prompt import (
    ask_confirm,
    field_selection_prompt,
    meowuri_prompt
)
