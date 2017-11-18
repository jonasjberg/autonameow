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


from unittest import TestCase

from util.queue import GenericQueue


class TestGenericQueue(TestCase):
    def setUp(self):
        self.q = GenericQueue()

    def test_generic_queue_can_be_instantiated(self):
        self.assertIsNotNone(self.q)

    def test_generic_queue_initially_empty(self):
        self.assertEqual(len(self.q), 0)
        self.assertTrue(self.q.is_empty())

    def test_enqueuing_items_increments_len(self):
        self.q.enqueue({'foo': 'bar'})
        self.assertEqual(len(self.q), 1)
        self.q.enqueue({'foo': 'bar'})
        self.assertEqual(len(self.q), 2)

    def test_queue_is_not_empty_after_enqueuing_items(self):
        self.q.enqueue({'foo': 'bar'})
        self.assertFalse(self.q.is_empty())

    def test_clear_removes_all_enqueued_items(self):
        self.q.enqueue({'foo': 'bar'})
        self.q.enqueue({'baz': 'abc'})
        self.q.clear()
        self.assertTrue(self.q.is_empty())
        self.assertEqual(len(self.q), 0)

    def test_enqueuing_none_items_are_ignored(self):
        self.q.enqueue(None)
        self.assertEqual(len(self.q), 0)
        self.assertTrue(self.q.is_empty())

    def test_queue_iter_returns_enqueued_item(self):
        item_a = {'foo': 'bar'}
        self.q.enqueue(item_a)

        for item in self.q:
            self.assertEqual(item_a, item)

    def test_queue_iter_returns_enqueued_item_without_dequeuing(self):
        item_a = {'foo': 'bar'}
        self.q.enqueue(item_a)

        for item in self.q:
            self.assertEqual(item_a, item)

        self.assertEqual(len(self.q), 1)

    def test_queue_iter_returns_enqueued_items(self):
        item_a = {'foo': 'bar'}
        item_b = {'baz': 'mjao'}
        self.q.enqueue(item_a)
        self.q.enqueue(item_b)

        items = list(self.q)
        self.assertIn(item_a, items)
        self.assertIn(item_a, items)

    def test_queue_iter_returns_enqueued_items_in_expected_order(self):
        item_a = {'foo': 'bar'}
        item_b = {'baz': 'mjao'}
        item_c = {'abc': 'baz'}
        self.q.enqueue(item_c)
        self.q.enqueue(item_a)
        self.q.enqueue(item_b)

        items = list(self.q)
        self.assertEqual(item_c, items[0])
        self.assertEqual(item_a, items[1])
        self.assertEqual(item_b, items[2])

    def test_queue_iter_returns_enqueued_items_without_dequeuing(self):
        item_a = {'foo': 'bar'}
        item_b = {'baz': 'mjao'}
        self.q.enqueue(item_a)
        self.q.enqueue(item_b)

        items = list(self.q)
        self.assertIn(item_a, items)
        self.assertIn(item_a, items)

        self.assertEqual(len(self.q), 2)

    def test_dequeue_returns_and_removes_item(self):
        item_a = {'foo': 'bar'}
        self.q.enqueue(item_a)

        i = self.q.dequeue()
        self.assertEqual(i, item_a)
        self.assertEqual(len(self.q), 0)

    def test_dequeue_returns_and_removes_items(self):
        item_a = {'foo': 'bar'}
        item_b = {'baz': 'mjao'}
        self.q.enqueue(item_a)
        self.q.enqueue(item_b)

        i = self.q.dequeue()
        j = self.q.dequeue()
        self.assertEqual(i, item_a)
        self.assertEqual(j, item_b)
        self.assertEqual(len(self.q), 0)

    def test_dequeue_returns_expected_item(self):
        item_a = {'foo': 'bar'}
        self.q.enqueue(item_a)

        i = self.q.dequeue()
        self.assertEqual(i, item_a)

    def test_dequeue_returns_expected_items(self):
        item_a = {'foo': 'bar'}
        self.q.enqueue(item_a)

        i = self.q.dequeue()
        self.assertEqual(i, item_a)

        item_b = {'baz': 'mjao'}
        self.q.enqueue(item_b)
        j = self.q.dequeue()
        self.assertEqual(j, item_b)

    def test_dequeue_returns_expected_items_in_correct_order(self):
        item_a = {'foo': 'bar'}
        item_b = {'baz': 'mjao'}
        self.q.enqueue(item_a)
        self.q.enqueue(item_b)

        i = self.q.dequeue()
        self.assertNotEqual(i, item_b)
        self.assertEqual(i, item_a)

        j = self.q.dequeue()
        self.assertNotEqual(j, item_a)
        self.assertEqual(j, item_b)

    def test_queue_implements___getattr__(self):
        self.q.reverse()
        self.q.sort()
