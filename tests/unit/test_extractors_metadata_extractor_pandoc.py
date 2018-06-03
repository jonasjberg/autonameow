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

import unittest
from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.metadata import PandocMetadataExtractor
from extractors.metadata.extractor_pandoc import _parse_pandoc_output
from extractors.metadata.extractor_pandoc import extract_document_metadata_with_pandoc
from unit.case_extractors import CaseExtractorBasics
from unit.case_extractors import CaseExtractorOutput
from unit.case_extractors import CaseExtractorOutputTypes


UNMET_DEPENDENCIES = (
    not PandocMetadataExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)


@skipIf(*UNMET_DEPENDENCIES)
class TestPandocMetadataExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    EXTRACTOR_NAME = 'PandocMetadataExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestPandocMetadataExtractorOutputTypes(CaseExtractorOutputTypes,
                                             TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('sample.md')


@skipIf(*UNMET_DEPENDENCIES)
class TestPandocMetadataExtractorOutputTestFileA(CaseExtractorOutput,
                                                 TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('sample.md')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('author', list, ['Gibson Sjöberg']),

        # TODO: Not available when using the template with only '$meta-json$'.
        # ('title', str, 'On Meow'),
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestPandocMetadataExtractorOutputTestFileB(CaseExtractorOutput,
                                                 TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')
    from datetime import datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('author', list, ['Friedrich Wilhelm Nietzsche']),

        # The pandoc JSON output currently looks like this;
        #
        #       "date": [
        #           "2017-07-20T05:22:31.613051+00:00",
        #           "2011-11-26"
        #       ]
        #
        # TODO: This should be handled somehow but doesn't work well with
        #       how the structure is declared in the "fieldmeta" file ..

        # TODO: This is WRONG! multivalued should be false
        # Expect more than one *different* dates, but never any
        # single "element" that is composed of more than one date.

        # EXPECTED: "2011-11-26"
        ('date', list, [datetime(2017, 7, 20), datetime(2011, 11, 26)]),

        # # EXPECTED: "2017-07-20T05:22:31.613051+00:00",
        # ('datetime', datetime, datetime(2017, 7, 20, 5, 22, 31)),

        ('title', str, 'Human, All Too Human: A Book for Free Spirits'),
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestPandocMetadataExtractorOutputTestFileC(CaseExtractorOutput,
                                                 TestCase):
    EXTRACTOR_CLASS = PandocMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('4123.epub')

    from datetime import datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('author', list, ['Bertrand Russell']),

        # The pandoc JSON output currently looks like this;
        #
        #       "date": [
        #           "2009-08-20",
        #           "1918"
        #       ]
        #
        # TODO: This should be handled somehow but doesn't work well with
        #       how the structure is declared in the "fieldmeta" file ..

        # TODO: This is WRONG! multivalued should be false
        # Expect more than one *different* dates, but never any
        # single "element" that is composed of more than one date.
        ('date', list, [datetime(2009, 8, 20, 0, 0, 0),
                        datetime(1918, 1, 1)]),
        ('title', str, 'Mysticism and Logic and Other Essays'),
    ]


class TestPandocMetadataExtractorCanHandle(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = PandocMetadataExtractor()

        cls.fo_image = uu.get_mock_fileobject(mime_type='image/jpeg')
        cls.fo_pdf = uu.get_mock_fileobject(mime_type='application/pdf')
        cls.fo_rtf = uu.get_mock_fileobject(mime_type='text/rtf')
        cls.fo_txt = uu.get_mock_fileobject(mime_type='text/plain')
        cls.fo_md = uu.fileobject_testfile('sample.md')
        cls.fo_epub = uu.fileobject_testfile('pg38145-images.epub')

    def _assert_can_handle_returns(self, expected, fileobject):
        actual = self.e.can_handle(fileobject)
        self.assertEqual(expected, actual)

    def test_class_method_can_handle_returns_false_as_expected(self):
        self._assert_can_handle_returns(False, self.fo_image)
        self._assert_can_handle_returns(False, self.fo_image)
        self._assert_can_handle_returns(False, self.fo_pdf)
        self._assert_can_handle_returns(False, self.fo_rtf)
        self._assert_can_handle_returns(False, self.fo_txt)

    def test_class_method_can_handle_returns_true_as_expected(self):
        self._assert_can_handle_returns(True, self.fo_md)
        self._assert_can_handle_returns(True, self.fo_epub)


class TestExtractDocumentMetadataWithPandocTestFileSampleMd(TestCase):
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
        self.assertEqual(['On Meow'], self.actual['title'])


class TestExtractDocumentMetadataWithPandocTestFile4123Epub(TestCase):
    @classmethod
    def setUpClass(cls):
        fo = uu.fileobject_testfile('4123.epub')
        cls.actual = extract_document_metadata_with_pandoc(fo.abspath)

    def _assert_extracted_metadata(self, expected_field, expected_value):
        self.assertIn(expected_field, self.actual)
        self.assertEqual(expected_value, self.actual[expected_field])

    def test_returns_expected_author(self):
        self._assert_extracted_metadata('author', 'Bertrand Russell')

    def test_returns_expected_title(self):
        self._assert_extracted_metadata('title', 'Mysticism and Logic and Other Essays')

    def test_returns_expected_date(self):
        self._assert_extracted_metadata('date', ['2009-08-20', '1918'])

    def test_returns_expected_description(self):
        self._assert_extracted_metadata('description', 'Essays on philosophy, religion, science, and mathematics.')

    def test_returns_expected_language(self):
        self._assert_extracted_metadata('language', 'en')

    def test_returns_expected_publisher(self):
        self._assert_extracted_metadata('publisher', 'Feedbooks')

    def test_returns_expected_source(self):
        self._assert_extracted_metadata('source', 'Project Gutenberg')

    def test_returns_expected_subject(self):
        self._assert_extracted_metadata(
            'subject', ['Science', 'Science and Technics',
                        'Religion', 'Philosophy', 'Human Science',
                        'Non-Fiction']
        )


class TestParsePandocOutput(TestCase):
    def test_parses_example_pandoc_output_json_string_4123_epub(self):
        pandoc_output_for_test_files_4123_epub = '''
{
    "author": "Bertrand Russell",
    "coverage": "",
    "date": [
        "2009-08-20",
        "1918"
    ],
    "description": "Essays on philosophy, religion, science, and mathematics.",
    "identifier": [
        "http://www.feedbooks.com/book/4123",
        "urn:uuid:d5adaa20-1955-11e7-8fff-4c72b9252ec6"
    ],
    "language": "en",
    "publisher": "Feedbooks",
    "rights": "This work was published before 1923 and is in the public domain in the USA only.",
    "source": "Project Gutenberg",
    "subject": [
        "Science",
        "Science and Technics",
        "Religion",
        "Philosophy",
        "Human Science",
        "Non-Fiction"
    ],
    "title": "Mysticism and Logic and Other Essays"
}
'''
        actual = _parse_pandoc_output(pandoc_output_for_test_files_4123_epub)
        self.assertIsInstance(actual, dict)
        self.assertIn('publisher', actual)
        self.assertEqual('Feedbooks', actual['publisher'])

    def test_parses_example_pandoc_output_json_string_pg38145_images_epub(self):
        pandoc_output_for_test_files_pg38145_images_epub = '''
{
    "author": "Friedrich Wilhelm Nietzsche",
    "contributor": "Alexander Harvey",
    "date": [
        "2017-07-20T05:22:31.613051+00:00",
        "2011-11-26"
    ],
    "identifier": "http://www.gutenberg.org/ebooks/38145",
    "language": "en",
    "rights": "Public domain in the USA.",
    "source": "http://www.gutenberg.org/files/38145/38145-h/38145-h.htm",
    "subject": "Human beings",
    "title": "Human, All Too Human: A Book for Free Spirits"
}
'''
        actual = _parse_pandoc_output(pandoc_output_for_test_files_pg38145_images_epub)
        self.assertIsInstance(actual, dict)
        self.assertIn('author', actual)
        self.assertEqual('Friedrich Wilhelm Nietzsche', actual['author'])
