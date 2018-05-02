# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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


#   NOTE:  Some of this code is based on 'pytesseract' by Matthias Lee.
#          https://github.com/madmaze/python-tesseract

import os
import shlex
import subprocess
import tempfile

try:
    from PIL import Image
except ImportError:
    Image = None

import util
from extractors import ExtractorError
from extractors.text.common import AbstractTextExtractor
from extractors.text.common import decode_raw
from util import encoding as enc


TESSERACT_COMMAND = 'tesseract'
TESSERACT_ARGS = None


class TesseractOCRTextExtractor(AbstractTextExtractor):
    # NOTE(jonas): Can't do 'image/*' because it includes 'image/vnd.djvu' ..
    HANDLES_MIME_TYPES = ['image/bmp', 'image/gif', 'image/jpeg', 'image/png']
    IS_SLOW = True

    def __init__(self):
        super().__init__()

        self.init_cache()

    def extract_text(self, fileobject):
        # NOTE: Tesseract behaviour will likely need tweaking depending
        #       on the image contents. Will need to pass "tesseract_args"
        #       somehow. I'm starting to think image OCR does not belong
        #       in this inheritance hierarchy ..
        return get_text_from_ocr(
            fileobject.abspath,
            tesseract_args=TESSERACT_ARGS
        )

    @classmethod
    def dependencies_satisfied(cls):
        # Requires tesseract and PIL.Image.
        return util.is_executable(TESSERACT_COMMAND) and Image is not None


def pil_read_image(filepath):
    """
    Loads an image at the given path with PIL.

    Args:
        filepath: Path of the image to load, as a Unicode string.

    Returns:
        An instance of the 'PIL.Image.Image' class.

    Raises:
        ExtractorError: The image could not be loaded, for any reason.
    """
    try:
        return Image.open(filepath)
    except (AttributeError, OSError, ValueError) as e:
        raise ExtractorError('Unable to load image; {!s}'.format(e))


def get_text_from_ocr(filepath, tesseract_args=None):
    """
    Get any textual content from the image by running OCR with tesseract.

    Args:
        filepath: The path to the image to process.
        tesseract_args: Optional tesseract arguments as Unicode strings.

    Returns:
        Any OCR results text or empty as Unicode strings.

    Raises:
        ExtractorError: The extraction failed.
    """
    # TODO: Test this!

    image = pil_read_image(filepath)

    # NOTE: Catching TypeError to work around bug in 'pytesseract';
    #
    # def get_errors(error_string):
    #     lines = error_string.splitlines()
    #     lines = [enc.decode_(line) for line in lines]
    #     error_lines = tuple(line for line in lines if line.find('Error') >= 0)

    try:
        # TODO: [TD0068] Let the user configure which languages to use with OCR.
        stdout = image_to_string(image, lang='swe+eng',
                                 config=tesseract_args)
    except (ExtractorError, TypeError) as e:
        # TODO: Cleanup exception handling.
        raise ExtractorError('tesseract ERROR: {}'.format(str(e)))
    else:
        result = decode_raw(stdout)
        if not result:
            return ''
        return result


def run_tesseract(input_filename, output_filename_base,
                  lang=None, boxes=False, config=None):
    """
    Runs the command:
        'tesseract_cmd' 'input_filename' 'output_filename_base'

    Returns the exit status and stderr output of tesseract.
    """
    command = [TESSERACT_COMMAND, input_filename, output_filename_base]

    if lang is not None:
        command += ['-l', lang]
    if boxes:
        command += ['batch.nochop', 'makebox']
    if config:
        command += shlex.split(config)

    try:
        process = subprocess.Popen(command, stderr=subprocess.PIPE)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise ExtractorError(e)
    else:
        return process.wait(), process.stderr.read()


def cleanup_temporary_file(filename):
    """
    Deletes the given filename.  Any errors are silently ignored.
    """
    try:
        os.remove(filename)
    except OSError:
        pass


def get_errors(error_string):
    """
    Returns all lines in the error_string that start with the string "error".
    """
    lines = error_string.splitlines()
    lines = [enc.decode_(line) for line in lines]
    error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    if error_lines:
        return '\n'.join(error_lines)
    return error_string.strip()


def new_temporary_file(prefix=None, suffix=None):
    """
    Returns the absolute path to a named temporary file, as a Unicode string.
    """
    return os.path.realpath(
        tempfile.NamedTemporaryFile(delete=False,
                                    prefix=prefix,
                                    suffix=suffix).name
    )


def image_to_string(image, lang=None, boxes=False, config=None):
    """
    Runs tesseract on the specified image.

    The image is first written to disk, then tesseract is executed with this
    image. The result is read and the temporary files are deleted.

    if boxes=True
        "batch.nochop makebox" gets added to the tesseract call

    if config is set, the config gets appended to the command.
        Example; config="-psm 6"
    """
    try:
        # This could fail if the image is truncated.
        _number_image_channels = len(image.split())
    except OSError as e:
        raise ExtractorError(e)
    else:
        if _number_image_channels == 4:
            # Discard the Alpha.
            r, g, b, _ = image.split()
            image = Image.merge('RGB', (r, g, b))

    input_file_name = new_temporary_file(suffix='.bmp')

    output_file_name_base = new_temporary_file()
    if not boxes:
        output_file_name = '{}.txt'.format(output_file_name_base)
    else:
        output_file_name = '{}.box'.format(output_file_name_base)

    try:
        image.save(input_file_name)
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes,
                                             config=config)
        if status:
            errors = get_errors(error_string)
            raise ExtractorError(status, errors)
        f = open(output_file_name)
        try:
            return f.read().strip()
        finally:
            f.close()
    finally:
        cleanup_temporary_file(input_file_name)
        cleanup_temporary_file(output_file_name)
