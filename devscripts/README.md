`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------


`devscripts`
============
Various utility scripts related to `autonameow` development.


### `average_runtime_regression_tests.sh`
Calculates the average runtime of the regression runner.

### `analyze-available-data.sh`
Experimental script for finding expected field values in the output of
`autonameow --list-all`.

### `check_whitespace.sh`
Check text file style violations, whitespace, line separators and tabs.

### `cloc.sh`
Generate statistics on the project source code using `cloc`.

### `ctags.sh`
Generate `.tags` file with `ctags`.

### `delete-python-caches.sh`
Delete all `*.pyc` files and `__pycache__` directories.

### `find_unit_test_visits.sh`
Find which unit tests that covered which lines of source code using `smother`.

### `functions-rarely-called.sh`
Very simple *and likely broken* search of unused functions and methods.

### `lint_bash.sh`
Perform static analysis on all bash scripts using `shellcheck`.

### `lint_python.sh`
Perform static analysis on all Python scripts using `pylint`.

### `list-imported-modules.sh`
List modules imported by the specified Python program.

### `run_command_on_git_revs.sh`
Execute arbitrary shell commands over a range of git revisions.

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
