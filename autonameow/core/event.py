#!/usr/bin/env python3
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


log = logging.getLogger(__name__)


class EventHandler(object):
    def __init__(self):
        self.callables = set()

    def add(self, func):
        assert callable(func), type(func)
        self.callables.add(func)

    def __call__(self, *args, **kwargs):
        log.debug(
            '{!s} called with args {!s} kwargs {!s}'.format(self, args, kwargs)
        )
        for func in self.callables:
            func(*args, **kwargs)

    def __str__(self):
        return self.__class__.__name__


class EventDispatcher(object):
    """
    Provides access to predefined event handlers to any part of the program.
    Example usage:

    >>> from core.event import EventDispatcher
    >>> d = EventDispatcher()
    >>> def _on_event_func(*args, **kwargs):
    ...     arg_foo = kwargs.get('foo')
    ...     print(*args, arg_foo)
    ...
    >>> # Bind a callable to the 'on_event' event handler.
    >>> d.on_startup.add(_on_event_func)

    >>> # Trigger the 'on_event' event and call all bound callables.
    >>> d.on_startup(1337, foo='bar')
    1337 bar
    """
    def __init__(self):
        self.log = logging.getLogger('{}.{!s}'.format(__name__, self))
        self._event_handlers = {
            'on_startup': EventHandler(),
            'on_shutdown': EventHandler(),
            'on_config_changed': EventHandler()
        }

    def _get_event_handlers(self, name):
        event_handlers = self._event_handlers.get(name)
        if event_handlers:
            self.log.debug('{!s} returning event handler "{!s}"'.format(self, name))
            return event_handlers

        msg = '{!s} get called with nonexistent event handler "{!s}"'.format(self, name)
        self.log.critical(msg)
        raise AssertionError(msg)

    def __getattr__(self, item):
        return self._get_event_handlers(item)

    def __str__(self):
        return self.__class__.__name__


dispatcher = EventDispatcher()
