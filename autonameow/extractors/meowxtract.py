#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import shutil
import sys
from collections import defaultdict

import extractors
from core import constants as C
from core import event
from core import exceptions
from core import extraction
from core import FileObject
from core import logs
from core import view
from extractors import text_provider
from util import disk
from util import encoding as enc


log = logging.getLogger(__name__)


TERMINAL_WIDTH, _ = shutil.get_terminal_size(fallback=(120, 48))


def _get_column_formatter():
    cf = view.ColumnFormatter()
    cf.max_total_width = TERMINAL_WIDTH
    return cf


class TextExtractionResult(object):
    def __init__(self, fulltext, provider):
        self.fulltext = fulltext
        self.provider = provider

        self.fulltext_linecount = len(self.fulltext.splitlines())

    def __gt__(self, other):
        return ((self.provider, self.fulltext_linecount)
                > (other.provider, other.fulltext_linecount))

    def __repr__(self):
        return '<{}({provider} ({fulltext_linecount} lines of text))>'.format(
            self.__class__.__name__, **self.__dict__
        )


class MetadataExtractionResult(object):
    def __init__(self, metadata, provider):
        self.metadata = metadata
        self.provider = provider

        self.metadata_fieldcount = len(self.metadata)

    def __gt__(self, other):
        return ((self.provider, self.metadata_fieldcount)
                > (other.provider, other.metadata_fieldcount))

    def __repr__(self):
        return '<{}({provider} ({metadata_fieldcount} metadata fields))>'.format(
            self.__class__.__name__, **self.__dict__
        )


def _decode_any_bytestring(value):
    # Values *should* have been coerced at this point.
    if isinstance(value, bytes):
        return enc.displayable_path(value)
    return value


def do_extract_text(fileobject):
    any_text_extraction_results = list()

    try:
        text = text_provider.get_plain_text(fileobject)
        if text:
            assert isinstance(text, str)
            any_text_extraction_results.append(
                TextExtractionResult(fulltext=text, provider='(unknown extractor)')
            )
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: %s', e)

    return any_text_extraction_results


def do_extract_metadata(fileobject):
    provider_results = defaultdict(dict)

    def _collect_results_callback(fileobject_, meowuri, data):
        assert isinstance(data, dict)
        _value = data.get('value')
        _str_value = _decode_any_bytestring(_value)
        _extractor = data.get('source', '(unknown extractor)')

        provider_results[_extractor][meowuri] = _str_value

    runner = extraction.ExtractorRunner(
        add_results_callback=_collect_results_callback
    )
    request_extractors = set(extractors.registry.metadata_providers)
    request_extractors.update(extractors.registry.filesystem_providers)
    try:
        runner.start(fileobject, request_extractors)
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: %s', e)
    else:
        all_metadata_extraction_results = list()
        for provider, metadata in provider_results.items():
            all_metadata_extraction_results.append(MetadataExtractionResult(
                metadata=metadata, provider=provider
            ))
        return all_metadata_extraction_results


def display_file_processing_starting(fileobject, num, total_fileobject_num):
    # TODO: [TD0171] Separate logic from user interface.
    view.msg('{!s}'.format(fileobject), style='heading')
    log.info('Processing (%s/%s) "%s" ..', num, total_fileobject_num, fileobject)


def display_file_processing_ended(fileobject, num, total_fileobject_num):
    log.info('Finished processing (%s/%s) "%s"', num, total_fileobject_num, fileobject)


def display_text_extraction_result(fileobject, text_extraction_result):
    provider = text_extraction_result.provider
    text = text_extraction_result.fulltext
    if text:
        # TODO: [TD0171] Separate logic from user interface.
        view.msg('Text Extracted by {!s}:'.format(provider), style='section')
        view.msg(text)
    else:
        log.info('%s was unable to extract text from "%s"', provider, fileobject)


def display_metadata_extraction_result(results):
    _results = list(results)

    lines_to_display = list()
    for metadata_extraction_result in _results:
        provider = str(metadata_extraction_result.provider)
        for uri, data in sorted(metadata_extraction_result.metadata.items()):
            lines_to_display.append((str(uri), str(data), provider))

    # TODO: [cleanup] Refactor data structures passed to this function.
    # Output is built in two passes like this in order to get the output sorted
    # by MeowURIS. The 'MetadataExtractionResult' objects passed in here are not
    # designed very well. Should have written the usage code first..
    cf = _get_column_formatter()
    for uri, data, provider in sorted(lines_to_display):
        cf.addrow(str(uri), str(data), provider)

    # TODO: [TD0171] Separate logic from user interface.
    view.msg('Extracted Metadata', style='section')
    view.msg(str(cf))


