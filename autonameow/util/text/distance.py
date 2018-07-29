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

from difflib import SequenceMatcher


def levenshtein(string_a, string_b):
    n, m = len(string_a), len(string_b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        string_a, string_b = string_b, string_a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if string_a[j - 1] != string_b[i - 1]:
                change += 1
            current[j] = min(add, delete, change)

    return current[n]


def normalized_levenshtein(string_a, string_b):
    lev_dist = levenshtein(string_a, string_b)
    normalized_dist = lev_dist / max(1, max(len(string_a), len(string_b)))
    return normalized_dist


def longest_common_substring_length(string_a, string_b):
    assert isinstance(string_a, str) and isinstance(string_b, str)

    matcher = SequenceMatcher(None, string_a, string_b, autojunk=False)
    match = matcher.find_longest_match(0, len(string_a), 0, len(string_b))
    return int(match.size)


def total_common_substring_length(string_a, string_b):
    assert isinstance(string_a, str), (type(string_a), str(string_a))
    assert isinstance(string_b, str), (type(string_b), str(string_b))

    matcher = SequenceMatcher(None, string_a, string_b, autojunk=False)
    matches = matcher.get_matching_blocks()
    total_matched_length = sum(m.size for m in matches)
    return total_matched_length


def string_difference(string_a, string_b):
    assert isinstance(string_a, str)
    assert isinstance(string_b, str)

    return normalized_levenshtein(string_a, string_b)


def string_similarity(string_a, string_b):
    assert isinstance(string_a, str)
    assert isinstance(string_b, str)

    lev_dist = levenshtein(string_a, string_b)
    denominator = max(1, max(len(string_a), len(string_b)))
    normalized_similarity = 1 - (lev_dist / denominator)
    return normalized_similarity


if __name__ == '__main__':
    import itertools
    import sys

    if len(sys.argv) < 3:
        sys.exit('Expected at least two arguments!')

    args = sys.argv[1:]
    arg_combinations = list(itertools.combinations(args, 2))
    results = list()
    for a, b in arg_combinations:
        s = string_similarity(a, b)
        d = string_difference(a, b)
        lcsl = longest_common_substring_length(a, b)
        tcsl = total_common_substring_length(a, b)
        results.append((a, b, s, d, lcsl, tcsl))

    from core.view.cli.common import ColumnFormatter
    cf = ColumnFormatter()
    cf.addrow('String A', 'String B', 'Similarity', 'Difference', 'LCSL', 'TCSL')
    cf.addrow('========', '========', '==========', '==========', '====', '====')
    _float = '{:.2f}'
    for a, b, s, d, lcsl, tcsl in sorted(results, key=lambda x: x[2], reverse=True):
        cf.addrow(a[:40], b[:40], _float.format(s), _float.format(d), str(lcsl), str(tcsl))

    print(str(cf))
