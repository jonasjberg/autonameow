#!/usr/bin/env python3
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

import argparse
import logging
import sys

from core import constants as C
from core import (
    exceptions,
    extraction,
    logs,
    types,
    ui
)
from core.fileobject import FileObject
from extractors import ExtractorError
from util import encoding as enc
from util import disk


log = logging.getLogger(__name__)


# TODO: [TD0159] Fix stand-alone extractor not respecting the `--quiet` option.


def do_extract_text(fileobject):
    klasses = extraction.suitable_extractors_for(fileobject)
    if not klasses:
        log.debug('No extractors suitable for "{!s}"'.format(fileobject))
        return

    log.debug('Got {} extractors for "{!s}"'.format(len(klasses), fileobject))
    for k in klasses:
        log.debug(str(k))

    text_extractors = [
        k for k in klasses
        if k.meowuri_prefix().startswith('extractor.text')
    ]
    if not text_extractors:
        log.warning(
            'No text extractors are suited for "{!s}"'.format(fileobject)
        )
        return

    log.debug('Got {} text extractors for "{!s}"'.format(len(text_extractors),
                                                         fileobject))
    for te in text_extractors:
        log.debug(str(te))

    for te in text_extractors:
        _extractor_instance = te()
        try:
            _text = _extractor_instance.extract(fileobject)
        except ExtractorError as e:
            log.error(
                'Halted extractor "{!s}": {!s}'.format(_extractor_instance, e)
            )
            continue

        assert isinstance(_text, dict)
        _full_text = _text.get('full')
        if not _full_text:
            log.error('Unable to extract text from "{!s}"'.format(fileobject))
            return

        assert isinstance(_full_text, str)
        # TODO: Factor out method of presenting the extracted text.
        ui.msg('Text Extracted by {!s}:'.format(_extractor_instance),
               style='section')
        ui.msg(_full_text)


def do_extract_metadata(fileobject):
    klasses = extraction.suitable_extractors_for(fileobject)
    if not klasses:
        log.debug('No extractors suitable for "{!s}"'.format(fileobject))
        return

    log.debug('Got {} extractors for "{!s}"'.format(len(klasses), fileobject))
    for k in klasses:
        log.debug(str(k))

    metadata_extractors = [
        k for k in klasses
        if k.meowuri_prefix().startswith('extractor.metadata')
    ]
    if not metadata_extractors:
        log.warning(
            'No metadata extractors are suited for "{!s}"'.format(fileobject)
        )
        return

    log.debug('Got {} metadata extractors for "{!s}"'.format(
        len(metadata_extractors), fileobject
    ))
    for me in metadata_extractors:
        log.debug(str(me))

    for me in metadata_extractors:
        _extractor_instance = me()
        try:
            _metadata = _extractor_instance.extract(fileobject)
        except ExtractorError as e:
            log.error('Halted extractor "{!s}": {!s}'.format(
                _extractor_instance, e
            ))
            continue

        try:
            _metainfo = _extractor_instance.metainfo()
        except ExtractorError as e:
            log.error('Halted extractor "{!s}": {!s}'.format(
                _extractor_instance, e
            ))
            continue

        assert isinstance(_metadata, dict)
        assert isinstance(_metainfo, dict)

        ui.msg('Metadata Extracted by {!s}'.format(_extractor_instance),
               style='section')
        cf = ui.ColumnFormatter()
        for k, v in sorted(_metadata.items()):
            cf.addrow(str(k), str(v))
        cf.addemptyrow()
        ui.msg(cf)


def main(options=None):
    if options is None:
        options = dict()

    # Default options are defined here.
    # Passed in 'options' always take precedence and overrides the defaults.
    opts = {
        'debug': False,
        'verbose': False,
        'quiet': False,

        'extract_text': False,
        'extract_metadata': False,

        'input_paths': [],
    }
    opts.update(options)

    logs.init_logging(options)

    if not opts.get('input_paths'):
        log.warning(
            'No input path(s) specified.  Use "--help" for usage information.'
        )
        sys.exit(C.EXIT_SUCCESS)

    _extract_any = opts.get('extract_text') or opts.get('extract_metadata')
    if not _extract_any:
        log.warning(
            'Not sure what to extract.  Use "--help" for usage information.'
        )
        sys.exit(C.EXIT_SUCCESS)

    # Path name encoding boundary. Returns list of paths in internal format.
    files_to_process = disk.normpaths_from_opts(
        opts.get('input_paths'),
        C.DEFAULT_FILESYSTEM_IGNORE,
        recurse=False
    )

    _num_files = len(files_to_process)
    log.info('Got {} files to process'.format(_num_files))

    for _num, _file in enumerate(files_to_process, start=1):
        # Sanity checking the "file_path" is part of 'FileObject' init.
        try:
            current_file = FileObject(_file)
        except (exceptions.InvalidFileArgumentError,
                exceptions.FilesystemError) as e:
            log.warning('{!s} - SKIPPING: "{!s}"'.format(
                e, enc.displayable_path(_file)))
            continue

        ui.msg('{!s}'.format(current_file), style='heading')
        log.info('Processing ({}/{}) "{!s}" ..'.format(
            _num, _num_files, current_file))

        if opts.get('extract_text'):
            do_extract_text(current_file)

        if opts.get('extract_metadata'):
            do_extract_metadata(current_file)


def parse_args(raw_args):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description='{} {} --- Stand-alone Content Extraction'.format(
            C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION
        ),
        epilog='Run autonameow extractors stand-alone.' +
        '\n Project website:  {}'.format(C.STRING_URL_REPO),
    )

    parser.add_argument(
        dest='input_paths',
        metavar='INPUT_PATH',
        nargs='*',
        help='Path(s) to file(s) of files to process. '
    )

    optgrp_extract = parser.add_argument_group('extraction options')
    optgrp_extract.add_argument(
        '--text',
        dest='extract_text',
        action='store_true',
        help='Extract unstructured textual contents from the given file(s).'
    )
    optgrp_extract.add_argument(
        '--metadata',
        dest='extract_metadata',
        action='store_true',
        help='Extract metadata from the given file(s).'
    )

    optgrp_output = parser.add_mutually_exclusive_group()
    optgrp_output.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        default=False,
        help='Enables debug mode, prints detailed debug information.'
    )
    optgrp_output.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Enables verbose mode, prints additional information.'
    )
    optgrp_output.add_argument(
        '-q', '--quiet',
        dest='quiet',
        action='store_true',
        default=False,
        help='Enables quiet mode, suppress all but renames.'
    )

    return parser.parse_args(raw_args)


def cli_main(argv=None):
    """
    Main program entry point when running as a command-line application.

    Args:
        argv: Raw command-line arguments as a list of strings.
    """
    args = argv
    if not args:
        print('Add "--help" to display usage information.')
        sys.exit(C.EXIT_SUCCESS)

    # Handle the command line arguments with argparse.
    opts = parse_args(args)

    # Translate from 'argparse'-specific format to internal options dict.
    options = {
        'debug': opts.debug,
        'verbose': opts.verbose,
        'quiet': opts.quiet,

        'extract_text': opts.extract_text,
        'extract_metadata': opts.extract_metadata,

        'input_paths': opts.input_paths,
    }

    try:
        main(options)
    except KeyboardInterrupt:
        sys.exit('\nReceived keyboard interrupt; Exiting ..')


if __name__ == '__main__':
    cli_main(sys.argv[1:])
