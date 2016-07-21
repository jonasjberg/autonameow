# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import os


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
