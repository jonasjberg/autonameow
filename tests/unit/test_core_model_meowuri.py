# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import unit.utils as uu
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.model.meowuri import evaluate_meowuri_globs
from core.model.meowuri import force_meowuri
from core.model.meowuri import is_meowuri_parts
from core.model.meowuri import is_one_meowuri_part
from core.model.meowuri import meowuri_list
from core.model.meowuri import MeowURILeaf
from core.model.meowuri import MeowURIChild
from core.model.meowuri import MeowURINode
from core.model.meowuri import MeowURIParser
from core.model.meowuri import MeowURIRoot


class TestIsOneMeowURIPart(TestCase):
    def tearDown(self):
        # Call 'cache_clear()' added by the 'functools.lru_cache' decorator.
        meowuri_list.cache_clear()

    def test_returns_true_given_valid_meowuri_parts(self):
        def _assert_meowuri_part(test_input):
            actual = is_one_meowuri_part(test_input)
            self.assertIsInstance(actual, bool)
            self.assertTrue(actual)

        _assert_meowuri_part('f')
        _assert_meowuri_part('foo')
        _assert_meowuri_part('123')
        _assert_meowuri_part('foo123')
        _assert_meowuri_part('_')

    def test_returns_false_given_non_meowuri_part(self):
        def _assert_not_meowuri_part(test_input):
            actual = is_one_meowuri_part(test_input)
            self.assertIsInstance(actual, bool)
            self.assertFalse(actual)

        for _bad_input in [None, b'', b'foo', 1, object()]:
            _assert_not_meowuri_part(_bad_input)

        _assert_not_meowuri_part('')
        _assert_not_meowuri_part(' ')
        _assert_not_meowuri_part('.')
        _assert_not_meowuri_part('..')
        _assert_not_meowuri_part(' .')
        _assert_not_meowuri_part(' ..')
        _assert_not_meowuri_part(' . ')
        _assert_not_meowuri_part(' .. ')
        _assert_not_meowuri_part('.foo')
        _assert_not_meowuri_part('foo.')
        _assert_not_meowuri_part('foo.bar')
        _assert_not_meowuri_part('.foo.bar')
        _assert_not_meowuri_part('.foo.bar.')


class TestIsMeowURIParts(TestCase):
    def tearDown(self):
        # Call 'cache_clear()' added by the 'functools.lru_cache' decorator.
        is_meowuri_parts.cache_clear()

    def _assert_meowuri_parts(self, given):
        actual = is_meowuri_parts(given)
        self.assertIsInstance(actual, bool)
        self.assertTrue(actual)

    def test_returns_true_given_valid_meowuri_parts(self):
        self._assert_meowuri_parts('f.o')
        self._assert_meowuri_parts('foo.bar')
        self._assert_meowuri_parts('123.bar')
        self._assert_meowuri_parts('foo.123')
        self._assert_meowuri_parts('f.o.b')
        self._assert_meowuri_parts('foo.bar.baz')
        self._assert_meowuri_parts('123.bar.baz')
        self._assert_meowuri_parts('foo.123.baz')
        # TODO: Normalize exiftool tags? Translate to some "custom" format?
        self._assert_meowuri_parts(':.:')
        self._assert_meowuri_parts('extractor.filesystem.xplat.mime_type')

    def test_returns_false_given_non_meowuri_parts(self):
        def _assert_not_meowuri_parts(test_input):
            actual = is_meowuri_parts(test_input)
            self.assertIsInstance(actual, bool)
            self.assertFalse(actual)

        for _bad_input in [None, b'', b'foo', 1, object()]:
            _assert_not_meowuri_parts(_bad_input)

        _assert_not_meowuri_parts('')
        _assert_not_meowuri_parts(' ')
        _assert_not_meowuri_parts('.')
        _assert_not_meowuri_parts('..')
        _assert_not_meowuri_parts(' .')
        _assert_not_meowuri_parts(' ..')
        _assert_not_meowuri_parts(' . ')
        _assert_not_meowuri_parts(' .. ')
        _assert_not_meowuri_parts('f')
        _assert_not_meowuri_parts('foo')
        _assert_not_meowuri_parts('123')
        _assert_not_meowuri_parts('foo123')
        _assert_not_meowuri_parts('_')
        _assert_not_meowuri_parts('.foo')
        _assert_not_meowuri_parts('foo.')
        _assert_not_meowuri_parts('foo. ')
        _assert_not_meowuri_parts('.foo.bar')
        _assert_not_meowuri_parts('foo.bar.')
        _assert_not_meowuri_parts('.foo.bar.')

    def test_all_full_meowuris_defined_in_unit_test_constants(self):
        for given in uuconst.ALL_FULL_MEOWURIS:
            self._assert_meowuri_parts(given)


