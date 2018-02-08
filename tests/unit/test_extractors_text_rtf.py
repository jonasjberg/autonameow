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
    skipIf,
    skip,
    TestCase,
)

import unit.utils as uu
from extractors.text import RichTextFormatTextExtractor
from extractors.text.rtf import extract_text_with_unrtf
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


UNMET_DEPENDENCIES = RichTextFormatTextExtractor.check_dependencies() is False
DEPENDENCY_ERROR = 'Extractor dependencies not satisfied'

# TODO: This will fail. Either normalize text before returning or skip this!
TESTFILE_A = uu.abspath_testfile('ObjectCalisthenics.rtf')
TESTFILE_A_EXPECTED = '''Object Calisthenics
11 steps to better software design today.

Weve all seen poorly written code thats hard to understand, test, and maintain. Object-oriented programming promised to save us from our old procedural code, allowing us to write software incrementally, reusing as we go along. But sometimes it seems like were just chasing down the same old complex, coupled designs in Java that we had in C. 

Good object-oriented design is hard to learn. Transitioning from procedural development to object-oriented design requires a major shift in thinking that is more difficult than it seems. Many developers assume theyre doing a good job with OO design, when in reality theyre unconsciously stuck in old habits that are hard to break.  It doesnt help that many examples and best practices (even Suns code in the JDK) encourage poor OO design in the name of performance or simple weight of history. 

The core concepts behind good design are well understood. Alan Shalloway has suggested that seven code qualities matter: cohesion, loose coupling, no redundancy, encapsulation, testability, readability, and focus. Yet its hard to put those concepts into practice. Its one thing to understand that encapsulation means hiding data, implementation, type, design, or construction. Its another thing altogether to design code that implements encapsulation well. So heres an exercise that can help you to internalize principles of good object-oriented design and actually use them in real life. 

The Challenge
Do a simple project using far stricter coding standards than youve ever used in your life. Below, youll find 12 rules of thumb that will help push your code into good object-oriented shape. 

By suspending disbelief, and rigidly applying these rules on a small, 1000 line project, youll start to see a significantly different approach to designing software. Once youve written 1000 lines of code, the exercise is done, and you can relax and go back to using these 12 rules as guidelines.

This is a hard exercise, especially because many of these rules are not universally applicable. The fact is, sometimes classes are a little more than 50 lines. But theres great value in thinking about what would have to happen to move those responsibilities into real, first-class-objects of their own. Its developing this type of thinking thats the real value of the exercise. So stretch the limits of what you imagine is possible, and see whether you start thinking about your code in a new way. 
'''

TESTFILE_B = uu.abspath_testfile('sample.rtf')
TESTFILE_B_EXPECTED = '''Foo title
bar text

        
meow list
        
cat list

baz last line
'''


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_test_file_exists_b(self):
        self.assertTrue(uu.file_exists(TESTFILE_B))


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestRichTextFormatTextExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = RichTextFormatTextExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'RichTextFormatTextExtractor'
        self.assertEqual(actual, expect)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestRichTextFormatTextExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)


@skip('TODO: Messy whitespace and unquoted control characters ..')
@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestRichTextFormatTextExtractorOutputTestFileA(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_A_EXPECTED),
    ]


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestRichTextFormatTextExtractorOutputTestFileB(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_B)
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_B_EXPECTED),
    ]


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestExtractTextWithUnrtf(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.actual = extract_text_with_unrtf(TESTFILE_B)

    def test_returns_expected_type(self):
        self.assertTrue(uu.is_internalstring(self.actual))

    def test_returns_expected_text(self):
        self.assertEqual(TESTFILE_B_EXPECTED, self.actual)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestRichTextFormatTextExtractorInternals(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_fileobject = uu.fileobject_testfile('ObjectCalisthenics.rtf')
        self.e = RichTextFormatTextExtractor()

    def test__get_text_returns_something(self):
        actual = self.e.extract_text(self.test_fileobject)
        self.assertIsNotNone(actual)

    def test__get_text_returns_expected_type(self):
        actual = self.e.extract_text(self.test_fileobject)
        self.assertIsInstance(actual, str)

    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.e.extract(self.test_fileobject))

    def test_method_extract_returns_expected_type(self):
        actual = self.e.extract(self.test_fileobject)
        self.assertIsInstance(actual, dict)


class TestRichTextFormatTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.e = RichTextFormatTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime

        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')
        self.fo_rtf = DummyFileObject(mime='text/rtf')

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))
        self.assertTrue(self.e.can_handle(self.fo_rtf))