def display_summary_metadata_stats(all_processed_files, metadata_results):
    num_files_processed = len(all_processed_files)
    files_not_in_results = [f for f in all_processed_files
                            if not metadata_results[f]]

    cf = _get_column_formatter()
    cf.addrow('PROCESSED FILE', '# METADATA FIELDS', 'PROVIDER')
    cf.addrow('==============', '=================', '========')
    for f, metadata_extraction_results in sorted(metadata_results.items()):
        for metadata_extraction_result in metadata_extraction_results:
            field_count = str(metadata_extraction_result.metadata_fieldcount)
            provider = str(metadata_extraction_result.provider)
            cf.addrow(str(f), field_count, provider)
    for f in files_not_in_results:
        cf.addrow(str(f), 'N/A', 'N/A')

    # TODO: [TD0171] Separate logic from user interface.
    view.msg('Metadata Extraction Results', style='section')
    view.msg('Got results for {} out of {} total processed files'.format(len(metadata_results), num_files_processed))
    view.msg('Remaining {} files could either not be handled by any extractor or the extraction failed'.format(len(files_not_in_results), num_files_processed))
    view.msg(' ')
    view.msg(str(cf))


def display_summary_text_stats(all_processed_files, text_results):
    num_files_processed = len(all_processed_files)
    files_not_in_results = [f for f in all_processed_files
                            if f not in text_results]

    cf = _get_column_formatter()
    cf.addrow('PROCESSED FILE', '# LINES', 'PROVIDER')
    cf.addrow('==============', '=======', '========')
    for f, text_extraction_results in sorted(text_results.items()):
        for text_extraction_result in text_extraction_results:
            linecount = str(text_extraction_result.fulltext_linecount)
            provider = str(text_extraction_result.provider)
            cf.addrow(str(f), linecount, provider)
    for f in files_not_in_results:
        cf.addrow(str(f), 'N/A', 'N/A')

    view.msg('Text Extraction Results', style='section')
    view.msg('Got results for {} out of {} total processed files'.format(len(text_results), num_files_processed))
    view.msg('Remaining {} files could either not be handled by any extractor or the extraction failed'.format(len(files_not_in_results), num_files_processed))
    view.msg(' ')
    view.msg(str(cf))


def display_summary_statistics(all_processed_files, summary_results):
    # TODO: [TD0171] Separate logic from user interface.
    view.msg('Summary Extraction Result Statistics', style='heading')

    results_text = summary_results['text']
    display_summary_text_stats(all_processed_files, results_text)

    results_metadata = summary_results['metadata']
    display_summary_metadata_stats(all_processed_files, results_metadata)


def main(options=None):
    if options is None:
        options = dict()

    # Default options are defined here.
    # Passed in 'options' always take precedence and overrides the defaults.
    opts = {
        'debug': False,
        'verbose': False,

        'show_stats': False,

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

    num_files_total = len(files_to_process)
    log.info('Got %s files to process', num_files_total)

    summary_results = {
        'text': defaultdict(list),
        'metadata': defaultdict(dict),
    }
    all_processed_files = list()
    for n, filepath in enumerate(files_to_process, start=1):
        try:
            current_file = FileObject(filepath)
        except (exceptions.InvalidFileArgumentError,
                exceptions.FilesystemError) as e:
            log.warning('%s --- SKIPPING: "%s"', e, enc.displayable_path(filepath))
            continue

        all_processed_files.append(current_file)
        display_file_processing_starting(current_file, n, num_files_total)

        if opts.get('extract_text'):
            with logs.log_runtime(log, 'Text Extraction', log_level='INFO'):
                results = do_extract_text(current_file)

            for result in results:
                summary_results['text'][current_file].append(result)
                display_text_extraction_result(current_file, result)

        if opts.get('extract_metadata'):
            with logs.log_runtime(log, 'Metadata Extraction', log_level='INFO'):
                results = do_extract_metadata(current_file)

            summary_results['metadata'][current_file] = results
            display_metadata_extraction_result(results)

        display_file_processing_ended(current_file, n, num_files_total)

    if opts.get('show_stats'):
        display_summary_statistics(all_processed_files, summary_results)


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

    optgrp_debug = parser.add_argument_group('Debug/developer options')
    optgrp_debug.add_argument(
        '--stats',
        dest='show_stats',
        action='store_true',
        help='Display detailed information on all extraction results.'
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

        'show_stats': opts.show_stats,

        'extract_text': opts.extract_text,
        'extract_metadata': opts.extract_metadata,

        'input_paths': opts.input_paths,
    }

    try:
        main(options)
    except KeyboardInterrupt:
        sys.exit('\nReceived keyboard interrupt; Exiting ..')
    finally:
        # Shutdown pooled extractor instances.
        event.dispatcher.on_shutdown()


if __name__ == '__main__':
    cli_main(sys.argv[1:])
