#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import inspect
import io
import os
import random
import string
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import MagicMock, Mock

import unit.constants as uuconst
from core import FileObject
from util import encoding as enc


def samplefile_abspath(filename):
    """
    Utility function used by tests to construct a full path to individual test
    files in the 'samplefiles' directory.

    Args:
        filename: Basename of a file in the 'samplefiles' directory as a Unicode
                  string (internal string format)

    Returns:
        The full absolute path to the sample file with the given basename.
    """
    return os.path.abspath(os.path.join(
        uuconst.DIRPATH_SAMPLEFILES,
        filename,
    ))


def samplefile_config_abspath(filename=uuconst.DEFAULT_YAML_CONFIG_BASENAME):
    """
    Utility function used by tests to construct a full path to individual
    configuration files in the 'samplefiles/configs' directory.

    Args:
        filename: Basename of a file in the 'samplefiles/configs' directory as
                  a Unicode string.

    Returns:
        The absolute path to the given configuration file as a Unicode string,
        or the default configuration file if no basename is specified.
    """
    assert isinstance(filename, str), type(filename)
    return os.path.abspath(os.path.join(
        uuconst.DIRPATH_SAMPLEFILES,
        'configs',
        filename,
    ))


def encode(s):
    return enc.encode_(s)


def decode(s):
    return enc.decode_(s)


def bytestring_path(path):
    return enc.bytestring_path(path)


def normpath(path):
    return enc.normpath(path)


def all_samplefiles():
    """
    Returns: Absolute paths to all files in the "samplefiles" directory
        as a list of Unicode strings.
    """
    _abs_paths = [
        os.path.abspath(os.path.join(uuconst.DIRPATH_SAMPLEFILES, f))
        for f in os.listdir(uuconst.DIRPATH_SAMPLEFILES)
    ]
    return [
        f for f in _abs_paths if os.path.isfile(f) and not os.path.islink(f)
    ]


def file_exists(filepath):
    """
    Tests whether a given path is an existing file.

    Args:
        filepath: Path to the file to test.

    Returns:
        True if the file exists, else False.
    """
    try:
        return bool(os.path.isfile(enc.syspath(filepath)))
    except (OSError, TypeError, ValueError):
        return False


def dir_exists(dirpath):
    """
    Tests whether a given path is an existing directory.

    Args:
        dirpath: The path to test.

    Returns:
        True if the directory exists and is readable, else False.
    """
    _path = enc.syspath(dirpath)
    try:
        return bool(os.path.exists(_path) and os.path.isdir(_path))
    except (OSError, TypeError, ValueError):
        return False


def path_is_readable(filepath):
    """
    Tests whether a given path is readable.

    Args:
        filepath: The path to test.

    Returns:
        True if the path is readable.
        False for any other case, including errors.
    """
    try:
        return bool(os.access(enc.syspath(filepath), os.R_OK))
    except (OSError, TypeError, ValueError):
        return False


def is_abspath(path):
    """
    Tests whether a given path is an absolute path.

    Args:
        path: The path to test.

    Returns:
        True if the path is an absolute path as per 'os.path.isabs(path)'.
        False for any other case, including errors.
    """
    try:
        return bool(os.path.isabs(enc.syspath(path)))
    except (OSError, TypeError, ValueError):
        return False


def make_temp_dir():
    """
    Creates and returns a temporary directory.

    Returns:
        The path to a new temporary directory, as an "internal" bytestring.
    """
    return normpath(tempfile.mkdtemp())


def make_temporary_file(prefix=None, suffix=None, basename=None):
    """
    Creates a temporary file and returns the full path to the file.

    Use "basename" to specify a specific file basename, including any extension.
    Arguments "prefix" and "suffix" have no effect if "basename" is specified.

    If "basename" is not specified, either or both of "prefix" and "suffix"
    can be used to specify a fixed suffix or prefix of the file basename.
    Any file extension should be specified with "suffix".

    Args:
        prefix: Optional prefix for the file basename given as a string.
        suffix: Optional suffix for the file basename given as a string.
        basename: Basename for the file given as a string.
            Overrides "prefix" and "suffix".

    Returns:
        The full absolute path of the created file as a bytestring.
    """
    temp_filepath = os.path.realpath(
        tempfile.NamedTemporaryFile(
            delete=False,
            prefix=prefix,
            suffix=suffix,
        ).name
    )

    if basename:
        # Rename the file.
        dest_filepath = os.path.abspath(os.path.join(
            os.path.dirname(temp_filepath),
            enc.syspath(basename),
        ))
        os.rename(temp_filepath, dest_filepath)
        resulting_filepath = dest_filepath
    else:
        resulting_filepath = temp_filepath

    return bytestring_path(resulting_filepath)


