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


class TextChunker(object):
    def __init__(self, text, chunk_to_text_ratio):
        """
        Splits multi-line text into smaller chunks.

        Example usage:

            chunker = _get_text_chunker('A\nB\nC\nD\nE\n', 0.5)
            assert chunker[0] == 'A\nB\n'
            assert chunker[1] == 'C\n'
            assert chunker[2] == 'D\nE\n'
            assert chunker.leading == 'A\nB\n'
            assert chunker.trailing == 'D\nE\n'
            assert len(chunker) == 3

        The chunk sizes (number of text lines in each chunk) is calculated from
        the chunk to text ratio as CHUNK_SIZE = LINES_IN_TEXT * CHUNK_RATIO

        The number of lines in the first and last chunks should match the chunk
        size exactly, while the number of lines in the center chunks might vary
        a bit so that the total number of chunks is more predictable.

        Args:
            text: Text to split into chunks, as either str or bytes.
            chunk_to_text_ratio: Size of the chunks as a float between 0 and 1.
        """
        assert isinstance(text, (str, bytes))
        self.text = text
        self.num_text_lines = len(self.text.splitlines())

        assert isinstance(chunk_to_text_ratio, (int, float))
        _chunk_ratio = float(chunk_to_text_ratio)
        assert 0.0 <= _chunk_ratio <= 1.0
        self.chunk_ratio = _chunk_ratio

        self._chunks = None

    @property
    def chunks(self):
        if self._chunks is None:
            self._chunks = self._split_text_into_chunks()
        return self._chunks

    def _split_text_into_chunks(self):
        chunk_size = int(self.num_text_lines * self.chunk_ratio)

        if chunk_size == 0 or self.num_text_lines <= chunk_size:
            # Chunk size could be 0 after rounding.
            return [self.text]

        lines = self.text.splitlines(keepends=True)

        # First pluck the first and last chunks to make sure that their line
        # counts match the chunk size.
        leading_chunk, lines = self._pop_leading(chunk_size, lines)
        trailing_chunk, lines = self._pop_trailing(chunk_size, lines)

        # Then split the remaining lines into groups of "chunk size" lines.
        remaining_lines = list(lines)
        center_chunks = list()
        loop_iteration_count = 0
        while remaining_lines:
            current_chunk, remaining_lines = self._pop_leading(chunk_size, remaining_lines)
            center_chunks.append(current_chunk)

            # Add any left over lines to the last center chunk.
            # This "rounding" is intended to make the total number of chunks
            # less sensitive to rounding, uneven numbers of lines, etc.
            # It is no big deal if the exact number of lines in the center
            # chunks varies somewhat with minor changes in chunk size and
            # input text, as long as the first and last chunks and total
            # number of chunks is more consistent.
            if len(remaining_lines) < chunk_size:
                center_chunks[-1] += ''.join(remaining_lines)
                break

            # Fail fast. Avoid infinite loops ..
            loop_iteration_count += 1
            if loop_iteration_count > self.num_text_lines:
                raise AssertionError(
                    'Loop iterations exceeded number of text lines'
                )

        # Re-assemble the leading, center and trailing chunks.
        center_chunks.insert(0, leading_chunk)
        center_chunks.append(trailing_chunk)
        return list(center_chunks)

    @staticmethod
    def _pop_trailing(chunk_size, text_lines):
        """
        Remove 'chunk_size' lines from the end of a list of text lines
        and join into a single string. Returns a (str, [str]) tuple.
        """
        trailing_chunk = ''.join(text_lines[-chunk_size:])
        text_lines = text_lines[:-chunk_size]
        return trailing_chunk, text_lines

    @staticmethod
    def _pop_leading(chunk_size, text_lines):
        """
        Remove 'chunk_size' lines from the start of a list of text lines
        and join into a single string. Returns a (str, [str]) tuple.
        """
        leading_chunk = ''.join(text_lines[:chunk_size])
        text_lines = text_lines[chunk_size:]
        return leading_chunk, text_lines

    def __getitem__(self, item):
        return self.chunks[item]

    @property
    def leading(self):
        return self.chunks[0]

    @property
    def trailing(self):
        return self.chunks[-1]

    def __len__(self):
        return len(self.chunks)
