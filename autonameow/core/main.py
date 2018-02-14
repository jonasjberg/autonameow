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

import sys
import traceback

from core import constants as C
from core import logs
from core.view import cli
from core.autonameow import Autonameow
from core.exceptions import AWAssertionError


# Default options passed to the main 'Autonameow' class instance.
DEFAULT_OPTIONS = {
    'debug': False,
    'verbose': False,
    'quiet': False,

    'show_version': False,
    'dump_config': False,
    'dump_options': False,
    'dump_meowuris': False,

    'list_all': False,
    'list_rulematch': False,

    'mode_automagic': False,
    'mode_batch': False,
    'mode_interactive': True,
    'mode_rulematch': True,
    'mode_timid': False,

    'config_path': None,

    'dry_run': True,
    'recurse_paths': False,

    'input_paths': [],
}


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
        options = dict()

    # Passed in 'options' always take precedence and overrides the defaults.
    opts = dict(DEFAULT_OPTIONS)
    opts.update(options)

    # Initialize global logging.
    logs.init_logging(opts)
    if opts.get('quiet'):
        logs.silence()

    # Main program entry point.
    with Autonameow(opts, ui=cli) as ameow:
        ameow.run()


def print_error(message):
    print(message, file=sys.stderr, flush=True)


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
        cli.msg('Add "--help" to display usage information.')
        sys.exit(C.EXIT_SUCCESS)

    # Handle the command line arguments with argparse.
    opts = cli.options.cli_parse_args(args)

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
        'list_rulematch': opts.list_rulematch,

        'mode_automagic': opts.mode_automagic,
        'mode_batch': opts.mode_batch,
        'mode_interactive': opts.mode_interactive,
        'mode_rulematch': opts.mode_rulematch,
        'mode_timid': opts.mode_timid,

        'config_path': opts.config_path,

        'dry_run': opts.dry_run,
        'recurse_paths': opts.recurse_paths,

        'input_paths': opts.input_paths,
    }

    try:
        real_main(options)
    except KeyboardInterrupt:
        sys.exit('\nReceived keyboard interrupt; Exiting ..')
    except (AssertionError, AWAssertionError) as e:
        _error_msg = format_sanitycheck_error(str(e))
        print_error(_error_msg)
        sys.exit(C.EXIT_SANITYFAIL)
