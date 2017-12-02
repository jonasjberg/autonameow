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

from unittest import TestCase

import unit.constants as uuconst
from core import constants as C
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.model.meowuri import (
    is_meowuri_part,
    is_meowuri_parts,
    meowuri_list,
    MeowURILeaf,
    MeowURIChild,
    MeowURIParser,
    MeowURIRoot
)


class TestMeowURIStringMatchingFunctions(TestCase):
    def test_is_meowuri_part(self):
        def _aT(test_input):
            actual = is_meowuri_part(test_input)
            self.assertTrue(isinstance(actual, bool))
            self.assertTrue(actual)

        _aT('f')
        _aT('foo')
        _aT('123')
        _aT('foo123')
        _aT('_')

        def _aF(test_input):
            actual = is_meowuri_part(test_input)
            self.assertTrue(isinstance(actual, bool))
            self.assertFalse(actual)

        for _bad_input in [None, b'', b'foo', 1, {}, [], object()]:
            _aF(_bad_input)

        _aF('')
        _aF(' ')
        _aF('.')
        _aF('..')
        _aF(' .')
        _aF(' ..')
        _aF(' . ')
        _aF(' .. ')
        _aF('.foo')
        _aF('foo.')
        _aF('foo.bar')
        _aF('.foo.bar')
        _aF('.foo.bar.')

    def test_is_meowuri_parts(self):
        def _aT(test_input):
            actual = is_meowuri_parts(test_input)
            self.assertTrue(isinstance(actual, bool))
            self.assertTrue(actual)

        _aT('f.o')
        _aT('foo.bar')
        _aT('123.bar')
        _aT('foo.123')
        _aT('f.o.b')
        _aT('foo.bar.baz')
        _aT('123.bar.baz')
        _aT('foo.123.baz')
        # TODO: Normalize exiftool tags? Translate to some "custom" format?
        _aT(':.:')
        _aT('extractor.filesystem.xplat.contents.mime_type')

        def _aF(test_input):
            actual = is_meowuri_parts(test_input)
            self.assertTrue(isinstance(actual, bool))
            self.assertFalse(actual)

        for _bad_input in [None, b'', b'foo', 1, {}, [], object()]:
            _aF(_bad_input)

        _aF('')
        _aF(' ')
        _aF('.')
        _aF('..')
        _aF(' .')
        _aF(' ..')
        _aF(' . ')
        _aF(' .. ')
        _aF('f')
        _aF('foo')
        _aF('123')
        _aF('foo123')
        _aF('_')
        _aF('.foo')
        _aF('foo.')
        _aF('foo. ')
        _aF('.foo.bar')
        _aF('foo.bar.')
        _aF('.foo.bar.')

    def test_full_meowuris(self):
        def _aT(test_input):
            actual = is_meowuri_parts(test_input)
            self.assertTrue(isinstance(actual, bool))
            self.assertTrue(actual,
                            'Expected True for "{!s}"'.format(test_input))

        for _valid_meowuri in uuconst.ALL_FULL_MEOWURIS:
            _aT(_valid_meowuri)


class TestMeowURIRoot(TestCase):
    def test_from_valid_input(self):

        def _ok(test_input):
            a = MeowURIRoot(test_input)
            self.assertIsNotNone(a)

        _ok('analyzer')
        _ok('generic')
        _ok('plugin')
        _ok(' analyzer')
        _ok(' generic')
        _ok(' plugin')
        _ok(' analyzer ')
        _ok(' generic ')
        _ok(' plugin ')

    def test_from_invalid_input(self):
        def _f(test_input):
            with self.assertRaises(InvalidMeowURIError):
                _ = MeowURIRoot(test_input)

        _f(None)
        _f('')
        _f('foo')
        _f('analysis')
        _f('filesystem')
        _f('plugins')
        _f('metadata')


class TestMeowURIMutability(TestCase):
    def setUp(self):
        self.m = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test_attribute_parts_is_immutable(self):
        before = self.m.parts

        with self.assertRaises(AttributeError):
            self.m.parts = ['foo']

        after = self.m.parts
        self.assertEqual(before, after)


class TestEvalMeowURIGlob(TestCase):
    def test_eval_meowuri_blob_returns_false_given_bad_arguments(self):
        m = MeowURI('generic.metadata.foo')
        actual = m.matchglobs(None)
        self.assertIsNotNone(actual)
        self.assertFalse(actual)


