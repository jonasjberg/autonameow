`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------


`devscripts`
============
Various utility scripts related to `autonameow` development.


### `analyze-available-data.sh`
Experimental script for finding expected field values in the output of
`autonameow --list-all`.

### `check-wiki-report.sh`
Used to automate documentation for the `1dv430` course.

### `cloc.sh`
Generate statistics on the project source code using `cloc`.

### `convert-html-to.pdf.sh`
Convert all HTML test reports to PDF.

### `ctags.sh`
Generate `.tags` file with `ctags`.

### `delete-python-caches.sh`
Delete all `*.pyc` files and `__pycache__` directories.

### `filter_list-all_meowuris.sh`
Run autonameow with the given file(s) and the `--list-all` option and filters
the output to display a lexicographically sorted list of unique MeowURIs.

### `lint_bash.sh`
Perform static analysis on all bash scripts using `shellcheck`.

### `list-imported-modules.sh`
List modules imported by the specified Python program.

### `run-tests-and-update-wiki.sh`
Used to automate documentation for the `1dv430` course.

### `todo_grep.sh`
Simple `grep` wrapper for searching the sources for TODOs.

### `todo_id.py`
Helper utility for listing and verifying TODO-list item identifiers.

### `vulture.sh`
Find unused code using `vulture`.

### `write-default-config.sh`
Write `default_config.py` as configuration files used by tests.

### `write_sample_textfiles.py`
Write sample text to files using different encodings.
