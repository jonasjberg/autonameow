#!/usr/bin/env bash
pdftotext -layout "$1" - 2>/dev/null
