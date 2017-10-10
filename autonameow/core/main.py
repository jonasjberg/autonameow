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

import sys
import traceback

from core import constants
from core.autonameow import Autonameow
from core.exceptions import AWAssertionError
from core.options import parse_args


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
    # "Raw" option arguments as a list of strings.
    args = argv
    if not args:
        print('Add "--help" to display usage information.')
        sys.exit(constants.EXIT_SUCCESS)

    # Handle the command line arguments and setup logging.
    # Returns parsed options returned by argparse.
    opts = parse_args(args)

    # Populate dict to pass to the Autonameow instance.
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

    with Autonameow(options) as ameow:
        try:
            ameow.run()
        except KeyboardInterrupt:
            sys.exit('\nReceived keyboard interrupt; Exiting ..')
        except AWAssertionError as e:
            _error_msg = format_sanitycheck_error(str(e))
            print_error(_error_msg)
            sys.exit(3)

