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

import logging

from core import constants as C
from core import (
    plugin_handler,
    providers
)
from core.model import MeowURI


log = logging.getLogger(__name__)


class BasePlugin(object):
    # Last part of the full MeowURI ('guessit', 'microsoft_vision', ..)
    MEOWURI_LEAF = C.UNDEFINED_MEOWURI_PART

    # Set at first call to 'meowuri_prefix()'.
    _meowuri_prefix = None

    # Dictionary with plugin-specific information, keyed by the fields that
    # the raw source produces. Stores information on types, etc..
    FIELD_LOOKUP = dict()

    # TODO: Hack ..
    coerce_field_value = providers.ProviderMixin.coerce_field_value

    def __init__(self, display_name=None):
        if display_name:
            self.display_name = display_name
        else:
            self.display_name = self.__class__.__name__

        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.request_data = plugin_handler.request_global_data

    def __call__(self, source, *args, **kwargs):
        return self.execute(source)

    @classmethod
    def meowuri_prefix(cls):
        if not cls._meowuri_prefix:
            _leaf = cls.__module__.split('_')[0] or cls.MEOWURI_LEAF
            cls._meowuri_prefix = MeowURI(
                C.MEOWURI_ROOT_SOURCE_PLUGINS, _leaf
            )
        return cls._meowuri_prefix

    def can_handle(self, fileobject):
        """
        Tests if this plugin class can handle the given file object.

        Args:
            fileobject: The file to test as an instance of 'FileObject'.

        Returns:
            True if the plugin class can handle the given file, else False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def execute(self, fileobject):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def test_init(cls):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def metainfo(self):
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        return dict(self.FIELD_LOOKUP)

    def __str__(self):
        return self.display_name
