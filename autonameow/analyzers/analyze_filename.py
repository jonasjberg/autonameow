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
    util
)
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.namebuilder import fields
from core.util import dateandtime


RE_EDITION = re.compile(r'([0-9])+((st|nd|rd|th)\w?(E|ed)?|(E|Ed))')
EDITION_RE_LOOKUP = {
    1: r'1st('
}


class FilenameAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    HANDLES_MIME_TYPES = ['*/*']

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(FilenameAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

    def run(self):
        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('datetime', self.get_datetime())
        self._add_results('title', self.get_title())
        self._add_results('edition', self.get_edition())
        self._add_results('extension', self.get_extension())

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
            self.file_object,
            'extractor.filesystem.xplat.basename.prefix'
        ).value
        if not basename:
            return

    def get_extension(self):
        ed_basename_suffix = self.request_data(
            self.file_object,
            'extractor.filesystem.xplat.basename.suffix'
        )
        ed_file_mimetype = self.request_data(
            self.file_object,
            'extractor.filesystem.xplat.contents.mime_type'
        )
        file_basename_suffix = ed_basename_suffix.as_string()
        file_mimetype = ed_file_mimetype.value
        result = likely_extension(file_basename_suffix, file_mimetype)
        return ExtractedData(
            coercer=types.AW_PATHCOMPONENT,
            mapped_fields=[
                WeightedMapping(fields.Extension, probability=1),
            ]
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
        fn = self.file_object.basename_prefix
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
    'text/plain': {
        'c': {'c'},
        'cpp': {'cpp'},
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


def _find_edition(text):
    match = RE_EDITION.search(text)
    if match:
        e = match.group(1)
        try:
            edition = types.AW_INTEGER(e)
            return edition
        except types.AWTypeError:
            pass

    return None
