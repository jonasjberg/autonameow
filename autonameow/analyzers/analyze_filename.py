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

import logging
import re
from collections import Counter


from analyzers import BaseAnalyzer
from core import types
from core.model import WeightedMapping
from core.namebuilder import fields
from util import dateandtime
from util.text import (
    find_edition,
    urldecode
)


log = logging.getLogger(__name__)


# Use two different types of separators;  "SPACE" and "SEPARATOR".
#
# Example filename:   "The-Artist_01_Great-Tune.mp4"
#                         ^      ^  ^     ^
#                     space   separators  space
#
# Splitting the filename by "SEPARATOR" gives some arbitrary "fields".
#
#                     "The-Artist"   "01"   "Great-Tune"
#                       Field #1      #2      Field #3
#
# Splitting the filename by "SPACE" typically gives words.
#
#                     "The"   "Artist"   "01"   "Great"   "Tune"

# TODO: Let the user specify this in the configuration file.
PREFERRED_FILENAME_CHAR_SPACE = '-'
PREFERRED_FILENAME_CHAR_SEPARATOR = '_'


class FilenameAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 1
    HANDLES_MIME_TYPES = ['*/*']

    def __init__(self, fileobject, config, request_data_callback):
        super(FilenameAnalyzer, self).__init__(
            fileobject, config, request_data_callback
        )

        self._basename_prefix = None
        self._basename_suffix = None
        self._file_mimetype = None

    def analyze(self):
        # TODO: [TD0136] Look into "requesting" already available data.
        basename_prefix = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.basename.prefix'
        )
        self._basename_prefix = types.force_string(basename_prefix.get('value'))

        basename_suffix = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.basename.suffix'
        )
        self._basename_suffix = types.force_string(basename_suffix.get('value'))

        file_mimetype = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.contents.mime_type'
        )
        self._file_mimetype = file_mimetype.get('value')

        self._add_results('datetime', self.get_datetime())
        self._add_results('edition', self._get_edition())
        self._add_results('extension', self._get_extension())
        self._add_results('publisher', self._get_publisher())

    def get_datetime(self):
        # TODO: [TD0110] Improve finding probable date/time in file names.
        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            if len(fn_timestamps) == 1:
                _timestamp = fn_timestamps[0]
                try:
                    _coerced_value = types.AW_TIMEDATE(_timestamp.get('value'))
                except types.AWTypeError:
                    pass
                else:
                    _prob = _timestamp.get('weight', 0.001)
                    return {
                        'value': _coerced_value,
                        'coercer': types.AW_TIMEDATE,
                        'mapped_fields': [
                            WeightedMapping(fields.DateTime, probability=_prob),
                            WeightedMapping(fields.Date, probability=_prob),
                        ],
                        'generic_field': 'date_created'
                    }

        # return fn_timestamps or None
        # TODO: Fix inconsistent analyzer results data.
        return None

    def _get_edition(self):
        if not self._basename_prefix:
            return None

        _number = find_edition(self._basename_prefix)
        if _number:
            return {
                'value': _number,
                'coercer': types.AW_INTEGER,
                'mapped_fields': [
                    WeightedMapping(fields.Edition, probability=1),
                ],
                'generic_field': 'edition'
            }
        else:
            return None

    def _get_extension(self):
        self.log.debug(
            'Attempting to get likely extension for MIME-type: "{!s}"  Basename'
            ' suffix: "{!s}"'.format(self._file_mimetype, self._basename_suffix)
        )
        result = likely_extension(self._basename_suffix, self._file_mimetype)
        self.log.debug('Likely extension: "{!s}"'.format(result))

        return {
            'value': result,
            'coercer': types.AW_PATHCOMPONENT,
            'mapped_fields': [
                WeightedMapping(fields.Extension, probability=1),
            ]
        }

    def _get_publisher(self):
        if not self._basename_prefix:
            return None

        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if not _options:
            return None

        _candidates = _options.get('candidates', {})
        result = find_publisher(self._basename_prefix, _candidates)
        if not result:
            return None

        return {
            'value': result,
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=1),
            ],
            'generic_field': 'publisher'
        }

    def _get_datetime_from_name(self):
        """
        Extracts date and time information from the file name.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        fn = self.fileobject.basename_prefix
        try:
            fn = types.AW_STRING(fn)
        except types.AWTypeError:
            return []

        # Strip non-digits from the left.
        fn = re.sub(r'^[^\d]+', '', fn)

        try:
            dt = types.AW_TIMEDATE(fn)
        except types.AWTypeError:
            pass
        else:
            return [{'value': dt,
                     'source': 'timedate_coercion',
                     'weight': 1}]

        results = []

        # 1. The Very Special Case
        # ========================
        # If this matches, it is very likely to be relevant, so test it first.
        # TODO: [TD0102] Look at how results are stored and named.
        dt_special = dateandtime.match_special_case(fn)
        if dt_special:
            results.append({'value': dt_special,
                            'source': 'very_special_case',
                            'weight': 1})
        else:
            dt_special_no_date = dateandtime.match_special_case_no_date(fn)
            if dt_special_no_date:
                results.append({'value': dt_special_no_date,
                                'source': 'very_special_case_no_date',
                                'weight': 1})

        # 2. Common patterns
        # ==================
        # Try more common patterns, starting with the most common.
        # TODO: [TD0102] Look at how results are stored and named.
        # TODO: [TD0019] This is not the way to do it!
        dt_android = dateandtime.match_android_messenger_filename(fn)
        if dt_android:
            results.append({'value': dt_android,
                            'source': 'android_messenger',
                            'weight': 1})

        # Match UNIX timestamp
        dt_unix = dateandtime.match_any_unix_timestamp(fn)
        if dt_unix:
            # TODO: [TD0102] Look at how results are stored and named.
            # TODO: [TD0019] Rework The FilenameAnalyzer class.
            results.append(
                {'value': dt_unix,
                 'source': 'unix_timestamp',
                 'weight': 1}
            )

        # Match screencapture-prefixed UNIX timestamp
        dt_screencapture_unix = dateandtime.match_screencapture_unixtime(fn)
        if dt_screencapture_unix:
            # TODO: [TD0102] Look at how results are stored and named.
            # TODO: [TD0019] Rework The FilenameAnalyzer class.
            results.append({'value': dt_screencapture_unix,
                            'source': 'screencapture_unixtime',
                            'weight': 1})

        # 3. Generalized patternmatching and bruteforcing
        # ===============================================
        # General "regex search" with various patterns.
        dt_regex = dateandtime.regex_search_str(fn)
        if dt_regex:
            for dt in dt_regex:
                results.append({'value': dt,
                                'source': 'regex_search',
                                'weight': 0.25})
        else:
            self.log.debug('Unable to extract date/time-information '
                           'from file name using regex search.')

        # Lastly, an iterative brute force search.
        # TODO: Collapse duplicate results with 'util.misc.multiset_count'..?
        dt_brute = dateandtime.bruteforce_str(fn)
        if dt_brute:
            for dt in dt_brute:
                results.append({'value': dt,
                                'source': 'bruteforce_search',
                                'weight': 0.1})
        else:
            self.log.debug('Unable to extract date/time-information '
                           'from file name using brute force search.')

        return results

    @classmethod
    def check_dependencies(cls):
        return True


# For each MIME-type; use the file extension in the dict key if the
# current file extension is any of the dict values stored under that key.
# NOTE(jonas): The inner-most values are set-literals.
MIMETYPE_EXTENSION_SUFFIXES_MAP = {
    'application/octet-stream': {
        # Might be corrupt files.
        '': {''},
        'azw3': {'azw3'},
        'bin': {'bin', 'binary'},
        'chm': {'chm'},
        'gz.sig': {'gz.sig'},
        'hex': {'hex'},
        'mobi': {'mobi'},
        'pdf': {'pdf'},
        'prc': {'prc'},
        'scpt': {'scpt'},
        'sig': {'sig'},
        'sln': {'sln'},  # Visual Studio Solution
        'tar.gz.sig': {'tar.gz.sig'},
        'txt': {'txt'}
    },
    'application/msword': {
        'doc': {'doc'}
    },
    'application/postscript': {
        'ps': {'ps'},
        'eps': {'eps'},
    },
    'application/gzip': {
        'gz': {'gz'},
        'tar.gz': {'tar.gz'}
    },
    'application/zip': {
        'zip': {'zip'},
        'epub': {'epub'},
        'alfredworkflow': {'alfredworkflow'}
    },
    'application/vnd.ms-powerpoint': {
        'ppt': {'ppt'},
    },
    'application/x-bzip2': {
        'tar.bz2': {'tar.bz2'},
    },
    'application/x-gzip': {
        'tar.gz': {'tar.gz', 'tgz'},
        'txt.gz': {'txt.gz'},
        'w.gz': {'w.gz'}  # CWEB source code
    },
    'application/x-lzma': {
        'tar.lzma': {'tar.lzma'}
    },
    'audio/mpeg': {
        'mp3': {'mp3'}
    },
    'text/html': {
        'html': {'html', 'htm'},
        'html.gz': {'htm.gz', 'html.gz'},
        'txt': {'txt'},
    },
    'text/plain': {
        'bibtex': {'bibtex'},
        'c': {'c'},
        'cpp': {'cpp', 'c++'},
        'css': {'css'},
        'csv': {'csv'},
        'gemspec': {'gemspec'},
        'h': {'h'},
        'html': {'html', 'htm'},
        'java': {'java'},
        'js': {'js'},
        'json': {'json'},
        'key': {'key'},
        'log': {'log'},
        'md': {'markdown', 'md', 'mkd'},
        'puml': {'puml'},
        'py': {'py', 'python'},
        'rake': {'rake'},
        'spec': {'spec'},
        'sh': {'bash', 'sh'},
        'txt': {'txt'},
        'txt.gz': {'txt.gz'},
        'yaml': {'yaml'},
    },
    'text/xml': {
        'cbp': {'cbp'},
        'workspace': {'workspace'}
    },
    'text/x-c': {
        'c': {'c', 'txt'},
        'h': {'h'},
        'w': {'w'}  # CWEB source code
    },
    'text/x-c++': {
        'cpp': {'cpp', 'c++', 'txt'},
        'h': {'h'}
    },
    'text/x-makefile': {
        '': {''},
        'asm': {'asm'}
    },
    'text/x-shellscript': {
        'sh': {'bash', 'sh', 'txt'},
        'py': {'py'},
    },
    'text/x-tex': {
        'log': {'log'},
        'tex': {'tex'},
    },
    'video/mpeg': {
        'VOB': {'VOB'},
        'vob': {'vob'},
        'mpg': {'mpeg'}
    }
}


def likely_extension(basename_suffix, mime_type):
    if mime_type and basename_suffix is not None:
        ext_suffixes_map = MIMETYPE_EXTENSION_SUFFIXES_MAP.get(mime_type, {})
        for ext, suffixes in ext_suffixes_map.items():
            if basename_suffix in suffixes:
                return ext

    # NOTE(jonas): Calling 'format()' returns a extension as a Unicode string.
    _coerced_mime = types.AW_MIMETYPE(mime_type)
    if _coerced_mime:
        log.debug('Passing coerced MIME "{!s}" to '
                  'AW_MIMETYPE.format()'.format(_coerced_mime))
        return types.AW_MIMETYPE.format(_coerced_mime)

    if basename_suffix == '':
        log.debug('Basename suffix is empty. Giving up..')
        return ''

    _coerced_suffix = types.AW_MIMETYPE(basename_suffix)
    if _coerced_suffix:
        log.debug('Passing coerced suffix "{!s}" to '
                  'AW_MIMETYPE.format()'.format(_coerced_suffix))
        return types.AW_MIMETYPE.format(_coerced_suffix)

    return None


# TODO: [TD0020] Identify data fields in file names.
class SubstringFinder(object):
    # TODO: (?) Implement or remove ..

    def identify_fields(self, string, field_list):
        substrings = self.substrings(string)

    def substrings(self, string):
        _splitchar = FilenameTokenizer(string).main_separator
        s = string.split(_splitchar)
        return list(filter(None, s))


class FilenamePreprocessor(object):
    def __init__(self):
        pass

    @classmethod
    def __call__(cls, filename):
        _processed = cls.preprocess(filename)
        return _processed

    @classmethod
    def preprocess(cls, filename):
        # Very simple heuristic for finding URL-encoded file names.
        #
        #   HTML 4.01 Specification
        #   17.13.4 Form content types
        #   application/x-www-form-urlencoded
        #   https://www.w3.org/TR/html4/interact/forms.html#h-17.13.4.1
        #
        # Spaces are represented as either '%20' or '+'.
        if ' ' not in filename:
            _decoded = None

            if '%20' in filename:
                _decoded = urldecode(filename)
            elif '+' in filename:
                _decoded = filename.replace('+', ' ')

            if _decoded and _decoded.strip():
                filename = _decoded

        return filename


class FilenameTokenizer(object):
    RE_UNICODE_WORDS = re.compile(r'[^\W_]')

    def __init__(self, filename):
        self.filename = FilenamePreprocessor()(filename)

    @property
    def tokens(self):
        _sep = self.main_separator
        if _sep:
            return self.filename.split(_sep)

    @property
    def separators(self, maxcount=None):
        if not maxcount:
            maxcount = 3

        _seps = self._find_separators(self.filename)
        if not _seps:
            return []

        if len(_seps) == 1:
            return _seps

        _tied_seps = self.get_seps_with_tied_counts(_seps)
        if _tied_seps:
            # Remove tied separators.
            _not_tied_seps = [s for s in _seps if s[0] not in _tied_seps]

            # Get preferred separator as a single character.
            _preferred = self.resolve_tied_count(_tied_seps)
            if _preferred:
                # Add back (sep, count)-tuple from preferred single char.
                _not_tied_seps.extend([s for s in _seps if s[0] == _preferred])

                # Add back the rest.
                _not_tied_seps.extend([s for s in _seps if s[0] != _preferred
                                       and s not in _not_tied_seps])

            _seps = _not_tied_seps

        return _seps[:maxcount]

    @property
    def main_separator(self):
        _seps = self._find_separators(self.filename)
        if not _seps:
            return None

        # Detect if first- and second-most common separators have an equal
        # number of occurrences and resolve any tied count separately.
        if len(_seps) >= 2:
            _first_count = _seps[0][1]
            _second_count = _seps[1][1]
            if _first_count == _second_count:
                return self.resolve_tied_count([_seps[0][0], _seps[1][0]])

        if _seps:
            try:
                return _seps[0][0]
            except IndexError:
                return ''

        return None

    @classmethod
    def get_seps_with_tied_counts(cls, separator_counts):
        seen = set()
        dupes = set()
        for _sep, _count in separator_counts:
            if _count in seen:
                dupes.add(_count)
            seen.add(_count)

        return [s[0] for s in separator_counts if s[1] in dupes]

    @classmethod
    def resolve_tied_count(cls, candidates):
        if not candidates:
            return []

        # Prefer to use the single space.
        if ' ' in candidates:
            return ' '
        elif PREFERRED_FILENAME_CHAR_SEPARATOR in candidates:
            # Use hardcoded preferred main separator character.
            return PREFERRED_FILENAME_CHAR_SEPARATOR
        elif PREFERRED_FILENAME_CHAR_SPACE in candidates:
            # Use hardcoded preferred space separator character.
            return PREFERRED_FILENAME_CHAR_SPACE
        else:
            # Last resort uses arbitrary value, sorted for consistency.
            return sorted(candidates, key=lambda x: x[0])[0]

    @classmethod
    def _find_separators(cls, string):
        non_words = cls.RE_UNICODE_WORDS.split(string)
        seps = [s for s in non_words if s is not None and len(s) >= 1]

        sep_chars = []
        for sep in seps:
            if len(sep) > 1:
                sep_chars.extend(list(sep))
            else:
                sep_chars.append(sep)

        if not sep_chars:
            return None

        counts = Counter(sep_chars)
        _most_common = counts.most_common(5)
        return _most_common


def find_publisher(text, candidates):
    for repl, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return repl

    return None
