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

from .cli import *


# NOTE(jonas): Pass only Unicode strings to the UI.


# This package is intended to be the interface to multiple containing
# subpackages that each implement different UIs.
#
# There is currently only a command-line interface, so this interface
# does not exist. BUT it might be good to implement the interface only once
# another UI is added and the real use and requirements are clearer anyway.
#
# For now, most of the core code should strive to call 'ui.msg()' instead of
# using 'ui.cli.msg()' directly, even if future addition of an alternative
# 'msg()' implementation will require massive rework..

# TODO: [TD0111] Separate abstract user interaction from UI specifics.
