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

from core import constants as C
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.model.meowuri import (
    MeowURILeaf,
    MeowURINode,
    MeowURIRoot,
    is_meowuri_part,
    is_meowuri_parts
)
import unit_utils as uu
import unit_utils_constants as uuconst


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
                a = MeowURIRoot(test_input)

        _f(None)
        _f('')
        _f('foo')
        _f('analysis')
        _f('filesystem')
        _f('plugins')
        _f('metadata')


class TestMeowURIwithValidInput(TestCase):
    @staticmethod
    def _format_expected(root=None, node=None, leaf=None):
        if root is None and node is None and leaf is None:
            raise AssertionError('This should not happen. Bad test input.')

        if node is None and leaf is None:
            return '{root}'.format(root=root)
        elif leaf is None:
            return '{root}{sep}{node}'.format(
                root=root, sep=C.MEOWURI_SEPARATOR, node=node
            )
        else:
            return '{root}{sep}{node}{sep}{leaf}'.format(
                root=root, sep=C.MEOWURI_SEPARATOR, node=node, leaf=leaf
            )

    def test_multiple_arguments(self):
        a = MeowURI('extractor', 'filesystem', 'xplat')
        ea = self._format_expected(
            root='extractor', node='filesystem', leaf='xplat'
        )
        self.assertEqual(ea, str(a))

        b = MeowURI('extractor', 'filesystem')
        eb = self._format_expected(
            root='extractor', node='filesystem'
        )
        self.assertEqual(eb, str(b))

    def test_single_argument(self):
        a = MeowURI('extractor.filesystem.xplat')
        ea = self._format_expected(
            root='extractor', node='filesystem', leaf='xplat'
        )
        self.assertEqual(ea, str(a))

        b = MeowURI('extractor.filesystem')
        eb = self._format_expected(
            root='extractor', node='filesystem'
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


class TestMeowURI(TestCase):
    def test_partitions_parts(self):
        a = MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertTrue(isinstance(a._root, MeowURIRoot))
        self.assertTrue(isinstance(a._nodes, list))
        self.assertTrue(isinstance(a._nodes[0], MeowURINode))
        self.assertTrue(isinstance(a._leaf, MeowURILeaf))

        b = MeowURI('extractor.metadata.exiftool.File:MIMEType')
        self.assertTrue(isinstance(b._root, MeowURIRoot))
        self.assertTrue(isinstance(b._nodes, list))
        self.assertTrue(isinstance(b._nodes[0], MeowURINode))
        self.assertTrue(isinstance(b._nodes[1], MeowURINode))
        self.assertTrue(isinstance(b._leaf, MeowURILeaf))

    def test_returns_partitioned_parts_as_strings(self):
        a = MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertTrue(uu.is_internalstring(a.root))
        self.assertTrue(isinstance(a.nodes, list))
        self.assertTrue(uu.is_internalstring(a.nodes[0]))
        self.assertTrue(uu.is_internalstring(a.leaf))
        self.assertEqual(a.root, 'generic')
        self.assertEqual(a.nodes[0], 'contents')
        self.assertEqual(a.leaf, 'mime_type')

        b = MeowURI('extractor.metadata.exiftool.File:MIMEType')
        self.assertEqual(b.root, 'extractor')
        self.assertEqual(b.nodes[0], 'metadata')
        self.assertEqual(b.nodes[1], 'exiftool')
        self.assertEqual(b.leaf, 'File:MIMEType')


class TestMeowURIBasedOnDebuggerFindings(TestCase):
    def test_extraction_collect_results(self):
        _prefix = 'extractor.filesystem.xplat'
        _leaf = 'basename.suffix'
        a = MeowURI(_prefix, _leaf)
        e = 'extractor.filesystem.xplat.basename.suffix'
        self.assertEqual(str(a), e)

    def test_extraction_collect_extractor_xplat_filesystem(self):
        _prefix = 'extractor.filesystem.xplat'
        for _key in ['abspath.full', 'basename.full', 'basename.extension',
                     'basename.suffix', 'basename.prefix', 'contents.mime_type',
                     'date_accessed', 'date_created', 'date_modified',
                     'pathname.full', 'pathname.parent']:
            a = MeowURI(_prefix, _key)
            e = '{}.{}'.format(_prefix, _key)
            self.assertEqual(str(a), e)

    def test_extraction_collect_extractor_metadata_exiftool(self):
        _prefix = 'extractor.metadata.exiftool'
        for _key in ['SourceFile', 'File:FileName', 'File:Directory',
                     'File:FileSize', 'File:FileModifyDate',
                     'File:FileAccessDate', 'File:MIMEType', 'PDF:Creator']:
            a = MeowURI(_prefix, _key)
            e = '{}.{}'.format(_prefix, _key)
            self.assertEqual(str(a), e)

    def test_extraction_collect_extractor_metadata_pypdf(self):
        _prefix = 'extractor.metadata.pypdf'
        for _key in ['Creator', 'Producer', 'CreationDate', 'ModDate',
                     'creator', 'producer', 'creator_raw']:
            a = MeowURI(_prefix, _key)
            e = '{}.{}'.format(_prefix, _key)
            self.assertEqual(str(a), e)

    def test_extraction_collect_extractor_text_pdftotext(self):
        _prefix = 'extractor.text.pdftotext'
        _key = 'full'
        a = MeowURI(_prefix, _key)
        e = 'extractor.text.pdftotext.full'
        self.assertEqual(str(a), e)

    def test_extraction_collect_extractor_metadata_jpeginfo(self):
        _prefix = 'extractor.metadata.jpeginfo'
        for _key in ['health', 'is_jpeg']:
            a = MeowURI(_prefix, _key)
            e = '{}.{}'.format(_prefix, _key)
            self.assertEqual(str(a), e)


class TestMeowURIMutability(TestCase):
    def setUp(self):
        self.m = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test_attribute_parts_is_immutable(self):
        before = self.m.parts

        with self.assertRaises(AttributeError):
            self.m.parts = ['foo']

        after = self.m.parts
        self.assertEqual(before, after)


class TestMeowURIClassMethodGeneric(TestCase):
    def test_returns_expected_from_string(self):
        actual = MeowURI.generic('contents.text')
        self.assertEqual(str(actual), uuconst.MEOWURI_GEN_CONTENTS_TEXT)

    def test_returns_expected_from_string_with_root(self):
        actual = MeowURI.generic(uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        self.assertEqual(str(actual), uuconst.MEOWURI_GEN_CONTENTS_TEXT)

    def test_returns_expected_from_multiple_strings(self):
        actual = MeowURI.generic('contents', 'text')
        self.assertEqual(str(actual), uuconst.MEOWURI_GEN_CONTENTS_TEXT)

    def test_returns_expected_from_multiple_strings_with_root(self):
        actual = MeowURI.generic('generic', 'contents', 'text')
        self.assertEqual(str(actual), uuconst.MEOWURI_GEN_CONTENTS_TEXT)


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
