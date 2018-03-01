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

import logging
import os
import re
from collections import Counter

from analyzers import (
    AnalyzerError,
    BaseAnalyzer
)
from core import constants as C
from core import types
from util import (
    dateandtime,
    disk,
    sanity
)
from util.text import (
    find_edition,
    urldecode
)


_PATH_THIS_DIR = types.AW_PATH(os.path.abspath(os.path.dirname(__file__)))
BASENAME_PROBABLE_EXT_LOOKUP = types.AW_PATHCOMPONENT('probable_extension_lookup')
PATH_PROBABLE_EXT_LOOKUP = disk.joinpaths(_PATH_THIS_DIR, BASENAME_PROBABLE_EXT_LOOKUP)

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

# TODO: [TD0153] Detect and clean up incrementally numbered files


class FilenameAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 1
    HANDLES_MIME_TYPES = ['*/*']
    # TODO: [TD0178] Store only strings in 'FIELD_LOOKUP'.
    FIELD_LOOKUP = {
        'datetime': {
            'coercer': 'aw_timedate',
            'multivalued': 'false',
            # TODO: [TD0166] No longer able to set probabilities dynamically ..
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': 1.0}},
                {'WeightedMapping': {'field': 'Date', 'probability': 1.0}},
            ],
            'generic_field': 'date_created'
        },
        'edition': {
            'coercer': 'aw_integer',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Edition', 'probability': 1.0}},
            ],
            'generic_field': 'edition'
        },
        'extension': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'probability': 1.0}},
            ]
        },
        'publisher': {
            'coercer': 'aw_string',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': 1.0}},
            ],
            'generic_field': 'publisher'
        }
    }

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

        self._basename_prefix = None
        self._basename_suffix = None
        self._file_mimetype = None

    def analyze(self):
        basename_prefix = self.fileobject.basename_prefix
        self._basename_prefix = types.force_string(basename_prefix)

        basename_suffix = self.fileobject.basename_suffix
        self._basename_suffix = types.force_string(basename_suffix)

        file_mimetype = self.fileobject.mime_type
        self._file_mimetype = file_mimetype or types.NULL_AW_MIMETYPE
        self._add_intermediate_results('datetime', self._get_datetime())
        self._add_intermediate_results('edition', self._get_edition())
        self._add_intermediate_results('extension', self._get_extension())
        self._add_intermediate_results('publisher', self._get_publisher())

    def _get_datetime(self):
        result = self._get_datetime_from_name()
        if result and not dateandtime.is_datetime_instance(result):
            # Sanity check because value has not been explicitly coerced.
            raise AssertionError(
                'FilenameAnalyzer._get_datetime_from_name() should '
                'return None or instances of "datetime". '
                'Got {!s}'.format(type(result))
            )
        return result

    def _get_datetime_from_name(self):
        # TODO: [TD0043] Allow the user to tweak hardcoded settings.
        # TODO: [TD0110] Improve finding probable date/time in file names.
        basename_prefix = str(self._basename_prefix)

        # Strip non-digits from the left.
        basename_prefix = re.sub(r'^[^\d]+', '', basename_prefix)

        match = get_most_likely_datetime_from_string(basename_prefix)
        if match:
            self.log.debug('Found "most likely" date/time in the basename')
            return match

        match = dateandtime.match_android_messenger_filename(basename_prefix)
        if match:
            self.log.debug('Found "android messenger timestamp" date/time in the basename')
            return match

        match = dateandtime.match_screencapture_unixtime(basename_prefix)
        if match:
            self.log.debug('Found "screencapture UNIX timestamp" date/time in the basename')
            return match

        match = dateandtime.match_any_unix_timestamp(basename_prefix)
        if match:
            self.log.debug('Found "UNIX timestamp" date/time in the basename')
            return match

        return None

    def _get_edition(self):
        if not self._basename_prefix:
            return None

        number = find_edition(self._basename_prefix)
        return number

    def _get_extension(self):
        self.log.debug(
            'Attempting to get likely extension for MIME-type: "{!s}"  Basename'
            ' suffix: "{!s}"'.format(self._file_mimetype, self._basename_suffix)
        )
        result = likely_extension(self._basename_suffix, self._file_mimetype)
        self.log.debug('Likely extension: "{!s}"'.format(result))
        return result

    def _get_publisher(self):
        if not self._basename_prefix:
            return None

        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if not _options:
            return None

        _candidates = _options.get('candidates', {})
        result = find_publisher(self._basename_prefix, _candidates)
        return result

    @classmethod
    def check_dependencies(cls):
        return True


# Populated at first access.
_PROBABLE_EXTENSION_CONFIG = None


