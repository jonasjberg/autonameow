# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import os
import magic

MAGIC_TYPE_LOOKUP = {'bmp':   ['image/x-ms-bmp'],
                     'gif':   ['image/gif'],
                     'jpg':   ['image/jpeg'],
                     'mp4':   ['video/mp4'],
                     'ogg':   ['video/ogg'],
                     'pdf':   ['application/pdf'],
                     'png':   ['image/png'],
                     'txt':   ['text/plain'],
                     'empty': ['inode/x-empty']}


def filetype_magic(file_path):
    """
    Determine file type by reading "magic" header bytes.
    Similar to the 'file' command in *NIX environments.
    :return:
    """
    # Workaround confusion around what magic library actually gets used.
    # http://www.zak.co.il/tddpirate/2013/03/03/the-python-module-for-file-type-identification-called-magic-is-not-standardized/
    def build_magic():
        try:
            mymagic = magic.open(magic.MAGIC_MIME_TYPE)
            mymagic.load()
        except AttributeError, e:
            mymagic = magic.Magic(mime=True)
            mymagic.file = mymagic.from_file
        return (mymagic)

    mymagic = build_magic()
    mtype = mymagic.file(file_path)
    if not mtype:
        return None

    # http://stackoverflow.com/a/16588375
    def find_key(input_dict, value):
        return next((k for k, v in input_dict.items() if v == value), None)

    try:
        found_type = find_key(MAGIC_TYPE_LOOKUP, mtype.split()[:2])
    except KeyError:
        return None

    return found_type.lower() if found_type else None


def split_filename(file_path):
    """
    Split file name of the file located in "file_path" into two components;
    "name" and "suffix/extension".
    :param file_path: path to the file to split
    :return: tuple of the file "name" and "extension/suffix"
    """
    base, ext = os.path.splitext(os.path.basename(file_path))

    if ext.lower() in ['.bz2', '.gz', '.lz', '.lzma', '.lzo', '.xz', '.z']:
        # Split "base" twice to make compound suffix out of the two extensions.
        ext = os.path.splitext(base)[1] + ext

    ext = ext.lstrip('.')

    if ext and ext.strip():
        return base, ext
    else:
        return base, None


def file_suffix(file_path, make_lowercase=True):
    """
    Get file suffix/extension for the file located in "file_path".
    Handles some special cases, for instance "basename.tar.gz" returns
    the suffix "tar.gz" and not just the extension "gz".
    :param file_path: path to the file from which to get extension.
    :param make_lowercase: make the extension lowercase, defaults to True
    :return: the file suffix/extension if found, else None
    """
    _, ext = split_filename(file_path)

    if ext and make_lowercase:
        ext = ext.lower()

    return ext


def file_base(file_path):
    """
    Get file basename without extension/suffix for the file located in
    "file_path".
    :param file_path: path to the file from which to get extension.
    :return: the file basename without extension if not empty, else None
    """
    base, _ = split_filename(file_path)
    return base if base else None
