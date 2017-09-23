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

from core import plugin_handler
from core import constants as C


class BasePlugin(object):
    # Last part of the full MeowURI ('guessit', 'microsoft_vision', ..)
    MEOWURI_LEAF = C.UNDEFINED_MEOWURI_PART

    def __init__(self, display_name=None):
        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.__class__.__name__

        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.request_data = plugin_handler.request_data

    def add_results(self, file_object, meowuri_leaf, data):
        if data is None:
            return

        meowuri = '{}.{}'.format(self.meowuri(), meowuri_leaf)
        #self.log.debug(
        #    '{!s} passing "{}" to "add_results" callback'.format(self, meowuri)
        #)
        plugin_handler.collect_results(file_object, meowuri, data)

    def __call__(self, source, *args, **kwargs):
        self.execute(source)

    @classmethod
    def meowuri(cls):
        _leaf = cls.__module__.split('_')[0] or cls.MEOWURI_LEAF

        return '{root}{sep}{leaf}'.format(
            root=C.MEOWURI_ROOT_PLUGINS, sep=C.MEOWURI_SEPARATOR,
            leaf=_leaf
        )

    def can_handle(self, file_object):
        """
        Tests if this plugin class can handle the given file object.

        Args:
            file_object: The file to test as an instance of 'FileObject'.

        Returns:
            True if the plugin class can handle the given file, else False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def execute(self, file_object):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return self.display_name

    @classmethod
    def test_init(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')