class TestMeowURIEquality(TestCase):
    def setUp(self):
        self.m = MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.a = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test_compare_with_string(self):
        self.assertEqual(self.m, uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertNotEqual(self.m, uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        self.assertNotEqual(self.m, uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        self.assertEqual(self.a, uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        self.assertNotEqual(self.a, uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        self.assertNotEqual(self.a, uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)

    def test_compare_with_other_class_instances(self):
        self.assertNotEqual(self.m, self.a)

        b = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        c = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        self.assertEqual(b, c)

    def test_compare_with_other_types(self):
        def _aF(test_input):
            self.assertNotEqual(self.m, test_input)

        _aF(None)
        _aF(object())
        _aF(1)
        _aF({})


class TestMeowURIComparison(TestCase):
    def test_less_than_based_on_length(self):
        a = MeowURI('extractor.filesystem.xplat.basename')
        b = MeowURI('extractor.filesystem.xplat.contents.full')
        self.assertTrue(a < b)

    def test_greater_than_based_on_length(self):
        a = MeowURI('extractor.filesystem.xplat.contents.full')
        b = MeowURI('extractor.filesystem.xplat.basename')
        self.assertTrue(a > b)

    def test_less_than_based_on_contents(self):
        a = MeowURI('extractor.filesystem.xplat.basename')
        b = MeowURI('extractor.filesystem.xplat.contents')
        self.assertTrue(a < b)

    def test_greater_than_based_on_contents(self):
        a = MeowURI('extractor.filesystem.xplat.contents')
        b = MeowURI('extractor.filesystem.xplat.basename')
        self.assertTrue(a > b)


class TestEvalMeowURIGlobA(TestCase):
    def setUp(self):
        self.g = MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.matchglobs(test_input))

        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['extractor.filesystem.xplat.contents.full'])
        _f(['extractor.filesystem.xplat.pathname.*', 'filesystem.pathname.full'])
        _f(['NAME_FORMAT'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.matchglobs(test_input))

        _t(['extractor.*'])
        _t(['extractor.filesystem.*'])
        _t(['extractor.filesystem.xplat.contents.*'])
        _t(['extractor.*', 'extractor.filesystem.xplat.pathname.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])


class TestEvalMeowURIGlobB(TestCase):
    def setUp(self):
        self.g = MeowURI(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL)

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.matchglobs(test_input))

        _f(['*.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['extractor.filesystem.xplat.contents.full'])
        _f(['extractor.filesystem.xplat.pathname.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['NAME_FORMAT'])
        _f(['extractor.filesystem.pathname.*'])
        _f(['extractor.filesystem.pathname.full'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.matchglobs(test_input))

        _t(['*.pathname.*', '*.basename.*', '*.full'])


class TestEvalMeowURIGlobC(TestCase):
    def setUp(self):
        self.g = MeowURI('generic.contents.textual.raw_text')

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.matchglobs(test_input))

        _f(['contents.text.*'])
        _f(['*.text.*'])
        _f(['*.text', '*.text', '*.text.*'])
        _f(['*.raw_*', '*.raw.*', '*.raw*.*', '*.*raw*.*'])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.matchglobs(test_input))

        _t(['generic.*'])
        _t(['*.contents.*'])
        _t(['*.textual.*'])
        _t(['*.pathname.*', '*.basename.*', '*.raw_text'])
        _t(['*.pathname.*', '*.textual.*', '*.foo'])


class TestEvalMeowURIGlobD(TestCase):
    def setUp(self):
        self.g = MeowURI(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT)

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.matchglobs(test_input))

        _f(['generic.*'])
        _f(['generic.contents.*'])
        _f([uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE])
        _f(['*.contents.mime_type'])
        _f(['*.mime_type'])
        _f(['extractor.filesystem.xplat.pathname.extension'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f(['*.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.matchglobs(test_input))

        _t(['*'])
        _t(['*.basename.*', '*.basename.extension',
            uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT])
        _t(['*.basename.extension'])
        _t(['*.basename.*', '*.basename.extension'])
        _t(['*', '*.basename.*', '*.basename.extension'])
        _t(['*.extension'])
        _t(['*', '*.extension'])


class TestEvalMeowURIGlobE(TestCase):
    def setUp(self):
        self.g = MeowURI(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL)

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.matchglobs(test_input))

        _f(['generic.*'])
        _f(['generic.contents.*'])
        _f([uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE])
        _f(['*.contents.mime_type'])
        _f(['*.mime_type'])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.matchglobs(test_input))

        _t(['*'])
        _t(['extractor.*'])
        _t(['extractor.filesystem.*'])
        _t(['extractor.filesystem.xplat.*'])
        _t(['extractor.filesystem.xplat.pathname.*'])
        _t([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _t(['extractor.filesystem.xplat.*',
            'extractor.filesystem.xplat.pathname.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _t(['*.pathname.*'])


class TestEvalMeowURIGlobF(TestCase):
    def setUp(self):
        self.g = MeowURI(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATOR)

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.matchglobs(test_input))

        _f(['datetime', 'date_accessed', 'date_created', 'date_modified',
            '*.PDF:CreateDate', '*.PDF:ModifyDate' '*.EXIF:DateTimeOriginal',
            '*.EXIF:ModifyDate'])
        _f(['generic.*'])
        _f(['extractor.filesystem.*'])
        _f(['extractor.filesystem.xplat.*'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['extractor.filesystem.xplat.*',
            'extractor.filesystem.xplat.pathname.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['*.pathname.*'])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.matchglobs(test_input))

        _t(['*'])
        _t(['extractor.*'])
        _t(['extractor.metadata.*'])
        _t(['extractor.metadata.exiftool.*'])
        _t([uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATOR])
        _t(['extractor.metadata.exiftool.*',
            uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATOR])
        _t(['*.metadata.exiftool.PDF:Creator'])
        _t(['*.exiftool.PDF:Creator'])
        _t(['*.PDF:Creator'])

    # def test_eval_glob_b(self):
    #     self.assertFalse(eval_meowuri_glob(
    #         'filesystem.pathname.parent', ['*.pathname.full',
    #                                        'filesystem.*.full']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'contents.textual.text.full', ['filesystem.*',
    #                                        'filesystem.pathname.*',
    #                                        'filesystem.pathname.full']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'filesystem.abspath.full', ['*.text.full']
    #     ))
    #
    #     self.assertTrue(eval_meowuri_glob(
    #         uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
    #         [uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE]
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
    #         ['extractor.metadata.exiftool.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
    #         ['extractor.metadata.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
    #         ['datetime', 'date_accessed', 'date_created', 'date_modified',
    #          '*.PDF:CreateDate', '*.PDF:ModifyDate' '*.EXIF:DateTimeOriginal',
    #          '*.EXIF:ModifyDate']
    #     ))


class TestMeowURIContains(TestCase):
    def test_empty_meowuri_returns_false(self):
        def _aF(test_input):
            for _dummy_meowuris in uuconst.DUMMY_MAPPED_MEOWURIS:
                m = MeowURI(_dummy_meowuris)
                actual = test_input in m
                self.assertFalse(actual)
                self.assertTrue(isinstance(actual, bool))

        _aF(None)
        _aF('')

    def test_invalid_meowuri_returns_false(self):
        def _aF(test_input):
            for _dummy_meowuris in uuconst.DUMMY_MAPPED_MEOWURIS:
                m = MeowURI(_dummy_meowuris)
                actual = test_input in m
                self.assertFalse(actual)
                self.assertTrue(isinstance(actual, bool))

        _aF(1)
        _aF(1.0)
        _aF(object())
        _aF(' ')
        _aF('  ')
        _aF('foo')

    def test_subset_returns_true(self):
        m = MeowURI('extractor.filesystem.xplat.contents.mime_type')

        def _aT(test_input):
            actual = test_input in m
            self.assertTrue(actual)
            self.assertTrue(isinstance(actual, bool))

        _aT('extractor.filesystem.xplat.contents.mime_type')
        _aT('extractor.filesystem.xplat.contents')
        _aT('extractor.filesystem.xplat')
        _aT('extractor.filesystem')
        _aT('extractor')


class TestMeowURIList(TestCase):
    def test_raises_exception_for_none_argument(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list(None))

    def test_raises_exception_for_empty_argument(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list(''))

    def test_raises_exception_for_only_periods(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list('.'))
            self.assertIsNone(meowuri_list('..'))
            self.assertIsNone(meowuri_list('...'))

    def test_return_value_is_type_list(self):
        self.assertTrue(isinstance(meowuri_list('a.b'), list))

    def test_valid_argument_returns_expected(self):
        self.assertEqual(meowuri_list('a'), ['a'])
        self.assertEqual(meowuri_list('a.b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a.b.c'), ['a', 'b', 'c'])
        self.assertEqual(meowuri_list('a.b.c.a'), ['a', 'b', 'c', 'a'])
        self.assertEqual(meowuri_list('a.b.c.a.b'),
                         ['a', 'b', 'c', 'a', 'b'])
        self.assertEqual(meowuri_list('a.b.c.a.b.c'),
                         ['a', 'b', 'c', 'a', 'b', 'c'])

    def test_valid_argument_returns_expected_for_unexpected_input(self):
        self.assertEqual(meowuri_list('a.b.'), ['a', 'b'])
        self.assertEqual(meowuri_list('a.b..'), ['a', 'b'])
        self.assertEqual(meowuri_list('.a.b'), ['a', 'b'])
        self.assertEqual(meowuri_list('..a.b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('.a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('..a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('...a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b.'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b..'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b...'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('.a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('..a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('...a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b.'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b..'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b...'), ['a', 'b'])

    def test_returns_expected(self):
        self.assertEqual(meowuri_list('filesystem.contents.mime_type'),
                         ['filesystem', 'contents', 'mime_type'])
        self.assertEqual(meowuri_list('metadata.exiftool.EXIF:Foo'),
                         ['metadata', 'exiftool', 'EXIF:Foo'])


class TestMeowURIIsGeneric(TestCase):
    def test_generic_meowuris_return_true(self):
        def _aT(test_input):
            actual = MeowURI(test_input).is_generic
            self.assertTrue(actual)

        _aT(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        _aT(uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        _aT(uuconst.MEOWURI_GEN_METADATA_AUTHOR)
        _aT(uuconst.MEOWURI_GEN_METADATA_CREATOR)
        _aT(uuconst.MEOWURI_GEN_METADATA_PRODUCER)
        _aT(uuconst.MEOWURI_GEN_METADATA_SUBJECT)
        _aT(uuconst.MEOWURI_GEN_METADATA_TAGS)
        _aT(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
        _aT(uuconst.MEOWURI_GEN_METADATA_DATEMODIFIED)

    def test_non_generic_meowuris_return_false(self):
        def _aF(test_input):
            actual = MeowURI(test_input).is_generic
            self.assertFalse(actual)

        _aF(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _aF(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        _aF(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE)


class TestMeowURIBasedOnDebuggerFindings(TestCase):
    def _check(self, *test_input, expected=None):
        actual = MeowURI(*test_input)
        self.assertEqual(expected, str(actual))

    def test_extraction_collect_results(self):
        _prefix = 'extractor.filesystem.xplat'
        _leaf = 'basename.suffix'
        self._check(_prefix, _leaf,
                    expected='extractor.filesystem.xplat.basename.suffix')

    def test_extraction_collect_extractor_xplat_filesystem(self):
        _prefix = 'extractor.filesystem.xplat'
        for _key in ['abspath.full', 'basename.full', 'basename.extension',
                     'basename.suffix', 'basename.prefix', 'contents.mime_type',
                     'date_accessed', 'date_created', 'date_modified',
                     'pathname.full', 'pathname.parent']:
            self._check(_prefix, _key, expected='{}.{}'.format(_prefix, _key))

    def test_extraction_collect_extractor_metadata_exiftool(self):
        _prefix = 'extractor.metadata.exiftool'
        for _key in ['SourceFile', 'File:FileName', 'File:Directory',
                     'File:FileSize', 'File:FileModifyDate',
                     'File:FileAccessDate', 'File:MIMEType', 'PDF:Creator']:
            self._check(_prefix, _key, expected='{}.{}'.format(_prefix, _key))

    def test_extraction_collect_extractor_text_pdftotext(self):
        _prefix = 'extractor.text.pdftotext'
        _key = 'full'
        self._check(_prefix, _key, expected='extractor.text.pdftotext.full')

    def test_extraction_collect_extractor_metadata_jpeginfo(self):
        _prefix = 'extractor.metadata.jpeginfo'
        for _key in ['health', 'is_jpeg']:
            self._check(_prefix, _key, expected='{}.{}'.format(_prefix, _key))


class TestMeowURIwithValidInput(TestCase):
    @staticmethod
    def _format_expected(root=None, child=None, leaf=None):
        if root is None and child is None and leaf is None:
            raise AssertionError('This should not happen. Bad test input.')

        if child is None and leaf is None:
            return '{root}'.format(root=root)
        elif leaf is None:
            return '{root}{sep}{child}'.format(
                root=root, sep=C.MEOWURI_SEPARATOR, child=child
            )
        else:
            return '{root}{sep}{child}{sep}{leaf}'.format(
                root=root, sep=C.MEOWURI_SEPARATOR, child=child, leaf=leaf
            )

    def test_multiple_arguments(self):
        a = MeowURI('extractor', 'filesystem', 'xplat')
        ea = self._format_expected(
            root='extractor', child='filesystem', leaf='xplat'
        )
        self.assertEqual(ea, str(a))

        b = MeowURI('extractor', 'filesystem')
        eb = self._format_expected(
            root='extractor', child='filesystem'
        )
        self.assertEqual(eb, str(b))

    def test_single_argument(self):
        a = MeowURI('extractor.filesystem.xplat')
        ea = self._format_expected(
            root='extractor', child='filesystem', leaf='xplat'
        )
        self.assertEqual(ea, str(a))

        b = MeowURI('extractor.filesystem')
        eb = self._format_expected(
            root='extractor', child='filesystem'
        )
        self.assertEqual(eb, str(b))


class TestDifferentNumberOfStringArgs(TestCase):
    def test_valid_meowuri_a(self):
        def _aE(*args):
            actual = MeowURI(*args)
            self.assertEqual(str(actual), 'generic.contents.text')
            actual_two = MeowURI(args)
            self.assertEqual(str(actual_two), 'generic.contents.text')

        _aE('generic.contents.text')
        _aE('generic.contents', 'text')
        _aE('generic', 'contents.text')
        _aE('generic', 'contents', 'text')

    def test_valid_meowuri_b(self):
        def _aE(*args):
            actual = MeowURI(*args)
            self.assertEqual(
                str(actual), 'extractor.filesystem.xplat.basename.suffix'
            )

        _aE('extractor.filesystem.xplat.basename.suffix')
        _aE('extractor.filesystem.xplat.basename', 'suffix')
        _aE('extractor.filesystem.xplat', 'basename', 'suffix')
        _aE('extractor.filesystem', 'xplat', 'basename', 'suffix')
        _aE('extractor', 'filesystem', 'xplat', 'basename', 'suffix')
        _aE('extractor', 'filesystem.xplat.basename.suffix')
        _aE('extractor', 'filesystem', 'xplat.basename.suffix')
        _aE('extractor', 'filesystem', 'xplat', 'basename.suffix')


class TestMeowURIParser(TestCase):
    def setUp(self):
        self.p = MeowURIParser()

    def test_parse_none_raises_exception(self):
        with self.assertRaises(InvalidMeowURIError):
            self.p.parse(None)

    def test_partitions_parts(self):
        a = self.p.parse(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertTrue(isinstance(a[0], MeowURIRoot))
        self.assertTrue(isinstance(a[1], list))
        self.assertTrue(isinstance(a[1][0], MeowURIChild))
        self.assertTrue(isinstance(a[2], MeowURILeaf))

        b = self.p.parse('extractor.metadata.exiftool.File:MIMEType')
        self.assertTrue(isinstance(b[0], MeowURIRoot))
        self.assertTrue(isinstance(b[1], list))
        self.assertTrue(isinstance(b[1][0], MeowURIChild))
        self.assertTrue(isinstance(b[1][1], MeowURIChild))
        self.assertTrue(isinstance(b[2], MeowURILeaf))

    def test_returns_partitioned_parts_as_strings(self):
        a = self.p.parse(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertEqual(str(a[0]), 'generic')
        self.assertEqual(str(a[1][0]), 'contents')
        self.assertEqual(str(a[2]), 'mime_type')

        b = self.p.parse('extractor.metadata.exiftool.File:MIMEType')
        self.assertEqual(str(b[0]), 'extractor')
        self.assertEqual(str(b[1][0]), 'metadata')
        self.assertEqual(str(b[1][1]), 'exiftool')
        self.assertEqual(str(b[2]), 'File:MIMEType')
