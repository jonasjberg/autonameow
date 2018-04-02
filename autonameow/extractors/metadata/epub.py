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

import zipfile

from extractors import (
    BaseExtractor,
    ExtractorError
)


class EpubMetadataExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['application/epub+zip']
    IS_SLOW = False

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.abspath)

    def _get_metadata(self, filepath):
        raw_metadata = _get_epub_metadata(filepath)
        if raw_metadata:
            metadata = self._to_internal_format(raw_metadata)
            return metadata
        return dict()

    def _to_internal_format(self, raw_metadata):
        # TODO: [TD0186] Re-implement epub metadata extractor
        return raw_metadata

    @classmethod
    def check_dependencies(cls):
        # TODO: [TD0186] Re-implement epub metadata extractor
        return False


def _get_epub_metadata(filepath):
    try:
        # TODO: [TD0186] Re-implement epub metadata extractor
        raise ExtractorError('TODO: Reimplement epub metadata extraction')
    except (zipfile.BadZipFile, OSError) as e:
        raise ExtractorError('Unable to open epub file; "{!s}"'.format(e))
