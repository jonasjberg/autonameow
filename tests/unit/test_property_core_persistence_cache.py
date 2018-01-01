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

from unittest import (
    SkipTest,
    TestCase
)

try:
    from hypothesis import given
    from hypothesis.strategies import (
        binary,
        booleans,
        characters,
        integers,
        text
    )
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')

from core.persistence import cache


class TestBaseCache(TestCase):
    def setUp(self):
        owner = 'test_owner'
        self.c = cache.BaseCache(owner=owner)

    def tearDown(self):
        self.c.flush()

    @given(text(), text())
    def test_cache_only_raises_expected_exceptions(self, key, data):
        try:
            self.c.set(key, data)
        except cache.CacheError:
            pass
        except Exception as e:
            raise AssertionError(
                'c.set("{!s}", "{!s}") raised: {!s}'.format(key, data, e)
            )

        try:
            self.c.get(key)
        except cache.CacheError:
            pass
        except Exception as e:
            raise AssertionError(
                'c.get("{!s}", "{!s}") raised: {!s}'.format(key, data, e)
            )
