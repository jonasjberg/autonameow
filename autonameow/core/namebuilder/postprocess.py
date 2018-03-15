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

from util import text


class FilenamePostprocessor(object):
    def __init__(self, lowercase_filename=None, uppercase_filename=None,
                 regex_replacements=None, simplify_unicode=None):
        self.lowercase_filename = lowercase_filename or False
        self.uppercase_filename = uppercase_filename or False
        self.simplify_unicode = simplify_unicode or False

        # List of tuples containing a compiled regex and a unicode string.
        self.regex_replacements = regex_replacements or []

    def __call__(self, filename):
        _filename = filename

        # TODO: [TD0137] Add rule-specific replacements.
        # Do replacements first as the regular expressions are case-sensitive.
        if self.regex_replacements:
            _filename = self._do_replacements(_filename,
                                              self.regex_replacements)

        # Convert to lower-case if both upper- and lower- are enabled.
        if self.lowercase_filename:
            _filename = _filename.lower()
        elif self.uppercase_filename:
            _filename = _filename.upper()

        if self.simplify_unicode:
            _filename = self._do_simplify_unicode(_filename)

        return _filename

    @staticmethod
    def _do_replacements(filename, regex_replacement_tuples):
        return text.batch_regex_replace(regex_replacement_tuples, filename)

    @staticmethod
    def _do_simplify_unicode(filename):
        return text.simplify_unicode(filename)
