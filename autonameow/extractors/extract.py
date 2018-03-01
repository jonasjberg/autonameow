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
    FileObject,
    logs,
    view
)
from util import encoding as enc
from util import disk


log = logging.getLogger(__name__)


# TODO: [TD0159] Fix stand-alone extractor not respecting the `--quiet` option.


def do_extract_text(fileobject):
    def _collect_results_callback(fileobject_, meowuri, data):
        log.debug('_collect_results_callback({!s}, {!s}, {!s})'.format(
            fileobject_, meowuri, data))

        assert isinstance(data, dict)
        text = data.get('value')
        assert isinstance(text, str)
        extractor = data.get('source', '(unknown extractor)')
        if not text:
            log.info('{!s} was unable to extract text from "{!s}"'.format(
                extractor, fileobject_))
            return

        # TODO: [TD0171] Separate logic from user interface.
        view.msg('Text Extracted by {!s}:'.format(extractor), style='section')
        view.msg(text)

    from extractors import TextProviderClasses
    assert TextProviderClasses
    runner = extraction.ExtractorRunner(
        add_results_callback=_collect_results_callback
    )
    try:
        runner.start(fileobject, request_extractors=TextProviderClasses)
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))


def do_extract_metadata(fileobject):
    results = dict()

    def _collect_results_callback(_, meowuri, data):
        _value = data.get('value')
        if not _value:
            return

        if isinstance(_value, bytes):
            _str_value = enc.displayable_path(_value)
        else:
            try:
                _str_value = str(_value)
            except (TypeError, ValueError) as e_:
                log.warning('Unable to convert value to Unicode string :: {!s} '
                            ': ({}) {!s}'.format(meowuri, type(_value), _value))
                log.warning(str(e_))
                return

        results[meowuri] = _str_value

    from extractors import MetadataProviderClasses
    assert MetadataProviderClasses
    runner = extraction.ExtractorRunner(
        add_results_callback=_collect_results_callback
    )
    try:
        runner.start(fileobject, request_extractors=MetadataProviderClasses)
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))
    else:
        # TODO: [TD0171] Separate logic from user interface.
        view.msg('Extracted Metadata', style='section')
        cf = view.ColumnFormatter()
        for k, v in sorted(results.items()):
            cf.addrow(str(k), str(v))
        cf.addemptyrow()
        view.msg(str(cf))


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

        # TODO: [TD0171] Separate logic from user interface.
        view.msg('{!s}'.format(current_file), style='heading')
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
