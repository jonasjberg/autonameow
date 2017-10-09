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
from core.meowuri import (
    MeowURI,
    MeowURIRoot,
    MeowURILeaf,
    MeowURINode
)
import unit_utils as uu
import unit_utils_constants as uuconst


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

    def test___getattr__(self):
        self.skipTest('TODO: Implement or remove ..')

        a = MeowURI('filesystem.abspath.full')
        self.assertEqual(a.filesystem, 'abspath')
        self.assertEqual(a.filesystem.abspath, 'full')


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
        self.a = MeowURI('extractor.filesystem.xplat.abspath.full')

    def test_compare_with_string(self):
        self.assertEqual(self.m, uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertNotEqual(self.m, uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        self.assertNotEqual(self.m, 'extractor.filesystem.xplat.abspath.full')

        self.assertEqual(self.a, 'extractor.filesystem.xplat.abspath.full')
        self.assertNotEqual(self.a, uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        self.assertNotEqual(self.a, uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)


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
        self.g = MeowURI('extractor.metadata.exiftool.PDF:Creator')

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
        _t(['extractor.metadata.exiftool.PDF:Creator'])
        _t(['extractor.metadata.exiftool.*',
            'extractor.metadata.exiftool.PDF:Creator'])
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
    #         'extractor.metadata.exiftool.PDF:CreateDate',
    #         ['extractor.metadata.exiftool.PDF:CreateDate']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'extractor.metadata.exiftool.PDF:CreateDate',
    #         ['extractor.metadata.exiftool.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'extractor.metadata.exiftool.PDF:CreateDate',
    #         ['extractor.metadata.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'extractor.metadata.exiftool.PDF:CreateDate',
    #         ['datetime', 'date_accessed', 'date_created', 'date_modified',
    #          '*.PDF:CreateDate', '*.PDF:ModifyDate' '*.EXIF:DateTimeOriginal',
    #          '*.EXIF:ModifyDate']
    #     ))


