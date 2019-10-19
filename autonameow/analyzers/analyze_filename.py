# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import logging
import os
import re

from analyzers import AnalyzerError
from analyzers import BaseAnalyzer
from core import constants as C
from core.truths import known_data_loader
from core.truths import known_metadata
from util import coercers
from util import dateandtime
from util import disk
from util.text import find_and_extract_edition
from util.text import regexbatch


_SELF_DIRPATH = coercers.AW_PATH(os.path.abspath(os.path.dirname(__file__)))
BASENAME_PROBABLE_EXT_LOOKUP = coercers.AW_PATHCOMPONENT('probable_extension_lookup')
PATH_PROBABLE_EXT_LOOKUP = disk.joinpaths(_SELF_DIRPATH, BASENAME_PROBABLE_EXT_LOOKUP)

log = logging.getLogger(__name__)


# TODO: [TD0020] Identify data fields in file names.
# TODO: [TD0130] Implement general-purpose substring matching/extraction.
# TODO: [TD0153] Detect and clean up incrementally numbered files


class FilenameAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 1
    HANDLES_MIME_TYPES = ['*/*']
    FIELD_LOOKUP = {
        'datetime': {
            'coercer': 'aw_timedate',
            'multivalued': 'false',
            # TODO: [TD0166] No longer able to set weights dynamically ..
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'weight': '1.0'}},
                {'WeightedMapping': {'field': 'Date', 'weight': '1.0'}},
            ],
            'generic_field': 'date_created'
        },
        'edition': {
            'coercer': 'aw_integer',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Edition', 'weight': '1.0'}},
            ],
            'generic_field': 'edition'
        },
        'extension': {
            'coercer': 'aw_pathcomponent',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Extension', 'weight': '1.0'}},
            ]
        },
        'publisher': {
            'coercer': 'aw_string',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'weight': '1.0'}},
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
        self._basename_prefix = coercers.force_string(
            self.fileobject.basename_prefix
        )
        self._basename_suffix = coercers.force_string(
            self.fileobject.basename_suffix
        )
        self._file_mimetype = self.fileobject.mime_type or coercers.NULL_AW_MIMETYPE

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

        match = dateandtime.match_macos_screenshot(basename_prefix)
        if match:
            self.log.debug('Found "MacOS Screenshot" date/time in the basename')
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

        # TODO: [TD0192] Detect and extract editions from titles
        number, _ = find_and_extract_edition(self._basename_prefix)
        return number

    def _get_extension(self):
        self.log.debug(
            'Attempting to get likely extension for MIME-type: "%s"  Basename'
            ' suffix: "%s"', self._file_mimetype, self._basename_suffix
        )
        result = likely_extension(self._basename_suffix, self._file_mimetype)
        self.log.debug('Likely extension: "%s"', result)
        return result

    def _get_publisher(self):
        if not self._basename_prefix:
            return None

        known_publisher_values = known_metadata.canonical_values('publisher')
        if not known_publisher_values:
            return None

        self.log.debug(
            'Searching basename prefix for %d known publisher values',
            len(known_publisher_values)
        )
        result = find_known_publisher(self._basename_prefix, known_publisher_values)
        if result:
            self.log.debug('Found known publisher in basename prefix "%s"',
                           result)
            return result

        regex_lookup_dict = known_data_loader.regex_lookup_dict('publisher')
        result = find_publishers(self._basename_prefix, regex_lookup_dict)
        if result:
            self.log.debug('Found possible publisher in basename prefix "%s"',
                           result)
            return result

        return None

    @classmethod
    def dependencies_satisfied(cls):
        return True


# Populated at first access.
_PROBABLE_EXTENSION_CONFIG = None


def get_probable_extension_config(filepath=PATH_PROBABLE_EXT_LOOKUP):
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
            filepath,
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
        text = coercers.force_string(data)
        if not text.strip():
            return dict()

        # Ignore comments starting with hashes.
        text = re.sub(r'#.*', '', text)

        parsed = {}

        # Set to None to silence warnings on variables potentially being
        # referenced before assignment. This "should not" happen; both variables
        # are expected to be set before use, which is verified with assertions.
        use_extension_value = None
        mimetype_value = None

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
                    assert mimetype_value is not None, 'Invalid state'
                    parsed[mimetype_value][use_extension_value] = set()
                    self.state = self.STATE_LIST_BLOCK

            elif self.state == self.STATE_LIST_BLOCK:
                m = self._match_extension_list_item(line)
                if m is not None:
                    assert use_extension_value is not None, 'Invalid state'
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
    # TODO: [TD0200] Improve system for finding probable file extensions.
    #                Use additional information, like the "basename prefix".
    #                Should be able to handle files without extensions with a
    #                certain name like 'METADATA', having any of a list of
    #                MIME-types, so that the probable extension is empty, etc.
    if mime_type and basename_suffix is not None:
        assert isinstance(mime_type, str)

        # For each MIME-type; use the file extension in the dict key if the
        # current file extension is any of the dict values stored under that key.
        # NOTE(jonas): The inner-most values are set-literals.
        mimetype_ext_suffixes_map = get_probable_extension_config()
        ext_suffixes_map = mimetype_ext_suffixes_map.get(mime_type, {})
        for ext, suffixes in ext_suffixes_map.items():
            if basename_suffix in suffixes:
                return ext

    # NOTE(jonas): Calling 'format()' returns a extension as a Unicode string.
    _coerced_mime = coercers.AW_MIMETYPE(mime_type)
    if _coerced_mime:
        log.debug('Passing coerced MIME "%s" to AW_MIMETYPE.format()', _coerced_mime)
        return coercers.AW_MIMETYPE.format(_coerced_mime)

    if basename_suffix == '':
        log.debug('Basename suffix is empty. Giving up..')
        return ''

    _coerced_suffix = coercers.AW_MIMETYPE(basename_suffix)
    if _coerced_suffix:
        log.debug('Passing coerced suffix "%s" to AW_MIMETYPE.format()', _coerced_suffix)
        return coercers.AW_MIMETYPE.format(_coerced_suffix)

    return None


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


def find_known_publisher(text, known_publishers):
    lowercase_text = text.lower()

    for publisher in known_publishers:
        if publisher.lower() in lowercase_text:
            return publisher

    return None


def find_publishers(text, candidates):
    match = regexbatch.find_replacement_value(candidates, text)
    return match or None
