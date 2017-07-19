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


# TODO: [TD0003] Fix this! Used for instantiating analyzers so that they are
# included in the global namespace and seen by 'get_analyzer_classes()'.
from analyzers.analyzer import Analyzer
from analyzers.analyze_filename import FilenameAnalyzer
from analyzers.analyze_filesystem import FilesystemAnalyzer
from analyzers.analyze_image import ImageAnalyzer
from analyzers.analyze_pdf import PdfAnalyzer
from analyzers.analyze_video import VideoAnalyzer
__dummy_a = Analyzer(None, None, None)
__dummy_b = FilenameAnalyzer(None, None, None)
__dummy_c = FilesystemAnalyzer(None, None, None)
__dummy_d = ImageAnalyzer(None, None, None)
__dummy_e = PdfAnalyzer(None, None, None)
__dummy_f = VideoAnalyzer(None, None, None)


def suitable_analyzers_for(file_object):
    """
    Returns analyzer classes that can handle the given file object.

    Args:
        file_object: File to get analyzers for as an instance of 'FileObject'.

    Returns:
        A list of analyzer classes that can analyze the given file.
    """
    return [a for a in AnalyzerClasses if a.can_handle(file_object)]


def get_analyzer_classes():
    """
    Get a list of all available analyzers as a list of "type".
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        All available analyzer classes as a list of type.
    """
    return [klass for klass in globals()['Analyzer'].__subclasses__()]


def get_analyzer_classes_basename():
    """
    Get a list of class base names for all available analyzers.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        The base names of available analyzer classes as a list of strings.
    """
    return [c.__name__ for c in get_analyzer_classes()]


AnalyzerClasses = get_analyzer_classes()
