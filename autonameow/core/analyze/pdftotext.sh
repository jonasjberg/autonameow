#!/usr/bin/env bash
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.
pdftotext -layout "$1" - 2>/dev/null