class TestMeowURI(TestCase):
    def setUp(self):
        self.m = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test___str__(self):
        self.assertEqual(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL, str(self.m))

    def test___repr__(self):
        expect = '<MeowURI({})>'.format(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        self.assertEqual(expect, repr(self.m))


class TestMeowURIStripLeaf(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test_returns_meowuri_without_the_leaf(self):
        actual = self.m.stripleaf()
        self.assertIsInstance(actual, MeowURI)
        self.assertEqual('extractor.filesystem.xplat', str(actual))


class TestMeowURIRoot(TestCase):
    def test_returns_instance_of_meowuriroot_given_valid_arguments(self):
        for given in [
            'analyzer',
            'generic',
            ' analyzer',
            ' generic',
            ' analyzer ',
            ' generic ',
        ]:
            with self.subTest(given=given):
                actual = MeowURIRoot(given)
                self.assertIsNotNone(actual)

    def test_raises_exception_given_invalid_arguments(self):
        for given in [
            None,
            '',
            ' ',
            '.',
            'foo',
            'analysis',
            'filesystem',
            'metadata',
        ]:
            with self.subTest(given=given):
                with self.assertRaises(InvalidMeowURIError):
                    _ = MeowURIRoot(given)


class TestMeowURIMutability(TestCase):
    def setUp(self):
        self.m = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test_attribute_parts_is_immutable(self):
        before = self.m.parts

        with self.assertRaises(AttributeError):
            self.m.parts = ['foo']

        after = self.m.parts
        self.assertEqual(before, after)


class TestEvaluateMeowURIGlob(TestCase):
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
        self.assertNotEqual(self.m, uuconst.MEOWURI_GEN_METADATA_AUTHOR)
        self.assertNotEqual(self.m, uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        self.assertEqual(self.a, uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        self.assertNotEqual(self.a, uuconst.MEOWURI_GEN_METADATA_AUTHOR)
        self.assertNotEqual(self.a, uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)

    def test_compare_with_other_class_instances(self):
        self.assertNotEqual(self.m, self.a)

        b = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        c = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        self.assertEqual(b, c)

    def test_hashable_for_set_membership(self):
        a = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        b = MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        c = MeowURI(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        d = MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)

        container = set()
        container.add(a)
        self.assertIn(a, container)
        self.assertNotIn(b, container)
        self.assertIn(c, container)
        self.assertNotIn(d, container)

        container.add(d)
        self.assertIn(a, container)
        self.assertIn(b, container)
        self.assertIn(c, container)
        self.assertIn(d, container)

        container.remove(a)
        self.assertNotIn(a, container)
        self.assertIn(b, container)
        self.assertNotIn(c, container)
        self.assertIn(d, container)

    def test_compare_with_other_types(self):
        def _aF(test_input):
            self.assertNotEqual(self.m, test_input)

        _aF(None)
        _aF(object())
        _aF(1)
        _aF({})


class TestMeowURIComparison(TestCase):
    def test_less_than_based_on_length(self):
        a = MeowURI('extractor.filesystem.xplat')
        b = MeowURI('extractor.filesystem.xplat.basename_full')
        self.assertTrue(a < b)

    def test_greater_than_based_on_length(self):
        a = MeowURI('extractor.filesystem.xplat.basename_full')
        b = MeowURI('extractor.filesystem.xplat')
        self.assertTrue(a > b)

    def test_less_than_based_on_contents(self):
        a = MeowURI('extractor.filesystem.xplat.abspath_full')
        b = MeowURI('extractor.filesystem.xplat.pathname_full')
        self.assertTrue(a < b)

    def test_greater_than_based_on_contents(self):
        a = MeowURI('extractor.filesystem.xplat.pathname_full')
        b = MeowURI('extractor.filesystem.xplat.basename_full')
        self.assertTrue(a > b)

    def test_alphabetical_ordering(self):
        a = MeowURI('extractor.metadata.filetags.description')
        b = MeowURI('extractor.metadata.filetags.tags')
        c = MeowURI('extractor.filesystem.xplat.abspath_full')
        self.assertTrue(a < b)
        self.assertTrue(a > c)
        self.assertTrue(b > c)
        self.assertTrue(c < a)
        self.assertTrue(c < b)

    def test_comparison_with_other_types_raises_valueerror(self):
        a = MeowURI('extractor.filesystem.xplat.basename_full')
        b = object()

        with self.assertRaises(TypeError):
            _ = a < b

        with self.assertRaises(TypeError):
            _ = a > b

        with self.assertRaises(TypeError):
            _ = b < a

        with self.assertRaises(TypeError):
            _ = b > a


class TestEvaluateMeowURIGlobA(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meowuri_string = uuconst.MEOWURI_FS_XPLAT_MIMETYPE

    def test_evaluates_false(self):
        def _f(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertFalse(actual)

        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['extractor.filesystem.xplat.contents.full'])
        _f(['extractor.filesystem.xplat.pathname.*', 'filesystem.pathname_full'])
        _f(['NAME_TEMPLATE'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])

    def test_evaluates_true(self):
        def _t(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertTrue(actual)

        _t(['extractor.*'])
        _t(['extractor.filesystem.*'])
        _t(['extractor.filesystem.xplat.*'])
        _t(['extractor.*', 'extractor.filesystem.xplat.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])


class TestEvaluateMeowURIGlobB(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meowuri_string = uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL

    def test_evaluates_false(self):
        def _f(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertFalse(actual)

        _f(['*.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['extractor.filesystem.xplat.contents.full'])
        _f(['extractor.filesystem.xplat.pathname.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _f(['NAME_TEMPLATE'])
        _f(['extractor.filesystem.pathname.*'])
        _f(['extractor.filesystem.pathname_full'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])

    def test_evaluates_true(self):
        def _t(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertTrue(actual)

        _t(['*.basename_full'])
        _t(['*.xplat.basename_full'])
        _t(['*.pathname.*', '*.basename_full', '*.full'])


class TestEvaluateMeowURIGlobC(TestCase):
    def setUp(self):
        self.meowuri_string = 'generic.contents.textual.raw_text'

    def test_evaluates_false(self):
        def _f(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertFalse(actual)

        _f(['contents.text.*'])
        _f(['*.text.*'])
        _f(['*.text', '*.text', '*.text.*'])
        _f(['*.raw_*', '*.raw.*', '*.raw*.*', '*.*raw*.*'])

    def test_evaluates_true(self):
        def _t(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertTrue(actual)

        _t(['generic.*'])
        _t(['*.contents.*'])
        _t(['*.textual.*'])
        _t(['*.pathname.*', '*.basename.*', '*.raw_text'])
        _t(['*.pathname.*', '*.textual.*', '*.foo'])


class TestEvaluateMeowURIGlobD(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meowuri_string = uuconst.MEOWURI_FS_XPLAT_EXTENSION

    def test_evaluates_false(self):
        def _f(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertFalse(actual)

        _f(['generic.*'])
        _f(['generic.contents.*'])
        _f([uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE])
        _f(['*.mime_type'])
        _f(['extractor.filesystem.xplat.pathname.extension'])
        _f(['extractor.filesystem.xplat.pathname.*'])
        _f(['*.pathname.*'])
        _f([uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL])
        _f(['*.basename.*'])

    def test_evaluates_true(self):
        def _t(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertTrue(actual)

        _t(['*'])
        _t(['*.extension'])
        _t(['*', '*.xplat.*', '*.xplat.extension'])
        _t(['*.extension'])
        _t(['*', '*.extension'])


class TestEvaluateMeowURIGlobE(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meowuri_string = uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL

    def test_evaluates_false(self):
        def _f(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertFalse(actual)

        _f(['generic.*'])
        _f(['generic.contents.*'])
        _f([uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE])
        _f(['*.mime_type'])

    def test_evaluates_true(self):
        def _t(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertTrue(actual, test_input)

        _t(['*'])
        _t(['extractor.*'])
        _t(['extractor.filesystem.*'])
        _t(['extractor.filesystem.xplat.*'])
        _t([uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _t(['extractor.filesystem.xplat.*',
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL])
        _t(['*.xplat.*'])


class TestEvaluateMeowURIGlobF(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meowuri_string = uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATOR

    def test_evaluates_false(self):
        def _f(test_input):
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertFalse(actual)

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
            actual = evaluate_meowuri_globs(self.meowuri_string, test_input)
            self.assertTrue(actual)

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


class TestMeowURIContains(TestCase):
    def test_returns_false_given_empty_or_none_arguments(self):
        def _aF(test_input):
            for _dummy_meowuris in uuconst.DUMMY_MAPPED_MEOWURIS:
                m = uu.as_meowuri(_dummy_meowuris)
                self.assertNotIn(test_input, m)

        _aF(None)
        _aF(False)
        _aF(True)
        _aF([])
        _aF([''])
        _aF('')
        _aF(b'')

    def test_returns_false_given_invalid_arguments(self):
        def _aF(test_input):
            for _dummy_meowuris in uuconst.DUMMY_MAPPED_MEOWURIS:
                m = uu.as_meowuri(_dummy_meowuris)
                self.assertNotIn(test_input, m)

        _aF(1)
        _aF(1.0)
        _aF(object())
        _aF(' ')
        _aF('  ')
        _aF('foo')
        _aF(b' ')
        _aF(b'  ')
        _aF(b'foo')

    def test_returns_true_given_string_that_matches_from_the_start(self):
        m = uu.as_meowuri('extractor.filesystem.xplat.basename_suffix')
        for given in [
            'extractor.filesystem.xplat.basename_suffix',
            'extractor.filesystem.xplat',
            'extractor.filesystem',
            'extractor',
        ]:
            with self.subTest(given=given):
                self.assertIn(given, m)

    def test_returns_true_given_meowuri_that_matches_from_the_start(self):
        m = uu.as_meowuri('extractor.filesystem.xplat.basename_suffix')
        for given in [
            m,
            MeowURIRoot('extractor'),
            uu.as_meowuri('extractor.filesystem'),
            uu.as_meowuri('extractor.filesystem.xplat'),
        ]:
            with self.subTest(given=given):
                self.assertIn(given, m)

    def test_returns_true_given_string_that_matches_any_part(self):
        uri_str = uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE
        uri_parts_list = meowuri_list(uri_str)
        m = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE)
        for n in range(1, len(uri_parts_list)):
            # Try all parts, starting with the last (leaf)
            given = '.'.join(uri_parts_list[-n:])
            self.assertIn(given, m)


class TestMeowURIMatchesStart(TestCase):
    def _assert_matches_from_start_returns(self, expect, uri, given):
        actual = uri.matches_start(given)
        self.assertEqual(expect, actual)
        self.assertIsInstance(actual, bool)

    def test_returns_true_given_string_that_matches_from_the_start(self):
        m = MeowURI('extractor.filesystem.xplat.extension')
        for given in [
            'extractor',
            'extractor.filesystem',
            'extractor.filesystem.xplat',
            'extractor.filesystem.xplat.extension',
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_start_returns(True, m, given)

    def test_returns_true_given_meowuri_that_matches_from_the_start(self):
        m = MeowURI('extractor.filesystem.xplat.extension')
        for given in [
            m,
            MeowURIRoot('extractor'),
            uu.as_meowuri('extractor.filesystem'),
            uu.as_meowuri('extractor.filesystem.xplat'),
            uu.as_meowuri('extractor.filesystem.xplat.extension'),
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_start_returns(True, m, given)

    def test_returns_false_given_string_not_matching_from_the_start(self):
        m = MeowURI('extractor.filesystem.xplat.extension')
        for given in [
            uuconst.MEOWURI_AZR_FILENAME_DATETIME,
            uuconst.MEOWURI_EXT_FILETAGS_DATETIME,
            'extractor.metadata.filetags',
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_start_returns(False, m, given)

    def test_returns_false_given_meowuri_not_matching_from_the_start(self):
        m = MeowURI('extractor.filesystem.xplat.extension')
        for given in [
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL),
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL),
            uu.as_meowuri('extractor.metadata.filetags.extension'),
            uu.as_meowuri('extractor.metadata.filetags'),
            MeowURIRoot('analyzer'),
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_start_returns(False, m, given)

    def test_returns_false_given_invalid_arguments(self):
        m = MeowURI(uuconst.MEOWURI_FS_XPLAT_PATHNAME_PARENT)
        for given in [
            None,
            False,
            True,
            object(),
            1, 1.0,
            dict(), {'a': 1},
            [], ['a'], [1, 2], ['a', 'b'],
            '', ' ', '  ',
            b'', b' ', b'foo',

        ]:
            with self.subTest(given=given):
                self._assert_matches_from_start_returns(False, m, given)


class TestMeowURIMatchesEnd(TestCase):
    def _assert_matches_from_end_returns(self, expect, uri, given):
        actual = uri.matches_end(given)
        self.assertEqual(expect, actual)
        self.assertIsInstance(actual, bool)

    def test_returns_true_given_string_that_matches_from_the_end(self):
        m = MeowURI('extractor.filesystem.xplat.extension')
        for given in [
            'extension',
            'xplat.extension',
            'filesystem.xplat.extension',
            'extractor.filesystem.xplat.extension',
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_end_returns(True, m, given)

    def test_returns_true_given_meowuri_that_matches_from_the_end(self):
        m = MeowURI('extractor.filesystem.xplat.extension')
        for given in [
            m,
            MeowURILeaf('extension'),
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_end_returns(True, m, given)

    def test_returns_false_given_string_that_does_not_match_from_the_end(self):
        m = MeowURI('extractor.filesystem.xplat.mime_type')
        for given in [
            'extension',
            'xplat.extension',
            'filesystem.xplat.extension',
            'extractor.filesystem.xplat.extension',
            'extractor.filesystem.xplat',
            'extractor.filesystem',
            'extractor',
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_end_returns(False, m, given)

    def test_returns_false_given_meowuri_that_does_not_match_from_the_end(self):
        m = MeowURI('extractor.filesystem.xplat.mime_type')
        for given in [
            MeowURIRoot('extractor'),
            uu.as_meowuri('extractor.filesystem.xplat'),
            uu.as_meowuri('extractor.filesystem'),
            uu.as_meowuri(uuconst.MEOWURI_EXT_FILETAGS_DATETIME),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE),
        ]:
            with self.subTest(given=given):
                self._assert_matches_from_end_returns(False, m, given)

    def test_returns_false_given_invalid_arguments(self):
        m = MeowURI(uuconst.MEOWURI_FS_XPLAT_PATHNAME_PARENT)
        for given in [
            None,
            False,
            True,
            object(),
            1, 1.0,
            dict(), {'a': 1},
            [], ['a'], [1, 2], ['a', 'b'],
            '', ' ', '  ',
            b'', b' ', b'foo',

        ]:
            with self.subTest(given=given):
                self._assert_matches_from_end_returns(False, m, given)


class TestMeowURIList(TestCase):
    def tearDown(self):
        # Call 'cache_clear()' added by the 'functools.lru_cache' decorator.
        meowuri_list.cache_clear()

    def test_raises_exception_for_none_argument(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list(None))

    def test_raises_exception_for_empty_argument(self):
        with self.assertRaises(InvalidMeowURIError):
            _ = meowuri_list('')

    def test_raises_exception_for_non_string_argument(self):
        for given in (b'', b' ', b'foo', b'foo.bar'):
            with self.assertRaises(InvalidMeowURIError):
                _ = meowuri_list(given)

    def test_raises_exception_for_only_periods(self):
        for given in ('.', ' .', '. ', ' . ',
                      '..', ' ..', '.. ', ' .. ',
                      '...', ' ...', '... ', ' ... '):
            with self.assertRaises(InvalidMeowURIError):
                _ = meowuri_list(given)

    def test_return_value_is_type_list(self):
        for given in ('a', 'a.b', 'a.b.c', 'foo.bar'):
            self.assertIsInstance(meowuri_list(given), list)

    def test_valid_argument_returns_expected(self):
        for given, expect in [
            ('a', ['a']),
            ('a.b', ['a', 'b']),
            ('a.b.c', ['a', 'b', 'c']),
            ('a.b.c.a', ['a', 'b', 'c', 'a']),
            ('a.b.c.a.b', ['a', 'b', 'c', 'a', 'b']),
            ('a.b.c.a.b.c', ['a', 'b', 'c', 'a', 'b', 'c']),
        ]:
            with self.subTest(given=given, expect=expect):
                self.assertEqual(expect, meowuri_list(given))

    def test_valid_argument_returns_expected_for_unexpected_input(self):
        for given, expect in [
            ('a.b.', ['a', 'b']),
            ('a.b..', ['a', 'b']),
            ('.a.b', ['a', 'b']),
            ('..a.b', ['a', 'b']),
            ('a..b', ['a', 'b']),
            ('.a..b', ['a', 'b']),
            ('..a..b', ['a', 'b']),
            ('...a..b', ['a', 'b']),
            ('a..b.', ['a', 'b']),
            ('a..b..', ['a', 'b']),
            ('a..b...', ['a', 'b']),
            ('a...b', ['a', 'b']),
            ('.a...b', ['a', 'b']),
            ('..a...b', ['a', 'b']),
            ('...a...b', ['a', 'b']),
            ('a...b.', ['a', 'b']),
            ('a...b..', ['a', 'b']),
            ('a...b...', ['a', 'b'])
        ]:
            with self.subTest(given=given, expect=expect):
                self.assertEqual(expect, meowuri_list(given))

    def test_returns_expected_given_assumedly_correct_sample_meowuris(self):
        for given, expect in [
            ('filesystem.mime_type', ['filesystem', 'mime_type']),
            ('metadata.exiftool.EXIF:Foo', ['metadata', 'exiftool', 'EXIF:Foo'])
        ]:
            with self.subTest(given=given, expect=expect):
                self.assertEqual(expect, meowuri_list(given))


class TestMeowURIIsGeneric(TestCase):
    def test_generic_meowuris_return_true(self):
        def _assert_meowuri_true(test_input):
            actual = MeowURI(test_input).is_generic
            self.assertTrue(actual)

        _assert_meowuri_true(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_AUTHOR)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_CREATOR)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_PRODUCER)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_SUBJECT)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_TAGS)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
        _assert_meowuri_true(uuconst.MEOWURI_GEN_METADATA_DATEMODIFIED)

    def test_non_generic_meowuris_return_false(self):
        def _assert_meowuri_false(test_input):
            actual = MeowURI(test_input).is_generic
            self.assertFalse(actual)

        _assert_meowuri_false(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _assert_meowuri_false(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        _assert_meowuri_false(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE)


class TestMeowURIBasedOnDebuggerFindings(TestCase):
    def _check(self, *test_input, expected=None):
        actual = MeowURI(*test_input)
        self.assertEqual(expected, str(actual))

    def test_extraction_store_results(self):
        _prefix = 'extractor.filesystem.xplat'
        _leaf = 'basename_suffix'
        self._check(_prefix, _leaf,
                    expected='extractor.filesystem.xplat.basename_suffix')

    def test_extraction_collect_extractor_xplat_filesystem(self):
        _prefix = 'extractor.filesystem.xplat'
        for _key in ['abspath_full', 'basename_full', 'extension',
                     'basename_suffix', 'basename_prefix', 'mime_type',
                     'date_accessed', 'date_created', 'date_modified',
                     'pathname_full', 'pathname_parent']:
            self._check(_prefix, _key, expected='{}.{}'.format(_prefix, _key))

    def test_extraction_collect_extractor_metadata_exiftool(self):
        _prefix = 'extractor.metadata.exiftool'
        for _key in ['SourceFile', 'File:FileName', 'File:Directory',
                     'File:FileSize', 'File:FileModifyDate',
                     'File:FileAccessDate', 'File:MIMEType', 'PDF:Creator']:
            self._check(_prefix, _key, expected='{}.{}'.format(_prefix, _key))

    def test_extraction_collect_extractor_text_pdf(self):
        _prefix = 'extractor.text.pdf'
        _key = 'full'
        self._check(_prefix, _key, expected='extractor.text.pdf.full')

    def test_extraction_collect_extractor_metadata_jpeginfo(self):
        _prefix = 'extractor.metadata.jpeginfo'
        for _key in ['health', 'is_jpeg']:
            self._check(_prefix, _key, expected='{}.{}'.format(_prefix, _key))

    def test_analyzer_ebook_title(self):
        self._check('analyzer.ebook.title', expected='analyzer.ebook.title')


class TestDifferentCombinationsOfStringAndMeowURIArgs(TestCase):
    def _assert_meowuri_str(self, expect, *given):
        assert isinstance(expect, str)
        actual = MeowURI(given)
        self.assertEqual(expect, str(actual))

    def test_one_string_argument_with_one_part_and_one_meowuri_instance(self):
        self._assert_meowuri_str(
            'extractor.metadata.exiftool.author',
            uu.as_meowuri('extractor.metadata.exiftool'), 'author'
        )
        self._assert_meowuri_str(
            'extractor.filesystem.xplat.date_created',
            uu.as_meowuri('extractor.filesystem.xplat'), 'date_created'
        )

    def test_one_string_argument_with_two_parts_and_one_meowuri_instance(self):
        self._assert_meowuri_str(
            'extractor.filesystem.xplat.extension',
            uu.as_meowuri('extractor.filesystem'), 'xplat.extension'
        )
        self._assert_meowuri_str(
            'extractor.filesystem.xplat.abspath_full',
            uu.as_meowuri('extractor.filesystem'), 'xplat.abspath_full'
        )

    def test_two_string_arguments_with_one_part_and_one_meowuri_instance(self):
        self._assert_meowuri_str(
            'extractor.filesystem.xplat.extension',
            uu.as_meowuri('extractor.filesystem'), 'xplat', 'extension'
        )
        self._assert_meowuri_str(
            'extractor.filesystem.xplat.abspath_full',
            uu.as_meowuri('extractor.filesystem'), 'xplat', 'abspath_full'
        )


class TestDifferentNumberOfStringArgs(TestCase):
    def test_valid_meowuri_a(self):
        def _check(*args):
            actual = MeowURI(*args)
            self.assertEqual('generic.metadata.author', str(actual))
            actual_two = MeowURI(args)
            self.assertEqual(str(actual_two), 'generic.metadata.author')

        _check('generic.metadata.author')
        _check('generic.metadata', 'author')
        _check('generic', 'metadata.author')
        _check('generic', 'metadata', 'author')

    def test_valid_meowuri_b(self):
        def _check(*args):
            actual = MeowURI(*args)
            self.assertEqual(
                str(actual), 'extractor.filesystem.xplat.basename_suffix'
            )

        _check('extractor.filesystem.xplat.basename_suffix')
        _check('extractor.filesystem.xplat', 'basename_suffix')
        _check('extractor.filesystem', 'xplat', 'basename_suffix')
        _check('extractor', 'filesystem', 'xplat', 'basename_suffix')
        _check('extractor', 'filesystem.xplat.basename_suffix')
        _check('extractor', 'filesystem', 'xplat.basename_suffix')
        _check('extractor', 'filesystem', 'xplat', 'basename_suffix')

    def test_valid_meowuri_c(self):
        def _check(*args):
            actual = MeowURI(*args)
            self.assertEqual(
                str(actual), 'extractor.metadata.exiftool.File:MIMEType'
            )

        _check('extractor.metadata.exiftool.File:MIMEType')
        _check('extractor.metadata.exiftool', 'File:MIMEType')
        _check('extractor.metadata', 'exiftool', 'File:MIMEType')
        _check('extractor', 'metadata', 'exiftool', 'File:MIMEType')
        _check('extractor', 'metadata', 'exiftool.File:MIMEType')
        _check('extractor', 'metadata.exiftool.File:MIMEType')
        _check('extractor', 'metadata', 'exiftool.File:MIMEType')


class TestMeowURIParser(TestCase):
    def setUp(self):
        self.p = MeowURIParser()

    def test_parse_none_raises_exception(self):
        with self.assertRaises(InvalidMeowURIError):
            self.p.parse(None)

    def test_partitions_parts(self):
        a = self.p.parse(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        self.assertIsInstance(a[0], MeowURIRoot)
        self.assertIsInstance(a[1], list)
        self.assertIsInstance(a[1][0], MeowURIChild)
        self.assertIsInstance(a[2], MeowURILeaf)

        b = self.p.parse('extractor.metadata.exiftool.File:MIMEType')
        self.assertIsInstance(b[0], MeowURIRoot)
        self.assertIsInstance(b[1], list)
        self.assertIsInstance(b[1][0], MeowURIChild)
        self.assertIsInstance(b[1][1], MeowURIChild)
        self.assertIsInstance(b[2], MeowURILeaf)

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

    def test_partitions_two_lists_of_parts(self):
        a = self.p.parse(['extractor.filesystem.xplat', 'basename_full'])
        self.assertIsInstance(a[0], MeowURIRoot)
        self.assertIsInstance(a[1], list)
        self.assertIsInstance(a[1][0], MeowURIChild)
        self.assertIsInstance(a[1][1], MeowURIChild)
        self.assertIsInstance(a[2], MeowURILeaf)

        b = self.p.parse('extractor.metadata.exiftool.File:MIMEType')
        self.assertIsInstance(b[0], MeowURIRoot)
        self.assertIsInstance(b[1], list)
        self.assertIsInstance(b[1][0], MeowURIChild)
        self.assertIsInstance(b[1][1], MeowURIChild)
        self.assertIsInstance(b[2], MeowURILeaf)

    def test_returns_two_lists_of_partitioned_parts_as_strings(self):
        a = self.p.parse(['extractor.filesystem.xplat', 'basename_full'])
        self.assertEqual(str(a[0]), 'extractor')
        self.assertEqual(str(a[1][0]), 'filesystem')
        self.assertEqual(str(a[1][1]), 'xplat')
        self.assertEqual(str(a[2]), 'basename_full')

        b = self.p.parse('extractor.metadata.exiftool.File:MIMEType')
        self.assertEqual(str(b[0]), 'extractor')
        self.assertEqual(str(b[1][0]), 'metadata')
        self.assertEqual(str(b[1][1]), 'exiftool')
        self.assertEqual(str(b[2]), 'File:MIMEType')


class TestMeowURINode(TestCase):
    def test_instantiated_class_is_not_none(self):
        node = MeowURINode(None)
        self.assertIsNotNone(node)

    def test_new_instance_has_expected_name(self):
        node = MeowURINode('foo')
        self.assertEqual('foo', node.name)

    def test_make_absolute_traverses_all_parents(self):
        a = MeowURINode('A')
        b = MeowURINode('B', parent=a)
        c = MeowURINode('C', parent=b)
        absolute_c = c.make_absolute()
        self.assertEqual('A.B.C', absolute_c)


class TestRoundtripsFromStringToMeowURIToString(TestCase):
    def _assert_roundtrips(self, given):
        actual = MeowURI(given)
        self.assertEqual(given, str(actual))

    def test_epub_metadata_extractor_prefix(self):
        self._assert_roundtrips('extractor.metadata.epub')

    def test_exiftool_metadata_extractor_prefix(self):
        self._assert_roundtrips('extractor.metadata.exiftool')

    def test_jpeginfo_metadata_extractor_prefix(self):
        self._assert_roundtrips('extractor.metadata.jpeginfo')

    def test_epub_text_extractor_prefix(self):
        self._assert_roundtrips('extractor.text.epub')

    def test_pdf_text_extractor_prefix(self):
        self._assert_roundtrips('extractor.text.pdf')


class TestRoundtripsFromMeowURIToStringToMeowURI(TestCase):
    def _assert_roundtrips(self, given):
        _given_meowuri = uu.as_meowuri(given)
        assert isinstance(_given_meowuri, MeowURI), 'Failed test sanity check'

        _given_meowuri_as_string = str(_given_meowuri)
        _actual = MeowURI(_given_meowuri_as_string)
        self.assertEqual(_given_meowuri, _actual)
        self.assertEqual(str(_given_meowuri), str(_actual))

    def test_epub_metadata_extractor_prefix(self):
        self._assert_roundtrips('extractor.metadata.epub')

    def test_exiftool_metadata_extractor_prefix(self):
        self._assert_roundtrips('extractor.metadata.exiftool')

    def test_jpeginfo_metadata_extractor_prefix(self):
        self._assert_roundtrips('extractor.metadata.jpeginfo')

    def test_epub_text_extractor_prefix(self):
        self._assert_roundtrips('extractor.text.epub')

    def test_pdf_text_extractor_prefix(self):
        self._assert_roundtrips('extractor.text.pdf')


class TestForceMeowURI(TestCase):
    def _assert_valid(self, *given):
        actual = force_meowuri(given)
        self.assertIsInstance(actual, MeowURI)

    def _assert_invalid(self, *given):
        actual = force_meowuri(given)
        self.assertIsNone(actual)

    def test_returns_meowuri_given_valid_string(self):
        self._assert_valid(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)

    def test_returns_meowuri_given_valid_string_and_meowuri(self):
        self._assert_valid(uu.as_meowuri('extractor.metadata.exiftool'), 'author')

    def test_returns_meowuri_given_meowuri(self):
        self._assert_valid(uu.as_meowuri('extractor.metadata.exiftool.author'))

    def test_returns_none_given_none(self):
        self._assert_invalid(None)
        self._assert_invalid(None, None)

    def test_returns_none_given_invalid_string(self):
        self._assert_invalid('')
        self._assert_invalid('', '')
        self._assert_invalid('foo', 'bar')
        self._assert_invalid('foo', '')

    def test_returns_none_given_non_string_arguments(self):
        self._assert_invalid(1)
        self._assert_invalid(1, 2)
        self._assert_invalid(object())
        self._assert_invalid(object(), object())
        self._assert_invalid({'a': 1})
        self._assert_invalid({}, {'a': 1})
        self._assert_invalid({'a': 1}, {'b': 2})


class TestHandlesDumpedMeowURIs(TestCase):
    def test_handles_dumped_meowuris(self):
        # self.assertTrue(False)
        for dumped_meowuri_str in uuconst.DUMPED_MEOWURIS:
            with self.subTest(given_string=dumped_meowuri_str):
                actual = MeowURI(dumped_meowuri_str)
                self.assertIsInstance(actual, MeowURI)
                self.assertEqual(dumped_meowuri_str, str(actual))
