#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import logging
import traceback


log = logging.getLogger(__name__)


class EventHandler(object):
    """
    Stores callables and forwards calls to all stored callables.
    """
    def __init__(self, name):
        self.name = name
        self.callables = set()

    def add(self, func):
        assert callable(func), type(func)
        self.callables.add(func)

    def __call__(self, *args, **kwargs):
        log.debug('%s called with args %s kwargs %s', self, args, kwargs)
        for func in self.callables:
            # Make sure all callables are called in case of an unhandled
            # exception. This really "should" NOT happen, it is assumed that
            # bound callables will responsibly handle any exceptions locally.
            try:
                func(*args, **kwargs)
            except Exception as e:
                log.critical(
                    '%s caught exception when called with args %s '
                    'kwargs %s :: %s', self, args, kwargs, e
                )
                log.critical(
                    '%s caught exception %s', self, traceback.format_exc()
                )

    def __str__(self):
        return '<{!s}({!s})>'.format(self.__class__.__name__, self.name)


class EventDispatcher(object):
    """
    Provides any part of the program with access to registered event handlers.
    Example usage:

    >>> from core.event import EventDispatcher
    >>> d = EventDispatcher(EventHandler('on_startup'))
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
    def __init__(self, *event_handlers):
        self._event_handlers = dict()
        self._register_event_handlers(event_handlers)

    def _register_event_handlers(self, event_handlers):
        for event_handler in event_handlers:
            self._event_handlers[event_handler.name] = event_handler

    def __getattr__(self, item):
        event_handler = self._event_handlers.get(item)
        if event_handler:
            log.debug('%s returning event handler "%s"', self, event_handler)
            return event_handler

        raise AssertionError('Invalid event handler: "{!s}"'.format(item))

    def __str__(self):
        return self.__class__.__name__


dispatcher = EventDispatcher(
    EventHandler('on_startup'),
    EventHandler('on_shutdown'),
    EventHandler('on_config_changed'),
)
