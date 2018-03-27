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

from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.metadata import EpubMetadataExtractor
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


unmet_dependencies = not EpubMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


# TODO: [TD0186] Re-implement epub metadata extractor


@skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = EpubMetadataExtractor
    EXTRACTOR_NAME = 'EpubMetadataExtractor'


@skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractorOutputTypes(CaseExtractorOutputTypes, TestCase):
    EXTRACTOR_CLASS = EpubMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')


@skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractorOutputTestFileA(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = EpubMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('title', str, 'Human, All Too Human: A Book for Free Spirits'),
    ]
