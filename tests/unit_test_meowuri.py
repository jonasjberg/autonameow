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

from core.meowuri import (
    MeowURI,
    MeowURIRoot,
    MeowURILeaf,
    MeowURINode
)


class TestMeowURI(TestCase):
    def test_partitions_parts(self):
        self.skipTest('TODO: Implement or remove ..')

        a = MeowURI('generic.contents.mimetype')
        self.assertTrue(isinstance(a.root, MeowURIRoot))
        self.assertTrue(isinstance(a.mids, list))
        self.assertTrue(isinstance(a.mids[0], MeowURINode))
        self.assertTrue(isinstance(a.leaf, MeowURILeaf))

        self.assertEqual(a.root.name, 'generic')
        self.assertEqual(a.mids[0].name, 'contents')
        self.assertEqual(a.leaf.name, 'mimetype')

        b = MeowURI('contents.mimetype')
        self.assertTrue(isinstance(b.root, MeowURIRoot))
        self.assertTrue(isinstance(b.leaf, MeowURILeaf))

    def test___getattr__(self):
        self.skipTest('TODO: Implement or remove ..')

        a = MeowURI('filesystem.abspath.full')
        self.assertEqual(a.filesystem, 'abspath')
        self.assertEqual(a.filesystem.abspath, 'full')

    def _is_node(self, thing):
        pass

    def _is_root(self, thing):
        pass

    def _is_leaf(self, thing):
        pass

    def test_TODO(self):
        self.skipTest('TODO: Implement or remove ..')

        a = MeowURI('analysis.filetags.datetime')
        self._is_root(a['analysis'])
        self._is_node(a['analysis']['filetags'])
        self._is_leaf(a['analysis']['filetags']['datetime'])

        b = MeowURI('filesystem.basename.extension')
        self._is_root(b['filesystem'])
        self._is_node(b['filesystem']['basename'])
        self._is_leaf(b['filesystem']['basename']['extension'])

        c = MeowURI('filesystem.contents.mime_type')
        self._is_root(c['filesystem'])
        self._is_node(c['filesystem']['contents'])
        self._is_leaf(c['filesystem']['contents']['mime_type'])

        d = MeowURI('metadata.exiftool.EXIF:DateTimeOriginal')

        # metadata.exiftool.PDF:CreateDate
        # metadata.exiftool.QuickTime:CreationDate
        # metadata.exiftool.XMP - dc:Creator
        # metadata.exiftool.XMP - dc:CreatorFile -as
        # metadata.exiftool.XMP - dc:Date
        # metadata.exiftool.XMP - dc:PublicationDate
        # metadata.exiftool.XMP - dc:Publisher
        # metadata.exiftool.XMP - dc:Title
        # plugin.guessit.date
        # plugin.guessit.title
        # plugin.microsoft_vision.caption