def get_mock_fileobject(mime_type=None):
    """
    Returns 'FileObject' instances for use by unit tests.

    The returned instance is either created from a sample file with the
    specified MIME-type, or from a new temporary file if no MIME-type is given.

    Args:
        mime_type: Optional MIME type of an existing sample file.

    Returns:
        An instance of 'FileObject' constructed from a file on disk.
    """
    # TODO: [hardcoded] Might break if options data structure is modified.

    SAMPLEFILE_FROM_MIMETYPE_LOOKUP = {
        'application/pdf': 'magic_pdf.pdf',
        'image/gif': 'magic_gif.gif',
        'image/jpeg': 'magic_jpg.jpg',
        'image/png': 'magic_png.png',
        'image/x-ms-bmp': 'magic_bmp.bmp',
        'text/plain': 'magic_txt.txt',
        'text/rtf': 'sample.rtf',
        'video/mp4': 'magic_mp4.mp4',
        'inode/x-empty': 'empty',
    }
    if mime_type and mime_type in SAMPLEFILE_FROM_MIMETYPE_LOOKUP:
        filename = SAMPLEFILE_FROM_MIMETYPE_LOOKUP[mime_type]
        return fileobject_from_samplefile(filename)

    filepath = make_temporary_file()
    return fileobject_from_filepath(filepath)


def get_meowuri():
    """
    Returns 'MeowURI' instances for use by unit tests.

    Returns:
        A valid MeowURI instance with any kind of valid value.
    """
    return as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)


def fileobject_from_filepath(filepath):
    bytestring_filepath = bytestring_path(filepath)
    return FileObject(bytestring_filepath)


def fileobject_from_samplefile(filename):
    """
    Like 'samplefile_abspath' but wraps the result in a 'FileObject' instance.
    """
    return FileObject(normpath(samplefile_abspath(filename)))


def get_mock_analyzer():
    """
    Returns: A mock Analyzer class.
    """
    # TODO: [hack][cleanup] Mock properly! Remove?
    n = 0
    while n < len(get_instantiated_analyzers()):
        yield get_instantiated_analyzers()[n]
        n += 1


@contextmanager
def capture_stdout(finally_print=False):
    """Save stdout in a StringIO.

    >>> with capture_stdout() as output:
    ...     print('spam')
    ...
    >>> output.getvalue()
    'spam'

    NOTE:  This method was lifted and modified from the "beets" project.

           Source repo: https://github.com/beetbox/beets
           Source file: 'beets/test/helper.py'
           Commit hash: 7a2bdf502f88a278da6be55f93770dad738a14e6
    """
    initial_state = sys.stdout
    sys.stdout = capture = io.StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = initial_state
        if finally_print:
            print(capture.getvalue())


@contextmanager
def capture_stderr(finally_print=False):
    """Save stderr in a StringIO.

    >>> with capture_stdout() as output:
    ...     print('spam')
    ...
    >>> output.getvalue()
    'spam'

    NOTE:  This method was lifted and modified from the "beets" project.

           Source repo: https://github.com/beetbox/beets
           Source file: 'beets/test/helper.py'
           Commit hash: 7a2bdf502f88a278da6be55f93770dad738a14e6
    """
    initial_state = sys.stderr
    sys.stderr = capture = io.StringIO()
    try:
        yield sys.stderr
    finally:
        sys.stderr = initial_state
        if finally_print:
            print(capture.getvalue())


def get_instantiated_analyzers():
    """
    Get a list of all available analyzers as instantiated class objects.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        A list of class instances, one per subclass of "Analyzer".
    """
    # NOTE: These are instantiated with a None FileObject, which might be a
    #       problem and is surely not very pretty.
    # TODO: [hack][cleanup] Mock properly! Remove?
    import analyzers
    registered, _ = analyzers.get_analyzer_classes()
    return [klass(None, None, None) for klass in registered]


def get_dummy_rulecondition_instances():
    # TODO: [hack][cleanup] Mock properly! Remove?
    from core.config.rules import RuleCondition
    return [
        RuleCondition(as_meowuri(meowuri_string), expression)
        for meowuri_string, expression in uuconst.DUMMY_RAW_RULE_CONDITIONS
    ]


def get_dummy_raw_conditions():
    # TODO: [hack][cleanup] Mock properly! Remove?
    return [{meowuri: expression}
            for meowuri, expression in uuconst.DUMMY_RAW_RULE_CONDITIONS]


def get_dummy_raw_data_sources():
    # TODO: [hack][cleanup] Mock properly! Remove?
    return uuconst.DUMMY_RAW_RULE_DATA_SOURCES


