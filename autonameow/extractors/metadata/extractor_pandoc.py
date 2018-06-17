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

import json
import os

import util
from core import constants as C
from extractors import ExtractorError
from extractors.metadata.base import BaseMetadataExtractor
from extractors.text.base import decode_raw
from util import coercers
from util import disk
from util import process

_PATH_THIS_DIR = coercers.AW_PATH(os.path.abspath(os.path.dirname(__file__)))
BASENAME_PANDOC_TEMPLATE = coercers.AW_PATHCOMPONENT('extractor_pandoc_template.plain')
PATH_CUSTOM_PANDOC_TEMPLATE = disk.joinpaths(_PATH_THIS_DIR,
                                             BASENAME_PANDOC_TEMPLATE)


class PandocMetadataExtractor(BaseMetadataExtractor):
    """
    Extracts various types of metadata using "pandoc".
    """
    HANDLES_MIME_TYPES = [
        'text/*', 'application/epub+zip'
    ]
    IS_SLOW = False

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.abspath)

    def _get_metadata(self, filepath):
        raw_metadata = extract_document_metadata_with_pandoc(filepath)
        if not raw_metadata:
            return dict()

        filtered_metadata = self._filter_raw_data(raw_metadata)
        metadata = self._to_internal_format(filtered_metadata)
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        return metadata

    def _filter_raw_data(self, raw_metadata):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        def _is_empty_string(v):
            return isinstance(v, str) and not v.strip()

        return {
            tag: value for tag, value in raw_metadata.items()
            if value and not _is_empty_string(value)
        }

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            coerced = self.coerce_field_value(field, value)
            # TODO: [TD0034] Filter out known bad data.
            # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
            # Empty strings are being passed through. But if we test with
            # 'if coerced', any False booleans, 0, etc. would be discarded.
            # Filtering must be field-specific.
            if coerced is not None:
                coerced_metadata[field] = coerced

        return coerced_metadata

    @classmethod
    def can_handle(cls, fileobject):
        # List of formats supported by pandoc v2.1.1 (homebrew 2018-02-19):
        #
        #     $ pandoc --list-input-formats
        #     commonmark
        #     creole
        #     docbook
        #     docx
        #     epub
        #     gfm
        #     haddock
        #     html
        #     jats
        #     json
        #     latex
        #     markdown
        #     markdown_github
        #     markdown_mmd
        #     markdown_phpextra
        #     markdown_strict
        #     mediawiki
        #     muse
        #     native
        #     odt
        #     opml
        #     org
        #     rst
        #     t2t
        #     textile
        #     tikiwiki
        #     twiki
        #     vimwiki
        #
        # Option '--list-input-formats' is not supported in pandoc v1.16.0.2
        # found in the ubuntu LTS repositories as of 2018-02-19.
        ok_suffixes = C.MARKDOWN_BASENAME_SUFFIXES.union(
            frozenset([b'tex', b'json', b'epub'])
        )
        return bool(
            # TODO: [TD0173] Check if 'pandoc' can handle a given file.
            cls._evaluate_mime_type_glob(fileobject)
            and fileobject.basename_suffix in ok_suffixes
        )

    @classmethod
    def dependencies_satisfied(cls):
        return (util.is_executable('pandoc')
                and disk.isfile(PATH_CUSTOM_PANDOC_TEMPLATE))


def extract_document_metadata_with_pandoc(filepath):
    """
    Custom pandoc template uses '$meta-json$' to output a
    "JSON representation of all of the document's metadata".
    """
    if not disk.isfile(PATH_CUSTOM_PANDOC_TEMPLATE):
        raise ExtractorError('Missing custom pandoc template file: '
                             '"{!s}"'.format(PATH_CUSTOM_PANDOC_TEMPLATE))

    # TODO: Convert non-UTF8 source text to UTF-8.
    #       pandoc does not handle non-UTF8 input.
    try:
        stdout = process.blocking_read_stdout(
            'pandoc', '--to', 'plain', '--template',
            PATH_CUSTOM_PANDOC_TEMPLATE, '--', filepath
        )
    except process.ChildProcessError as e:
        raise ExtractorError(e)

    json_string = decode_raw(stdout)
    return _parse_pandoc_output(json_string)


def _parse_pandoc_output(json_string):
    try:
        result = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ExtractorError('Error loading pandoc JSON output: {!s}'.format(e))
    else:
        return result
