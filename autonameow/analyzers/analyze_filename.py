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

from collections import Counter
import re

from analyzers import BaseAnalyzer
from core import (
    types,
    model
)
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.namebuilder import fields
from core.util import dateandtime


RE_EDITION = re.compile(r'([0-9])+((st|nd|rd|th)?\w?(E|ed|Ed)?)')
EDITION_RE_LOOKUP = {
    1: r'1st('
}
RE_ORDINAL_REPLACEMENT = []
for _pat, _replace in ((r'1st|first', 1),
                       (r'2nd|second', 2),
                       (r'3rd|third', 3),
                       (r'4th|fourth', 4),
                       (r'5th|fifth', 5),
                       (r'6th|sixth', 6),
                       (r'7th|eventh', 7),
                       (r'8th|eighth', 8),
                       (r'9th|ninth', 9),
                       (r'10th|tenth', 10),
                       (r'11th|eleventh', 11),
                       (r'12th|twelfth', 12),
                       (r'13th|thirteenth', 13),
                       (r'14th|fourteenth', 14),
                       (r'15th|fifteenth', 15),
                       (r'16th|sixteenth', 16),
                       (r'17th|seventeenth', 17),
                       (r'18th|eighteenth', 18),
                       (r'19th|nineteenth', 19),
                       (r'20th|twentieth', 20)):
    RE_ORDINAL_REPLACEMENT.append((re.compile(_pat, re.IGNORECASE), _replace))


class FilenameAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    HANDLES_MIME_TYPES = ['*/*']

    def __init__(self, fileobject, config,
                 add_results_callback, request_data_callback):
        super(FilenameAnalyzer, self).__init__(
            fileobject, config, add_results_callback, request_data_callback
        )

    def run(self):
        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('datetime', self.get_datetime())
        self._add_results('title', self.get_title())
        self._add_results('edition', self.get_edition())
        self._add_results('extension', self.get_extension())
        self._add_results('publisher', self.get_publisher())

    def get_datetime(self):
        results = []

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            results += fn_timestamps

        return results if results else None

    def get_title(self):
        return None

    def get_edition(self):
        basename = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.basename.prefix'
        )
        if not basename:
            return None

        _number = find_edition(basename.as_string())
        if _number:
            return ExtractedData(
                coercer=types.AW_INTEGER,
                mapped_fields=[
                    WeightedMapping(fields.Edition, probability=1),
                ],
                generic_field=model.GenericEdition
            )(_number)
        else:
            return None

    def get_extension(self):
        ed_basename_suffix = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.basename.suffix'
        )
        if not ed_basename_suffix:
            return

        ed_file_mimetype = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.contents.mime_type'
        )
        if not ed_file_mimetype:
            return

        file_basename_suffix = ed_basename_suffix.as_string()
        file_mimetype = ed_file_mimetype.value
        result = likely_extension(file_basename_suffix, file_mimetype)
        return ExtractedData(
            coercer=types.AW_PATHCOMPONENT,
            mapped_fields=[
                WeightedMapping(fields.Extension, probability=1),
            ]
        )(result)

    def get_publisher(self):
        ed_basename_prefix = self.request_data(
            self.fileobject,
            'extractor.filesystem.xplat.basename.prefix'
        )
        if not ed_basename_prefix:
            return

        file_basename_prefix = ed_basename_prefix.as_string()
        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if _options:
            _candidates = _options.get('candidates', {})
        else:
            _candidates = {}

        result = find_publisher(file_basename_prefix, _candidates)
        if not result:
            return None

        return ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=1),
            ],
            generic_field=model.GenericPublisher
        )(result)

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


MIMETYPE_EXTENSION_SUFFIXES_MAP = {
    # Note that the inner-most values are set-literals.
    'application/octet-stream': {
        'chm': {'chm'},
        'mobi': {'mobi'}
    },
    'text/plain': {
        'c': {'c'},
        'cpp': {'cpp', 'c++'},
        'csv': {'csv'},
        'gemspec': {'gemspec'},
        'h': {'h'},
        'java': {'java'},
        'js': {'js'},
        'json': {'json'},
        'key': {'key'},
        'md': {'markdown', 'md', 'mkd'},
        'puml': {'puml'},
        'py': {'py', 'python'},
        'rake': {'rake'},
        'spec': {'spec'},
        'sh': {'bash', 'sh'},
        'txt': {'txt'},
        'yaml': {'yaml'},
    },
    'text/x-shellscript': {
        'sh': {'bash', 'sh', 'txt'},
        'py': {'py'},
    },
}


def likely_extension(basename_suffix, mime_type):
    ext_suffixes_map = MIMETYPE_EXTENSION_SUFFIXES_MAP.get(mime_type)
    if ext_suffixes_map:
        for ext, suffixes in ext_suffixes_map.items():
            if basename_suffix in suffixes:
                return ext

    return types.AW_MIMETYPE.format(mime_type)


class SubstringFinder(object):
    # TODO: (?) Implement or remove ..

    def identify_fields(self, string, field_list):
        substrings = self._substrings(string)

    def _substrings(self, string):
        s = re.split(r'\W', string)
        return list(filter(None, s))


# TODO: Implement or remove ..
class FilenameTokenizer(object):
    RE_UNICODE_WORDS = re.compile(r'\w')

    def __init__(self, filename):
        self.filename = filename

    @property
    def separators(self):
        return self._find_separators(self.filename) or []

    def _find_separators(self, string):
        non_words = self.RE_UNICODE_WORDS.split(string)
        seps = [s for s in non_words if s is not None and s.strip()]

        sep_chars = []
        for sep in seps:
            if len(sep) > 1:
                sep_chars.extend(list(sep))
            else:
                sep_chars.append(sep)

        if not sep_chars:
            return None

        counts = Counter(sep_chars)
        # TODO: Implement or remove ..
        _most_common = counts.most_common(3)
        return _most_common


def find_edition(text):
    for _re_pattern, _num in RE_ORDINAL_REPLACEMENT:
        m = _re_pattern.search(text)
        if m:
            return _num

    match = RE_EDITION.search(text)
    if match:
        e = match.group(1)
        try:
            edition = types.AW_INTEGER(e)
            return edition
        except types.AWTypeError:
            pass

    return None


def find_publisher(text, candidates):
    for repl, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return repl

    return None