def get_probable_extension_config():
    """
    Retrieves the data used to find a likely extension from
    a given MIME-type and basename suffix.

    The data is read from disk, parsed and cached at first call.

    Returns:
        Config data as a dict.
    """
    global _PROBABLE_EXTENSION_CONFIG
    if _PROBABLE_EXTENSION_CONFIG is None:
        _PROBABLE_EXTENSION_CONFIG = _read_probable_extension_config_file(
            PATH_PROBABLE_EXT_LOOKUP
        )
    return _PROBABLE_EXTENSION_CONFIG


class MimetypeExtensionMapParser(object):
    (STATE_INITIAL, STATE_MIMETYPE_BLOCK, STATE_LIST_BLOCK) = range(3)
    VALUE_REPLACEMENTS = {
        'BLANK': ''
    }

    def __init__(self):
        self.state = self.STATE_INITIAL

    def parse(self, data):
        text = types.force_string(data)
        if not text.strip():
            return dict()

        # Ignore comments starting with hashes.
        text = re.sub(r'#.*', '', text)

        parsed = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            m = self._match_mimetype_block_start(line)
            if m:
                mimetype_value = m
                parsed[mimetype_value] = dict()
                self.state = self.STATE_MIMETYPE_BLOCK
                continue

            if self.state == self.STATE_MIMETYPE_BLOCK:
                use_extension_value = self._match_extension_list_start(line)
                if use_extension_value is not None:
                    parsed[mimetype_value][use_extension_value] = set()
                    self.state = self.STATE_LIST_BLOCK

            elif self.state == self.STATE_LIST_BLOCK:
                m = self._match_extension_list_item(line)
                if m is not None:
                    parsed[mimetype_value][use_extension_value].add(m)
                else:
                    use_extension_value = self._match_extension_list_start(line)
                    if use_extension_value is not None:
                        parsed[mimetype_value][use_extension_value] = set()
                        self.state = self.STATE_LIST_BLOCK

        return parsed

    def _match_mimetype_block_start(self, line):
        if line.startswith('MIMETYPE '):
            _, value = line.split(' ')
            return value
        return None

    def _match_extension_list_item(self, line):
        m = re.match(r'(^- )(.*)', line)
        if m:
            value = m.group(2).strip()
            return self._replace_keywords(value)
        return None

    def _match_extension_list_start(self, line):
        m = re.match(r'(^EXTENSION) (.*)', line)
        if m:
            value = m.group(2).strip()
            return self._replace_keywords(value)
        return None

    def _replace_keywords(self, value):
        return self.VALUE_REPLACEMENTS.get(value, value)


def _parse_mimetype_extension_suffixes_map_data(data):
    parser = MimetypeExtensionMapParser()
    try:
        return parser.parse(data)
    except Exception as e:
        raise AnalyzerError(
            'Error while parsing probable extension data :: {!s}'.format(e)
        )


def _read_probable_extension_config_file(filepath):
    try:
        with open(filepath, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            file_data = fh.read()
    except OSError as e:
        raise AnalyzerError(
            'Error while loading probable extension data file :: {!s}'.format(e)
        )
    return _parse_mimetype_extension_suffixes_map_data(file_data)


def likely_extension(basename_suffix, mime_type):
    if mime_type and basename_suffix is not None:
        sanity.check_internal_string(mime_type)

        # For each MIME-type; use the file extension in the dict key if the
        # current file extension is any of the dict values stored under that key.
        # NOTE(jonas): The inner-most values are set-literals.
        mimetype_ext_suffixes_map = get_probable_extension_config()
        ext_suffixes_map = mimetype_ext_suffixes_map.get(mime_type, {})
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


# TODO: [TD0130] Implement general-purpose substring matching/extraction.
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


# TODO: [TD0130] Implement general-purpose substring matching/extraction.
class FilenameTokenizer(object):
    RE_UNICODE_WORDS = re.compile(r'[^\W_]')

    def __init__(self, filename):
        self.filename = FilenamePreprocessor()(filename)

    @property
    def tokens(self):
        _sep = self.main_separator
        if _sep:
            return self.filename.split(_sep)
        return None

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


def get_most_likely_datetime_from_string(string):
    """
    Tries to extract the "most likely" date/time.

    Returns: An instance of 'datetime' or None.
    """
    # TODO: [TD0043] Allow the user to tweak hardcoded settings.

    # "The Very Special Case" (ISO-date like with time)
    match = dateandtime.match_special_case(string)
    if match:
        return match

    # "The Very Special Case" (ISO-date like without time)
    match = dateandtime.match_special_case_no_date(string)
    return match


def find_publisher(text, candidates):
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    for repl, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return repl
    return None
