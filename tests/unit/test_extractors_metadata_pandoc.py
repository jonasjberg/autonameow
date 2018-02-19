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

from unittest import (
    skip,
    skipIf,
    TestCase,
)

import unit.utils as uu
from extractors.metadata import PandocMetadataExtractor
from extractors.metadata.pandoc import (
    convert_document_to_json_with_pandoc,
    extract_document_metadata_with_pandoc,
    parse_pandoc_json
)

from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


unmet_dependencies = not PandocMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


EXPECTED_PANDOC_JSON_FOR_SAMPLE_DOT_MD = [
    {'unMeta': {'author': {'c': [{'c': [{'c': 'Gibson', 't': 'Str'},
                                        {'c': [], 't': 'Space'},
                                        {'c': 'Sjöberg', 't': 'Str'}],
                                  't': 'MetaInlines'}],
                           't': 'MetaList'},
                'title': {'c': [{'c': [{'c': 'On', 't': 'Str'},
                                       {'c': [], 't': 'Space'},
                                       {'c': 'Meow', 't': 'Str'}],
                                 't': 'MetaInlines'}],
                          't': 'MetaList'}}},
    [{'c': [1,
            ['on-meow', [], []],
            [{'c': 'On', 't': 'Str'},
             {'c': [], 't': 'Space'},
             {'c': 'Meow', 't': 'Str'}]],
      't': 'Header'},
     {'c': [{'c': 'Meow', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'meow', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'meow', 't': 'Str'}],
      't': 'Para'},
     {'c': [[{'c': [{'c': 'meow', 't': 'Str'},
                    {'c': [], 't': 'Space'},
                    {'c': 'list', 't': 'Str'}],
              't': 'Plain'}],
            [{'c': [{'c': 'cat', 't': 'Str'},
                    {'c': [], 't': 'Space'},
                    {'c': 'list', 't': 'Str'}],
              't': 'Plain'}]],
      't': 'BulletList'},
     {'c': [{'c': 'this', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'is', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'the', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'meow', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'last', 't': 'Str'},
            {'c': [], 't': 'Space'},
            {'c': 'line', 't': 'Str'}],
      't': 'Para'}]
]


@skipIf(unmet_dependencies, dependency_error)
class TestPandocMetadataExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    EXTRACTOR_NAME = 'PandocMetadataExtractor'


@skipIf(unmet_dependencies, dependency_error)
class TestPandocMetadataExtractorOutputTypes(CaseExtractorOutputTypes,
                                             TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('sample.md')


@skipIf(unmet_dependencies, dependency_error)
class TestPandocMetadataExtractorOutputTestFileA(CaseExtractorOutput,
                                                 TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('sample.md')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('author', list, ['Gibson Sjöberg']),
        ('title', str, 'On Meow'),
    ]


@skipIf(unmet_dependencies, dependency_error)
class TestPandocMetadataExtractorOutputTestFileB(CaseExtractorOutput,
                                                 TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')
    from datetime import datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('author', list, ['Friedrich Wilhelm Nietzsche']),
        ('date', datetime, datetime(2017, 7, 20, 0, 0, 0)),
        ('title', str, 'Human, All Too Human: A Book for Free Spirits'),
    ]


@skipIf(unmet_dependencies, dependency_error)
class TestPandocMetadataExtractorOutputTestFileC(CaseExtractorOutput,
                                                 TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('4123.epub')

    from datetime import datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('author', list, ['Bertrand Russell']),
        ('date', datetime, datetime(2009, 8, 20, 0, 0, 0)),
        ('title', str, 'Mysticism and Logic and Other Essays'),
    ]


class TestPandocMetadataExtractorCanHandle(TestCase):
    def setUp(self):
        self.e = PandocMetadataExtractor()

        self.fo_image = uu.get_mock_fileobject(mime_type='image/jpeg')
        self.fo_pdf = uu.get_mock_fileobject(mime_type='application/pdf')
        self.fo_rtf = uu.get_mock_fileobject(mime_type='text/rtf')
        self.fo_txt = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_md = uu.fileobject_testfile('sample.md')
        self.fo_epub = uu.fileobject_testfile('pg38145-images.epub')

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))
        self.assertFalse(self.e.can_handle(self.fo_rtf))
        self.assertFalse(self.e.can_handle(self.fo_txt))
        self.assertTrue(self.e.can_handle(self.fo_md))
        self.assertTrue(self.e.can_handle(self.fo_epub))


class TestExtractDocumentMetadataWithPandocA(TestCase):
    # TODO: [TD0173] Parse pandoc JSON output or use custom template?
    @classmethod
    def setUpClass(cls):
        fo = uu.fileobject_testfile('sample.md')
        cls.actual = extract_document_metadata_with_pandoc(fo.abspath)

    def test_does_not_return_none(self):
        self.assertIsNotNone(self.actual)

    def test_returns_expected_type(self):
        self.assertIsInstance(self.actual, dict)

    def test_returns_expected_metadata_author(self):
        self.assertIn('author', self.actual)
        self.assertEqual(['Gibson Sjöberg'], self.actual['author'])

    def test_returns_expected_metadata_title(self):
        self.assertIn('title', self.actual)
        self.assertEqual('On Meow', self.actual['title'])


class TestExtractDocumentMetadataWithPandocB(TestCase):
    # TODO: [TD0173] Parse pandoc JSON output or use custom template?
    @classmethod
    def setUpClass(cls):
        fo = uu.fileobject_testfile('4123.epub')
        cls.actual = extract_document_metadata_with_pandoc(fo.abspath)

    def test_returns_expected_metadata_author(self):
        self.assertIn('author', self.actual)
        self.assertEqual(['Bertrand Russell'], self.actual['author'])

    def test_returns_expected_metadata_title(self):
        self.assertIn('title', self.actual)
        self.assertEqual('Mysticism and Logic and Other Essays', self.actual['title'])

    def test_returns_expected_date(self):
        self.assertIn('date', self.actual)
        self.assertEqual('2009-08-20', self.actual['date'])


class TestConvertDocumentToJsonWithPandoc(TestCase):
    # TODO: [TD0173] Parse pandoc JSON output or use custom template?
    @classmethod
    def setUpClass(cls):
        fo = uu.fileobject_testfile('sample.md')
        cls.actual = convert_document_to_json_with_pandoc(fo.abspath)

    def test_does_not_return_none(self):
        self.assertIsNotNone(self.actual)

    def test_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)
        self.assertEqual(2, len(self.actual))

    def test_returns_json_with_expected_metadata_section(self):
        self.assertIn('unMeta', self.actual[0])

    def test_returns_expected_json_data(self):
        # Tests changes to pandoc's AST reflected in the JSON output.
        self.assertEqual(EXPECTED_PANDOC_JSON_FOR_SAMPLE_DOT_MD, self.actual)

    def test_returns_json_with_expected_body_section(self):
        body_section = self.actual[1]
        self.assertIsNotNone(body_section)
        self.assertIsInstance(body_section, list)
        self.assertEqual(4, len(body_section))
        self.assertIsInstance(body_section[0], dict)
        self.assertIsInstance(body_section[1], dict)
        self.assertIsInstance(body_section[2], dict)
        self.assertIsInstance(body_section[3], dict)


@skip('TODO: [TD0173] Parse pandoc JSON output or use custom template?')
class TestParsePandocJson(TestCase):
    def test_parses_meta_section(self):
        given = EXPECTED_PANDOC_JSON_FOR_SAMPLE_DOT_MD
        actual = parse_pandoc_json(given)
        self.assertIn('meta', actual)