def get_dummy_parsed_conditions():
    # TODO: [hack][cleanup] Mock properly! Remove?
    _dummy_raw_conditions = get_dummy_raw_conditions()

    from core.config.config_parser import parse_rule_conditions
    return [parse_rule_conditions(c) for c in _dummy_raw_conditions]


def get_dummy_rule():
    # TODO: [hack][cleanup] Does this behave as the "mocked" systems? (!)
    _dummy_parsed_conditions = get_dummy_parsed_conditions()

    from core.config.rules import Rule
    return Rule(
        description='dummy',
        exact_match=False,
        ranking_bias=0.5,
        name_template='dummy',
        conditions=_dummy_parsed_conditions[0],
        data_sources=get_dummy_raw_data_sources()[0]
    )


def is_class_instance(thing):
    """
    Tests whether a given object is a instance of a class.

    Note that primitives or builtins are not considered class instances.
    This function is intended for verifying user-defined classes.

    Args:
        thing: The object to test.

    Returns:
        True if the given object is an instance of a class that is not a
        builtin or primitive, otherwise False.
    """
    if not thing:
        return False

    if isinstance(thing, (type, bool, str, bytes, int, float, list, set, tuple)):
        return False

    if hasattr(thing, '__class__'):
        return True

    return False


def is_class(thing):
    """
    Tests whether a given object is an (uninstantiated) class.

    Args:
        thing: The object to test.

    Returns:
        True if the given object is a class, otherwise False.
    """
    return bool(inspect.isclass(thing))


def str_to_datetime(yyyy_mm_ddthhmmss, tz=None):
    """
    Converts a string on the form "YYYY-MM-DD HHMMSS" to a 'datetime' object.

    Args:
        yyyy_mm_ddthhmmss: String to convert.

    Returns:
        A 'datetime' object if the conversion was successful.
    Raises:
        ValueError: The string could not be converted.
    """
    if tz is None:
        return datetime.strptime(yyyy_mm_ddthhmmss, '%Y-%m-%d %H%M%S')
    else:
        _time_string = yyyy_mm_ddthhmmss + tz
        return datetime.strptime(_time_string, '%Y-%m-%d %H%M%S%z')


def is_importable(module_name):
    """
    Tests if a given module can be imported without raising an exception.

    Returns: True if the module was successfully imported, otherwise False.
    """
    try:
        _ = __import__(module_name, None, None)
    except (TypeError, ValueError, ImportError):
        return False
    else:
        return True


def init_session_repository():
    # TODO: [hack][cleanup] Mock properly! Remove?
    from core.datastore import repository
    repository._initialize()


def init_provider_registry():
    from core import master_provider
    master_provider._initialize_provider_registry()


def init_master_data_provider(active_config):
    from core import master_provider
    master_provider._initialize_master_data_provider(active_config)


def is_internalstring(thing):
    if thing is None:
        return False
    return bool(isinstance(thing, str))


def is_internalbytestring(thing):
    if thing is None:
        return False
    return bool(isinstance(thing, bytes))


def get_default_config():
    # TODO: [hack][cleanup] Mock properly! Remove?
    init_session_repository()

    _config_path = normpath(samplefile_config_abspath())
    assert isinstance(_config_path, bytes)

    from core.config.config_parser import ConfigurationParser
    config_parser = ConfigurationParser()
    return config_parser.from_file(_config_path)


def mock_persistence_path():
    return b'/tmp/autonameow_cache'


def mock_cache_path():
    return b'/tmp/autonameow_cache'


def as_meowuri(s):
    from core.model import MeowURI
    from core.exceptions import InvalidMeowURIError
    try:
        return MeowURI(s)
    except InvalidMeowURIError as e:
        raise AssertionError(e)


def get_expected_text_for_samplefile(filename):
    """
    Returns any text that should be extracted from a given sample file.

    If the given basename is found in the 'samplefiles' directory and a
    accompanying file containing reference text is found, it is returned.

    Args:
        filename: Basename of a file in the 'samplefiles' directory as a Unicode
                  string (internal string format)

    Returns:
        Reference, expected text contained in file as a Unicode string or None
        if there is no file with expected text.
    """
    assert isinstance(filename, str)

    expected_text_basename = filename + '_expected.txt'
    expected_text_filepath = samplefile_abspath(expected_text_basename)
    try:
        with open(expected_text_filepath, 'r', encoding='utf8') as fh:
            return fh.read()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError):
        raise


def get_mock_provider():
    mock_provider = Mock()
    mock_provider.metainfo = MagicMock(return_value=dict())
    mock_provider.name.return_value = 'MockProvider'
    return mock_provider


def random_ascii_string(num_chars):
    assert isinstance(num_chars, int)
    ASCII_CHARS = string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(ASCII_CHARS) for _ in range(num_chars))
