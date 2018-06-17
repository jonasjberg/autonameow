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
    _diff = levenshtein(string_a, string_b)
    _normdiff = _diff / max(1, max(len(string_a), len(string_b)))
    return _normdiff


def string_difference(string_a, string_b):
    return normalized_levenshtein(string_a, string_b)


def string_similarity(string_a, string_b):
    _diff = levenshtein(string_a, string_b)
    _normdiff = _diff / max(1, max(len(string_a), len(string_b)))
    _normalized_similarity = 1 - _normdiff
    return _normalized_similarity


if __name__ == '__main__':
    import itertools
    import sys

    if len(sys.argv) < 3:
        sys.exit('Expected at least two arguments!')

    args = sys.argv[1:]
    arg_combinations = list(itertools.combinations(args, 2))
    results = list()
    for a, b in arg_combinations:
        # Trivial canonicalization
        # a = a.lower().replace('.', '').strip()
        # b = b.lower().replace('.', '').strip()

        s = string_similarity(a, b)
        d = string_difference(a, b)
        results.append((a, b, s, d))

    from core.view.cli.common import ColumnFormatter
    cf = ColumnFormatter()
    cf.addrow('String A', 'String B', 'Similarity', 'Difference')
    cf.addrow('========', '========', '==========', '==========')
    _float = '{:.2f}'
    for a, b, s, d in sorted(results, key=lambda x: x[2], reverse=True):
        cf.addrow(a, b, _float.format(s), _float.format(d))

    print(str(cf))
