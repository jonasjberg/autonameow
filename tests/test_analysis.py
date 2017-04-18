# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016-2017, Jonas Sjoberg.

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
