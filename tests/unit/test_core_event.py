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

from unittest import TestCase
from unittest.mock import Mock


def _get_event_dispatcher():
    from core.event import EventDispatcher
    return EventDispatcher(
        event_handlers={
            'on_startup': _get_event_handler(),
            'on_shutdown': _get_event_handler(),
            'on_config_changed': _get_event_handler(),
        }
    )


def _get_event_handler(name=None):
    from core.event import EventHandler
    return EventHandler(name or 'UNNAMED')


class TestEventHandler(TestCase):
    def test_instantiated_event_handler_is_not_none(self):
        handler = _get_event_handler()
        self.assertIsNotNone(handler)

    def test_raises_assertion_error_given_non_callable(self):
        handler = _get_event_handler()
        for not_callable in [None, 'foo', [lambda x: x]]:
            with self.assertRaises(AssertionError):
                handler.add(not_callable)

    def _assert_calls_added_callable_with(self, *args, **kwargs):
        handler = _get_event_handler()
        mock_callable = Mock()

        handler(*args, **kwargs)
        mock_callable.assert_not_called()

        handler.add(mock_callable)
        handler(*args, **kwargs)
        mock_callable.assert_called_once_with(*args, **kwargs)

    def _assert_calls_all_added_callables_with(self, *args, **kwargs):
        handler = _get_event_handler()
        mock_callable_a = Mock()
        mock_callable_b = Mock()

        handler(*args, **kwargs)
        mock_callable_a.assert_not_called()
        mock_callable_b.assert_not_called()

        handler.add(mock_callable_a)
        handler.add(mock_callable_b)
        handler(*args, **kwargs)
        mock_callable_a.assert_called_once_with(*args, **kwargs)
        mock_callable_b.assert_called_once_with(*args, **kwargs)

    def test_calls_added_callable_without_args(self):
        self._assert_calls_added_callable_with()

    def test_calls_added_callable_with_args(self):
        self._assert_calls_added_callable_with('A', 'B')

    def test_calls_added_callable_with_kwargs(self):
        self._assert_calls_added_callable_with(x='A', y='B')

    def test_calls_added_callable_with_args_and_kwargs(self):
        self._assert_calls_added_callable_with('A', 'B', x='C', y='D')

    def test_calls_all_added_callables_with_args_and_kwargs(self):
        self._assert_calls_all_added_callables_with('A', 'B', x='C', y='D')

    def test___str__(self):
        handler = _get_event_handler(name='foo')
        self.assertEqual('<EventHandler(foo)>', str(handler))

    def test_all_callables_are_called_even_after_uncaught_exception(self):
        handler = _get_event_handler()
        mock_callable_a = Mock()
        broken_callable = lambda _: 1 / 0
        mock_callable_c = Mock()

        handler.add(mock_callable_a)
        handler.add(broken_callable)
        handler.add(mock_callable_c)
        handler('foo')
        mock_callable_a.assert_called_once_with('foo')
        mock_callable_c.assert_called_once_with('foo')


class TestEventDispatcher(TestCase):
    def test_instantiated_event_dispatcher_is_not_none(self):
        dispatcher = _get_event_dispatcher()
        self.assertIsNotNone(dispatcher)

    def _assert_has_callable_attribute(self, attribute_name):
        assert isinstance(attribute_name, str), 'failed test sanity-check'

        dispatcher = _get_event_dispatcher()
        self.assertTrue(
            hasattr(dispatcher, attribute_name),
            'Expected dispatcher to have attribute {}'.format(attribute_name)
        )
        dispatcher_attribute = getattr(dispatcher, attribute_name)
        self.assertTrue(
            callable(dispatcher_attribute),
            'Expected attribute {} to be callable'.format(attribute_name)
        )

    def test_dispatcher_has_default_hardcoded_attribute_on_startup(self):
        self._assert_has_callable_attribute('on_startup')

    def test_dispatcher_has_default_hardcoded_attribute_on_shutdown(self):
        self._assert_has_callable_attribute('on_shutdown')

    def test_dispatcher_has_default_hardcoded_attribute_on_config_changed(self):
        self._assert_has_callable_attribute('on_config_changed')

    def test_raises_assertion_error_if_handler_does_not_exist(self):
        dispatcher = _get_event_dispatcher()
        for bad_arg in [
            '',
            'foobar',
        ]:
            with self.assertRaises(AssertionError):
                _ = getattr(dispatcher, bad_arg)

    def test_calls_are_dispatched_to_added_callables(self):
        dispatcher = _get_event_dispatcher()
        mock_callable_a = Mock()
        mock_callable_b = Mock()

        dispatcher.on_startup.add(mock_callable_a)
        mock_callable_a.assert_not_called()
        mock_callable_b.assert_not_called()

        dispatcher.on_startup(1, x=2)
        mock_callable_a.assert_called_once_with(1, x=2)
        mock_callable_b.assert_not_called()

    def test_calls_are_dispatched_to_added_callables(self):
        dispatcher = _get_event_dispatcher()
        mock_startup_callable_A = Mock()
        mock_startup_callable_B = Mock()
        mock_shutdown_callable = Mock()

        dispatcher.on_startup.add(mock_startup_callable_A)
        dispatcher.on_startup.add(mock_startup_callable_B)
        mock_startup_callable_A.assert_not_called()
        mock_startup_callable_B.assert_not_called()
        mock_shutdown_callable.assert_not_called()

        dispatcher.on_startup(3, y=4)
        mock_startup_callable_A.assert_called_once_with(3, y=4)
        mock_startup_callable_B.assert_called_once_with(3, y=4)
        mock_shutdown_callable.assert_not_called()

        dispatcher.on_shutdown.add(mock_shutdown_callable)
        mock_startup_callable_A.assert_called_once_with(3, y=4)
        mock_startup_callable_B.assert_called_once_with(3, y=4)
        mock_shutdown_callable.assert_not_called()

        dispatcher.on_shutdown(5, z=6)
        mock_startup_callable_A.assert_called_once_with(3, y=4)
        mock_startup_callable_B.assert_called_once_with(3, y=4)
        mock_shutdown_callable.assert_called_once_with(5, z=6)

        dispatcher.on_startup(7)
        mock_startup_callable_A.assert_called_with(7)
        mock_startup_callable_B.assert_called_with(7)
        mock_shutdown_callable.assert_called_once_with(5, z=6)

    def test___str__(self):
        dispatcher = _get_event_dispatcher()
        actual = str(dispatcher)
        self.assertIsInstance(actual, str)
        self.assertEqual('EventDispatcher', actual)

    def test_calls_following_uncaught_exception_are_dispatched(self):
        dispatcher = _get_event_dispatcher()
        mock_callable_A = Mock()
        broken_callable = lambda _: 1 / 0
        mock_callable_c = Mock()

        dispatcher.on_shutdown.add(mock_callable_A)
        dispatcher.on_shutdown.add(broken_callable)
        dispatcher.on_shutdown.add(mock_callable_c)
        dispatcher.on_shutdown('foo')
        mock_callable_A.assert_called_once_with('foo')
        mock_callable_c.assert_called_once_with('foo')
