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

import logging as log

from PIL import Image
import pytesseract

from core import util
from core.exceptions import ExtractorError
from extractors.textual import AbstractTextExtractor


class ImageOCRTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['image/*']
    data_query_string = 'contents.visual.ocr_text'
    is_slow = True

    def __init__(self, source):
        super(ImageOCRTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        # NOTE: Tesseract behaviour will likely need tweaking depending
        #       on the image contents. Will need to pass "tesseract_args"
        #       somehow. I'm starting to think image OCR does not belong
        #       in this inheritance hierarchy ..
        log.debug('Running image OCR with PyTesseract ..')
        result = get_text_from_ocr(self.source, tesseract_args=None)
        return result


def get_text_from_ocr(image_path, tesseract_args=None):
    """
    Get any textual content from the image by running OCR with tesseract
    through the pytesseract wrapper.

    Args:
        image_path: The path to the image to process.
        tesseract_args: Optional tesseract arguments as Unicode strings.

    Returns:
        Any OCR results text or empty as Unicode strings.

    Raises:
        ExtractorError: The extraction failed.
    """
    # TODO: Test this!

    try:
        image = Image.open(image_path)
    except IOError as e:
        raise ExtractorError(e)

    log.debug('Calling tesseract; ARGS: "{!s}" FILE: "{!s}"'.format(
        tesseract_args, util.displayable_path(image_path)
    ))
    try:
        # TODO: [TD0068] Let the user configure which languages to use with OCR.
        text = pytesseract.image_to_string(image, lang='swe+eng',
                                           config=tesseract_args)
    except pytesseract.pytesseract.TesseractError as e:
        raise ExtractorError('PyTesseract ERROR: {}'.format(str(e)))
    else:
        if text:
            text = text.strip()
            log.debug('PyTesseract returned {} bytes of text'.format(len(text)))
            return util.decode_(text)
        return ''
