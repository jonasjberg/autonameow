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


class TestMeowURIRoot(TestCase):
    def test_from_valid_input(self):
        self.skipTest('TODO: ..')

        def _ok(test_input):
            a = MeowURIRoot(test_input)
            self.assertIsNotNone(a)

        _ok('analysis')
        _ok('filesystem')
        _ok('metadata')
        _ok('plugin')
        _ok(' analysis')
        _ok(' filesystem')
        _ok(' metadata')
        _ok(' plugin')
        _ok(' analysis ')
        _ok(' filesystem ')
        _ok(' metadata ')
        _ok(' plugin ')

    def test_from_invalid_input(self):
        self.skipTest('TODO: ..')

        def _f(test_input):
            with self.assertRaises(InvalidMeowURIError):
                a = MeowURIRoot(test_input)

        _f(None)
        _f('')
        _f('foo')
        _f('plugins')


class TestMeowURIwithValidInput(TestCase):
    def _format_expected(self, root=None, node=None, leaf=None):
        if root is None and node is None and leaf is None:
            raise AssertionError('This should not happen')
        elif node is None and leaf is None:
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
        a = MeowURI('generic.contents.mimetype')
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
        a = MeowURI('generic.contents.mimetype')
        self.assertTrue(isinstance(a.root, str))
        self.assertTrue(isinstance(a.nodes, list))
        self.assertTrue(isinstance(a.nodes[0], str))
        self.assertTrue(isinstance(a.leaf, str))
        self.assertEqual(a.root, 'generic')
        self.assertEqual(a.nodes[0], 'contents')
        self.assertEqual(a.leaf, 'mimetype')

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
        self.assertEqual(str(actual), 'generic.contents.text')

    def test_returns_expected_from_string_with_root(self):
        actual = MeowURI.generic('generic.contents.text')
        self.assertEqual(str(actual), 'generic.contents.text')

    def test_returns_expected_from_multiple_strings(self):
        actual = MeowURI.generic('contents', 'text')
        self.assertEqual(str(actual), 'generic.contents.text')

    def test_returns_expected_from_multiple_strings_with_root(self):
        actual = MeowURI.generic('generic', 'contents', 'text')
        self.assertEqual(str(actual), 'generic.contents.text')


class TestEvalMeowURIGlob(TestCase):
    def test_eval_meowuri_blob_returns_false_given_bad_arguments(self):
        self.skipTest('TODO: ..')

        m = MeowURI('a.b.c')
        actual = m.eval_glob(None)
        self.assertIsNotNone(actual)
        self.assertFalse(actual)


class TestEvalMeowURIGlobA(TestCase):
    def setUp(self):
        self.skipTest('TODO')

        self.g = MeowURI('filesystem.contents.mime_type')

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.eval_glob(test_input))

        _f(['filesystem.pathname.*'])
        _f(['filesystem.pathname.full'])
        _f(['filesystem.contents.full'])
        _f(['filesystem.pathname.*', 'filesystem.pathname.full'])
        _f(['NAME_FORMAT'])
        _f(['filesystem.pathname.*'])
        _f(['filesystem.pathname.full'])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.eval_glob(test_input))

        _t(['filesystem.*'])
        _t(['filesystem.contents.*'])
        _t(['filesystem.*', 'filesystem.pathname.*',
            'filesystem.pathname.full'])


class TestEvalMeowURIGlobB(TestCase):
    def setUp(self):
        self.skipTest('TODO')

        self.g = MeowURI('filesystem.basename.full')

    def test_evaluates_false(self):
        def _f(test_input):
            self.assertFalse(self.g.eval_glob(test_input))

        _f(['*.pathname.*'])
        _f(['filesystem.pathname.full'])
        _f(['filesystem.contents.full'])
        _f(['filesystem.pathname.*', 'filesystem.pathname.full'])
        _f(['NAME_FORMAT'])
        _f(['filesystem.pathname.*'])
        _f(['filesystem.pathname.full'])

    def test_evaluates_true(self):
        def _t(test_input):
            self.assertTrue(self.g.eval_glob(test_input))

        _t(['*.pathname.*', '*.basename.*', '*.full'])


    # def test_eval_glob_b(self):
    #     self.assertFalse(eval_meowuri_glob(
    #         'filesystem.pathname.extension', ['*.basename.*',
    #                                           '*.basename.extension',
    #                                           'filesystem.basename.extension']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'filesystem.pathname.parent', ['*.pathname.full',
    #                                        'filesystem.*.full']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'extractor.metadata.exiftool.PDF:Creator',
    #         ['datetime', 'date_accessed', 'date_created', 'date_modified',
    #          '*.PDF:CreateDate', '*.PDF:ModifyDate' '*.EXIF:DateTimeOriginal',
    #          '*.EXIF:ModifyDate']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'contents.textual.text.full', ['filesystem.*',
    #                                        'filesystem.pathname.*',
    #                                        'filesystem.pathname.full']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'contents.textual.raw_text', ['contents.text.*']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'contents.textual.raw_text', ['*.text.*']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'contents.textual.raw_text', ['*.text', '*.text', '*.text.*']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'contents.textual.raw_text', ['*.raw_*', '*.raw.*', '*.raw*.*'
    #                                                             '*.*raw*.*']
    #     ))
    #     self.assertFalse(eval_meowuri_glob(
    #         'filesystem.abspath.full', ['*.text.full']
    #     ))
    #
    # def test_eval_meowuri_blob_returns_true_as_expected(self):
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['filesystem.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['filesystem.pathname.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['filesystem.pathname.full']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['filesystem.*',
    #                                      'filesystem.pathname.*',
    #                                      'filesystem.pathname.full']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['*',
    #                                      'filesystem.*',
    #                                      'filesystem.pathname.*',
    #                                      'filesystem.pathname.full']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.pathname.full', ['*.pathname.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.basename.extension', ['*.basename.*',
    #                                           '*.basename.extension',
    #                                           'filesystem.basename.extension']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.basename.extension', ['*',
    #                                           '*.basename.*',
    #                                           '*.basename.extension',
    #                                           'filesystem.basename.extension']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.basename.extension', ['*.extension']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'filesystem.basename.extension', ['*',
    #                                           '*.extension']
    #     ))
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
    #     self.assertTrue(eval_meowuri_glob(
    #         'contents.textual.text.full', ['contents.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'contents.textual.text.full', ['*.textual.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'contents.textual.text.full', ['*.text.*']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'contents.textual.text.full', ['*.full']
    #     ))
    #     self.assertTrue(eval_meowuri_glob(
    #         'contents.textual.text.full', ['contents.*', '*.textual.*',
    #                                        '*.text.*', '*.full']
    #     ))


