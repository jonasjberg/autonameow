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

from util.text.chunker import TextChunker


def _get_text_chunker(*args, **kwargs):
    text_chunker = TextChunker(*args, **kwargs)
    return text_chunker


class TestTextChunker(TestCase):
    def test_raises_assertion_error_when_given_bad_arguments(self):
        for bad_args in [
            (None, None),
            (None, 1.0),
            (None, '1.0'),
            (None, [1.0]),
            (['foo'], 1.0),
            ([b'foo'], 1.0),
            ('foo', None),
            ('foo', '1.0'),
            ('foo', [1.0]),
        ]:
            with self.assertRaises(AssertionError):
                _ = _get_text_chunker(*bad_args)

    def _assert_chunks(self, expected, given_args):
        chunker = _get_text_chunker(*given_args)
        self.assertEqual(expected, chunker.chunks)

    def _assert_chunked_text(self, expect_chunks, expect_len, given_args):
        chunker = _get_text_chunker(*given_args)
        self.assertEqual(expect_chunks, chunker.chunks)
        self.assertEqual(expect_len, len(chunker))

    def test_instantiated_text_chunker_is_not_none(self):
        chunker = _get_text_chunker('foo', 1.0)
        self.assertIsNotNone(chunker)

    def test_chunks_returns_expected_for_chunk_size_0_1(self):
        self._assert_chunked_text(
            expect_chunks=['A\n', 'B\n', 'C\n', 'D\n', 'E\n', 'F\n', 'G\n', 'H\n', 'I\n', 'J\n'],
            expect_len=10,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.1)
        )

    def test_chunks_returns_expected_for_chunk_size_0_2(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\n', 'C\nD\n', 'E\nF\n', 'G\nH\n', 'I\nJ\n'],
            expect_len=5,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.2)
        )

    def test_chunks_returns_expected_for_chunk_size_0_3(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\n', 'D\nE\nF\nG\n', 'H\nI\nJ\n'],
            expect_len=3,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.3)
        )

    def test_chunks_retkrns_expected_for_chunk_size_0_4(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\n', 'E\nF\n', 'G\nH\nI\nJ\n'],
            expect_len=3,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.4)
        )

    def test_chunks_returns_expected_for_chunk_size_0_5(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\nE\n', 'F\nG\nH\nI\nJ\n'],
            expect_len=2,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.5)
        )

    def test_chunks_returns_expected_for_chunk_size_0_6(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\nE\nF\n', 'G\nH\nI\nJ\n'],
            expect_len=2,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.6)
        )

    def test_chunks_returns_expected_for_chunk_size_0_7(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\nE\nF\nG\n', 'H\nI\nJ\n'],
            expect_len=2,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.7)
        )

    def test_chunks_returns_expected_for_chunk_size_0_8(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\nE\nF\nG\nH\n', 'I\nJ\n'],
            expect_len=2,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.8)
        )

    def test_chunks_returns_expected_for_chunk_size_0_9(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\nE\nF\nG\nH\nI\n', 'J\n'],
            expect_len=2,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 0.9)
        )

    def test_chunks_returns_expected_for_chunk_size_1_0(self):
        self._assert_chunked_text(
            expect_chunks=['A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n'],
            expect_len=1,
            given_args=('A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\n', 1.0)
        )

    def test_chunks_returns_expected_with_chunk_size_quarter(self):
        self._assert_chunks(expected=['foo\n'],
                            given_args=('foo\n', 0.25))
        self._assert_chunks(expected=['foo ooo\n'],
                            given_args=('foo ooo\n', 0.25))

        self._assert_chunks(expected=['foo\n\n'],
                            given_args=('foo\n\n', 0.25))
        self._assert_chunks(expected=['foo ooo\n\n'],
                            given_args=('foo ooo\n\n', 0.25))

    def test_chunks_returns_expected_with_chunk_size_half(self):
        self._assert_chunks(expected=['foo\n'],
                            given_args=('foo\n', 0.5))
        self._assert_chunks(expected=['foo ooo\n'],
                            given_args=('foo ooo\n', 0.5))

        self._assert_chunks(expected=['foo\n', '\n'],
                            given_args=('foo\n\n', 0.5))
        self._assert_chunks(expected=['foo ooo\n', '\n'],
                            given_args=('foo ooo\n\n', 0.5))

    def test_chunks_returns_expected_with_four_line_text_chunksize_quarter(self):
        self._assert_chunks(expected=['foo\n', 'bar\n', 'baz\n', 'meow\n'],
                            given_args=('foo\nbar\nbaz\nmeow\n', 0.25))

    def test_chunks_returns_expected_with_four_line_text_chunksize_half(self):
        self._assert_chunks(expected=['foo\nbar\n', 'baz\nmeow\n'],
                            given_args=('foo\nbar\nbaz\nmeow\n', 0.5))

    def test_indexed_access_with_four_line_text_chunksize_quarter(self):
        chunker = _get_text_chunker('foo\nbar\nbaz\nmeow\n', 0.25)
        self.assertEqual('foo\n', chunker[0])
        self.assertEqual('bar\n', chunker[1])
        self.assertEqual('baz\n', chunker[2])
        self.assertEqual('meow\n', chunker[3])

    def test_indexed_access_with_four_line_text_chunksize_half(self):
        chunker = _get_text_chunker('foo\nbar\nbaz\nmeow\n', 0.5)
        self.assertEqual('foo\nbar\n', chunker[0])
        self.assertEqual('baz\nmeow\n', chunker[1])

        # Without final trailing newline
        chunker = _get_text_chunker('foo\nbar\nbaz\nmeow', 0.5)
        self.assertEqual('foo\nbar\n', chunker[0])
        self.assertEqual('baz\nmeow', chunker[1])

    def test_indexed_access_with_five_line_text_chunksize_half(self):
        chunker = _get_text_chunker('A\nB\nC\nD\nE\n', 0.5)
        self.assertEqual('A\nB\n', chunker[0])
        self.assertEqual('C\n', chunker[1])
        self.assertEqual('D\nE\n', chunker[2])

        chunker = _get_text_chunker('A\nB\nC\nD\n', 0.5)
        self.assertEqual('A\nB\n', chunker[0])
        self.assertEqual('C\nD\n', chunker[1])

        chunker = _get_text_chunker('A\nB B\nC C C\nD D D D\n', 0.5)
        self.assertEqual('A\nB B\n', chunker[0])
        self.assertEqual('C C C\nD D D D\n', chunker[1])

    def test_indexed_access_with_three_line_text_chunksize_half(self):
        chunker = _get_text_chunker('A\nB\nC', 0.5)
        self.assertEqual('A\n', chunker[0])
        self.assertEqual('B\n', chunker[1])
        self.assertEqual('C', chunker[2])

    def test_indexed_access_with_three_line_text_chunksize_whole(self):
        chunker = _get_text_chunker('A\nB\nC', 1.0)
        self.assertEqual('A\nB\nC', chunker[0])

    def test_indexed_access_with_sample_text(self):
        text = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.
'''
        chunks = _get_text_chunker(text, 0.5)
        expect_chunk_0 = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat.
'''
        expect_chunk_1 = '''
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia
deserunt mollit anim id est laborum.
'''
        self.assertEqual(expect_chunk_0, chunks[0])
        self.assertEqual(expect_chunk_1, chunks[1])

    def test_leading_returns_expected(self):
        chunks = _get_text_chunker('A\nB\n', 0.5)
        self.assertEqual('A\n', chunks.leading)

    def test_trailing_returns_expected(self):
        chunks = _get_text_chunker('A\nB\n', 0.5)
        self.assertEqual('B\n', chunks.trailing)

    def test_leading_and_trailing_with_sample_text(self):
        text = '''Lorem ipsum dolor sit amet,
consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam,
aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate
eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia
deserunt mollit anim id est laborum.'''

        expect_leading = 'Lorem ipsum dolor sit amet,\n'

        expect_trailing = 'deserunt mollit anim id est laborum.'

        chunks = _get_text_chunker(text, 0.1)
        self.assertEqual(len(text.splitlines()), 10)
        self.assertEqual(expect_leading, chunks.leading)
        self.assertEqual(expect_trailing, chunks.trailing)
