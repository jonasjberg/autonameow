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


class GenericQueue(object):
    """
    Generic queue base class.

    TODO: Add some kind of parallel processing, don't wait for blocking I/O.
    """
    def __init__(self):
        self._items = []

    def enqueue(self, item):
        """
        Adds an item to the queue.

        Args:
            item: The item to enqueue.
        """
        if item:
            self._items.insert(0, item)

    def dequeue(self):
        """
        Returns and removes an item from the queue.

        Returns:
            The next enqueued item, if any.
        """
        if not self.is_empty():
            return self._items.pop()

    def is_empty(self):
        """
        Returns: True if the queue is empty, otherwise False.
        """
        return False if len(self) > 0 else True

    def clear(self):
        """
        Removes all items from the queue.
        """
        self._items = []

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        """
        Provides access to items in the queue.

        Items are returned in reverse chronological order, I.E. the item
        added first is returned last. Items are NOT dequeued.

        Returns:
            The enqueued items as an iterator.
        """
        for item in self._items:
            yield item

    def __str__(self):
        out = []
        for pos, item in enumerate(self):
            out.append('{:02d}: {!s}'.format(pos, item))
        return ', '.join(out)
