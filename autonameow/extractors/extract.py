#!/usr/bin/env python3
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

import argparse
import logging
import sys


from core import constants as C


log = logging.getLogger(__name__)


def main(options=None):
    if options is None:
        options = {}

    # Default options are defined here.
    # Passed in 'options' always take precedence and overrides the defaults.
    opts = {
        'debug': False,
        'verbose': False,
        'quiet': False,

        'show_version': False,

        'extract_text': False,
        'extract_metadata': False,

        'input_paths': [],
    }
    opts.update(options)

    if not opts.get('input_paths'):
        log.info(
            'No input path(s) specified. Use "--help" for usage information.'
        )
        sys.exit(0)

    _extract_any = opts.get('extract_text') or opts.get('extract_metadata')
    if not _extract_any:
        log.info(
            'Nothing to do! Use "--help" for usage information.'
        )
        sys.exit(0)

    pass


def parse_args(raw_args):
    parser = argparse.ArgumentParser(
        prog=__file__,
        description='{} {} --- Stand-alone Content Extraction'.format(
            C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION
        ),
        epilog='Run autonameow extractors stand-alone.' +
               '\n Project website:  {}'.format(C.STRING_REPO_URL),
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

        'show_version': opts.show_version,

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
