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

from core.analyze.analysis import (
    get_analyzer_mime_mappings,
    get_analyzer_classes,
    get_instantiated_analyzers
)

from core.analyze.analyze_pdf import PdfAnalyzer
from core.analyze.analyze_image import ImageAnalyzer
from core.analyze.analyze_text import TextAnalyzer
from core.analyze.analyze_video import VideoAnalyzer
from core.analyze.analyze_filename import FilenameAnalyzer
from core.analyze.analyze_filesystem import FilesystemAnalyzer


class TestAnalysis(TestCase):
    def test_get_analysis_mime_mappings(self):
        ANALYZER_TYPE_LOOKUP = {ImageAnalyzer: ['jpg', 'png'],
                                PdfAnalyzer: 'pdf',
                                TextAnalyzer: ['txt', 'md'],
                                VideoAnalyzer: 'mp4',
                                FilesystemAnalyzer: None,
                                FilenameAnalyzer: None}
        self.assertEqual(ANALYZER_TYPE_LOOKUP, get_analyzer_mime_mappings())

    def test_get_analyzer_classes(self):
        ANALYZER_CLASSES = [ImageAnalyzer, FilesystemAnalyzer, FilenameAnalyzer,
                            VideoAnalyzer, PdfAnalyzer, TextAnalyzer]

        self.assertCountEqual(ANALYZER_CLASSES, get_analyzer_classes())

    def test_get_instantiated_analyzers(self):
        self.skipTest('Fix/skip this test ..')
    #     INSTANTIATED_ANALYZERS = [ImageAnalyzer(None), PdfAnalyzer(None),
    #                               TextAnalyzer(None), VideoAnalyzer(None),
    #                               FilesystemAnalyzer(None),
    #                               FilenameAnalyzer(None)]
    #     self.assertEqual(INSTANTIATED_ANALYZERS, get_instantiated_analyzers())
