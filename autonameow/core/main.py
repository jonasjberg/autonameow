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

import logging
import sys
import traceback

from core import (
    constants,
    logs
)
from core.autonameow import Autonameow
from core.exceptions import AWAssertionError
from core.options import parse_args


def real_main(options=None):
    """
    Actual program entry point.

    This function is intended to be platform/interface-agnostic, in that it
    should be called by an outer interface-specific layer; like the CLI entry
    function 'cli_main'.

    The passed in options is in an internal format (dict) as to not depend on
    any means of providing program options; argument parsers, etc.

    Args:
        options: Per-instance program options, as type dict.
    """
    if options is None:
        options = {}

    # Default options are defined here.
    # Passed in 'options' always take precedence and overrides the defaults.
    opts = {
        'debug': False,
        'verbose': False,
        'quiet': False,

        'show_version': False,
        'dump_config': False,
        'dump_options': False,
        'dump_meowuris': False,

        'list_all': False,
        'list_datetime': False,
        'list_title': False,

        'mode_batch': False,
        'mode_automagic': False,
        'mode_interactive': True,

        'config_path': None,

        'dry_run': True,
        'recurse_paths': False,

        'input_paths': [],
    }
    opts.update(options)

    # Initialize global logging.
    logs.init_logging(opts)
    log = logging.getLogger(__name__)
    if opts.get('quiet'):
        logs.silence()

    # Check legality of option combinations.
    if opts.get('mode_automagic') and opts.get('mode_interactive'):
        log.warning('Operating mode must be either one of "automagic" or '
                    '"interactive", not both. Reverting to default: '
                    '[interactive mode].')
        opts['mode_automagic'] = False
        opts['mode_interactive'] = True

    if not opts.get('mode_automagic') and opts.get('mode_batch'):
        log.warning('Running in "batch" mode without "automagic" mode does'
                    'not make any sense. Nothing to do!')

    if opts.get('mode_batch') and opts.get('mode_interactive'):
        log.warning('Operating mode must be either one of "batch" or '
                    '"interactive", not both. Reverting to default: '
                    '[interactive mode].')
        opts['mode_batch'] = False
        opts['mode_interactive'] = True

    if not opts.get('mode_automagic') and not opts.get('mode_interactive'):
        log.info('Using default operating mode: [interactive mode].')
        opts['mode_interactive'] = True

    # Main program entry point.
    with Autonameow(opts) as ameow:
        ameow.run()


def print_error(message):
    print(message, file=sys.stderr)


def format_sanitycheck_error(string):
    ERROR_MSG_TEMPLATE = '''
******************************************************
            SANITY-CHECK ASSERTION FAILURE
******************************************************
Something that really should NOT happen just happened!

This is most likely a BUG that should be reported ..
.. TODO: [TD0095] Information on how to report issues.
______________________________________________________

 Running: {_program} version {_version}
Platform: {_platform}
  Python: {_python}
______________________________________________________

{message}

{traceback}
'''
    # TODO: [TD0095] Clean this up. Try to minimize imports.
    import platform
    from core import constants as C

    typ, val, tb = sys.exc_info()
    msg = ERROR_MSG_TEMPLATE.format(
        _program='autonameow',  # core.version.__title__
        _version=C.STRING_PROGRAM_VERSION,
        _platform=platform.platform(),
        _python='{!s} {!s}'.format(platform.python_implementation(),
                                   platform.python_version()),
        traceback=''.join(traceback.format_exception(typ, val, tb)),
        message=string
    )
    return msg


def cli_main(argv=None):
    """
    Main program entry point when running as a command-line application.

    Args:
        argv: Raw command-line arguments as a list of strings.
    """
    args = argv
    if not args:
        print('Add "--help" to display usage information.')
        sys.exit(constants.EXIT_SUCCESS)

    # Handle the command line arguments with argparse.
    opts = parse_args(args)

    # Translate from 'argparse'-specific format to internal options dict.
    options = {
        'debug': opts.debug,
        'verbose': opts.verbose,
        'quiet': opts.quiet,

        'show_version': opts.show_version,
        'dump_config': opts.dump_config,
        'dump_options': opts.dump_options,
        'dump_meowuris': opts.dump_meowuris,

        'list_all': opts.list_all,
        'list_datetime': opts.list_datetime,
        'list_title': opts.list_title,

        'mode_batch': opts.mode_batch,
        'mode_automagic': opts.mode_automagic,
        'mode_interactive': opts.mode_interactive,

        'config_path': opts.config_path,

        'dry_run': opts.dry_run,
        'recurse_paths': opts.recurse_paths,

        'input_paths': opts.input_paths,
    }

    try:
        real_main(options)
    except KeyboardInterrupt:
        sys.exit('\nReceived keyboard interrupt; Exiting ..')
    except AWAssertionError as e:
        _error_msg = format_sanitycheck_error(str(e))
        print_error(_error_msg)
        sys.exit(3)
