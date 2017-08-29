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

from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

from core import (
    exceptions,
    util
)
from extractors.text import AbstractTextExtractor


class ImageOCRTextExtractor(AbstractTextExtractor):
    handles_mime_types = ['image/*']
    meowuri_root = 'contents.visual.ocr_text'
    is_slow = True

    def __init__(self, source):
        super(ImageOCRTextExtractor, self).__init__(source)

    def _get_raw_text(self):
        # NOTE: Tesseract behaviour will likely need tweaking depending
        #       on the image contents. Will need to pass "tesseract_args"
        #       somehow. I'm starting to think image OCR does not belong
        #       in this inheritance hierarchy ..
        tesseract_args = None

        self.log.debug('Calling tesseract; ARGS: "{!s}" FILE: "{!s}"'.format(
            tesseract_args, util.displayable_path(self.source)
        ))
        result = get_text_from_ocr(self.source, tesseract_args=tesseract_args)

        self.log.debug('PyTesseract returned {} (?) of text'.format(len(result)))
        return result

    @classmethod
    def check_dependencies(cls):
        return pytesseract is not None and util.is_executable('tesseract')


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
        raise exceptions.ExtractorError(e)

    # NOTE: Catching TypeError to work around bug in 'pytesseract';
    #
    # def get_errors(error_string):
    #     lines = error_string.splitlines()
    #     lines = [util.decode_(line) for line in lines]
    #     error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    #                                                             ^^^^^^^
    #                         This is fails when environment is set up so
    #                    that tesseract output is bytes or non-Unicode ..
    try:
        # TODO: [TD0068] Let the user configure which languages to use with OCR.
        text = pytesseract.image_to_string(image, lang='swe+eng',
                                           config=tesseract_args)
    except (pytesseract.pytesseract.TesseractError, TypeError) as e:
        raise exceptions.ExtractorError(
            'PyTesseract ERROR: {}'.format(str(e))
        )
    else:
        if text:
            text = text.strip()
            return util.decode_(text)
        return ''
