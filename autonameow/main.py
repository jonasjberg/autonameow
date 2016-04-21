#!/usr/bin/env python
# coding=utf-8

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import argparse
import logging

import util.disk
from analyze.analysis import Analysis
from analyze.common import AnalyzerBase
from analyze.image import ImageAnalyzer
from analyze.pdf import PdfAnalyzer
from file_object import FileObject


def handle_logging():
    # def setup_custom_logger(name):
    #     if args.debug:
    #         format = "%(asctime)s %(levelname)-6s %(funcName)s(%(lineno)d) -- %(message)s"
    #         dateformat = '%Y-%m-%d %H:%M:%S'
    #         level = logging.DEBUG
    #     elif args.verbose:
    #         format = "%(asctime)s %(levelname)-6s -- %(message)s"
    #         dateformat = '%Y-%m-%d %H:%M:%S'
    #         level = logging.INFO
    #     elif args.quiet:
    #         format = "%(levelname)s -- %(message)s"
    #         dateformat = None
    #         level = logging.CRITICAL
    #     else:
    #         format = "%(levelname)s -- %(message)s"
    #         dateformat = None
    #         level = logging.WARNING
    #
    #     formatter = logging.Formatter(fmt=format, datefmt=dateformat)
    #
    #     handler = logging.StreamHandler()
    #     handler.setFormatter(formatter)
    #
    #     logger = logging.getLogger(name)
    #     logger.setLevel(logging.DEBUG)
    #     logger.addHandler(handler)
    #     return logger
    #
    # logger = setup_custom_logger('root')
    # logger.debug('main message')

    if args.debug:
        FORMAT = "%(asctime)s %(levelname)-6s %(funcName)s(%(lineno)d) -- %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif args.verbose:
        FORMAT = "%(asctime)s %(levelname)-6s -- %(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT,
                            datefmt='%Y-%m-%d %H:%M:%S')
    elif args.quiet:
        FORMAT = "%(levelname)s -- %(message)s"
        logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
    else:
        FORMAT = "%(levelname)s -- %(message)s"
        logging.basicConfig(level=logging.WARNING, format=FORMAT)


def main():
    # Main program entry point
    handle_logging()

    # Iterate over command line arguments ..
    if args.input_files:
        for arg in args.input_files:
            if util.disk.is_readable_file(arg):
                logging.info('Processing file \"%s\"' % str(arg))

                # Create a new FileObject representing the current arg.
                f = FileObject(arg)

                # Begin analysing the file.
                analysis = Analysis(f)
                analysis.run()

                if args.add_datetime:
                    if analysis.get_datetime() is not None:
                        logging.info('Found datetime information:')

                        print(str(analysis.get_datetime()))
                        # for k, v in analysis.get_datetime():
                        #     logging.info('%20.20s : %-60.60s' % str(k), str(v))

                # TODO: Implement below dummy code or something similar to it.
                # if analyzer.hasResults():
                #     results = analyzer.getResults()
                #     file.assembleNewName(results)


            else:
                # Unable to read file. Skip ..
                logging.error('Unable to read file \"%s\"' % str(file))
                continue

    else:
        logging.info("No input files specified. Exiting.")
        exit(1)


def create_cli_argument_parser():
    parser = argparse.ArgumentParser(
        description='Automatic renaming of files from analysis of several sources of information.')

    output_control_group = parser.add_mutually_exclusive_group()
    output_control_group.add_argument("-z", "--debug",
                                      dest='debug',
                                      action="store_true",
                                      help='debug mode')

    output_control_group.add_argument("-v", "--verbose",
                                      dest='verbose',
                                      action="store_true",
                                      help='verbose mode')

    output_control_group.add_argument("-q", "--quiet",
                                      dest='quiet',
                                      action="store_true",
                                      help='quiet mode')

    action_control_group = parser.add_mutually_exclusive_group()
    action_control_group.add_argument("--add-datetime",
                                      dest='add_datetime',
                                      action="store_true",
                                      help='add datetime only')

    parser.add_argument(dest='input_files',
                        metavar='filename',
                        nargs='*',
                        help='input file(s)')

    parser.add_argument('-d', '--dry-run',
                        dest='dry_run',
                        action='store',
                        help='simulate what would happen but do not actually write any changes to disk')

    return parser


parser = create_cli_argument_parser()
args = parser.parse_args()

if __name__ == '__main__':
    main()
