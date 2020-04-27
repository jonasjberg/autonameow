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

__all__ = [
    '__author__',
    '__copyright__',
    '__email__',
    '__license__',
    '__title__',
    '__version__',
    '__version_info__',
    '__url__',
    '__url_repo__',
]

__title__ = 'autonameow'
__version_info__ = (0, 6, 0)
__version__ = '.'.join(map(str, __version_info__))
__author__ = 'Jonas Sjöberg'
__email__ = 'autonameow@jonasjberg.com'
__url__ = 'www.jonasjberg.com'
__url_repo__ = 'www.github.com/jonasjberg/autonameow'
__license__ = 'GNU General Public License Version 2'
__copyright__ = 'Copyright(c)2016-2020 {}'.format(__author__)


# TODO: Automatically update this when tagging a new version.
# TODO: [TD0145] Add script for automating release of a new version.
RELEASE_DATE = '2020-04-27'
