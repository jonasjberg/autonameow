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
import logging
import os
import subprocess

import util
from core import constants as C
from core import types
from core.model import WeightedMapping
from core.namebuilder import fields
from extractors import (
    BaseExtractor,
    ExtractorError
)
from extractors.text.common import decode_raw
from util import disk

_PATH_THIS_DIR = types.AW_PATH(os.path.abspath(os.path.dirname(__file__)))
BASENAME_PANDOC_TEMPLATE = types.AW_PATHCOMPONENT('pandoc_template.plain')
PATH_CUSTOM_PANDOC_TEMPLATE = disk.joinpaths(_PATH_THIS_DIR,
                                             BASENAME_PANDOC_TEMPLATE)


log = logging.getLogger(__name__)


class PandocMetadataExtractor(BaseExtractor):
    """
    Extracts various types of metadata using "pandoc".
    """
    HANDLES_MIME_TYPES = [
        'text/*', 'application/epub+zip'
    ]
    IS_SLOW = False

    # TODO: [TD0178] Store only strings in 'FIELD_LOOKUP'.
    FIELD_LOOKUP = {
        'author': {
            'coercer': 'aw_string',
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
            ],
            'generic_field': 'author'
        },
        'author-meta': {
            'coercer': 'aw_string',
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
            ],
            'generic_field': 'author'
        },
        'date-meta': {
            'coercer': 'aw_date',
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=1),
                WeightedMapping(fields.DateTime, probability=1),
            ],
            'generic_field': 'date_created'
        },
        'date': {
            'coercer': 'aw_date',
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=1),
                WeightedMapping(fields.DateTime, probability=1),
            ],
            'generic_field': 'date_created'
        },
        'pagetitle': {
            'coercer': 'aw_string',
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=0.4),
            ],
            'generic_field': 'title'
        },
        'subtitle': {
            'coercer': 'aw_string',
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=0.25),
            ],
            'generic_field': 'title'
        },
        'table-of-contents': {
            'coercer': 'aw_string',
            'multivalued': True,
        },
        'title-prefix': {
            'coercer': 'aw_string',
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=0.5),
            ],
            'generic_field': 'title'
        },
        'tags': {
            'coercer': 'aw_string',
            'multivalued': True,
            'mapped_fields': [
                WeightedMapping(fields.Tags, probability=1),
            ],
            'generic_field': 'tags'
        },
        'title': {
            'coercer': 'aw_string',
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1),
            ],
            'generic_field': 'title'
        },
    }

    def extract(self, fileobject, **kwargs):
        self.log.debug('{!s}: Starting extraction'.format(self))
        source = fileobject.abspath

        _metadata = self._get_metadata(source)

        self.log.debug('{!s}: Completed extraction'.format(self))
        return _metadata

    def _get_metadata(self, source):
        _raw_metadata = extract_document_metadata_with_pandoc(source)
        if _raw_metadata:
            _filtered_metadata = self._filter_raw_data(_raw_metadata)

            # Internal data format boundary.  Wrap "raw" data with type classes.
            metadata = self._to_internal_format(_filtered_metadata)
            return metadata

        return dict()

    def _filter_raw_data(self, raw_metadata):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        return {
            tag: value for tag, value in raw_metadata.items()
            if value is not None
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
    def check_dependencies(cls):
        return (util.is_executable('pandoc')
                and disk.isfile(PATH_CUSTOM_PANDOC_TEMPLATE))


def extract_document_metadata_with_pandoc(file_path):
    # TODO: [TD0173] Parse JSON output or output of custom template?
    if not disk.isfile(PATH_CUSTOM_PANDOC_TEMPLATE):
        raise ExtractorError('Missing custom pandoc template file: '
                             '"{!s}"'.format(PATH_CUSTOM_PANDOC_TEMPLATE))

    # TODO: Convert non-UTF8 source text to UTF-8.
    #       pandoc does not handle non-UTF8 input.
    try:
        process = subprocess.Popen(
            ['pandoc', '--to', 'plain', '--template',
             PATH_CUSTOM_PANDOC_TEMPLATE, '--', file_path],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    if process.returncode != 0:
        raise ExtractorError(
            'pandoc returned {!s} with STDERR: "{!s}"'.format(
                process.returncode, stderr)
        )

    yaml_text = decode_raw(stdout)

    # Custom pandoc template generates output in YAML format.
    try:
        result = disk.load_yaml(yaml_text)
    except disk.YamlLoadError as e:
        raise ExtractorError('Unable to load custom pandoc template text '
                             'output as yaml :: {!s}'.format(e))

    return result if result else dict()


def parse_pandoc_json(json_dict):
    # TODO: [TD0173] Parse JSON output or output of custom template?
    pass


def convert_document_to_json_with_pandoc(file_path):
    # TODO: [TD0173] Parse JSON output or output of custom template?
    # TODO: Convert non-UTF8 source text to UTF-8.
    #       pandoc does not handle non-UTF8 input.
    try:
        process = subprocess.Popen(
            ['pandoc', '--to', 'json', '--', file_path],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)

    if process.returncode != 0:
        raise ExtractorError(
            'pandoc returned {!s} with STDERR: "{!s}"'.format(
                process.returncode, stderr)
        )

    json_text = decode_raw(stdout)

    # Custom pandoc template generates output in YAML format.
    try:
        result = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ExtractorError('Unable to parse pandoc json output :: {!s}'.format(e))

    return result if result else dict()
