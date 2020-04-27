`autonameow`
============
*Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------


`devscripts`
============
Various utility scripts related to `autonameow` development.


### `average_runtime_regression_tests.sh`
Calculates the average runtime of the regression runner.

### `check_spelling.sh`
Searches the sources for previously and/or commonly misspelled words.

### `check_whitespace.sh`
Check text file style violations, whitespace, line separators and tabs.

### `cloc.sh`
Generate statistics on the project source code using `cloc`.

### `ctags.sh`
Generate `.tags` file with `ctags`.

### `delete_python_caches.sh`
Delete all `*.pyc` files and `__pycache__` directories.

### `find_unit_test_visits.sh`
Find which unit tests that covered which lines of source code using `smother`.

### `functions_rarely_called.sh`
Very simple *and likely broken* search of unused functions and methods.

### `lint_bash.sh`
Perform static analysis on all bash scripts using `shellcheck`.

### `lint_python.sh`
Perform static analysis on all Python scripts using `pylint`.

### `lint_yaml.sh`
Perform static analysis on all YAML files using `yamllint`.

### `run_command_on_git_revs.sh`
Execute arbitrary shell commands over a range of git revisions.

### `todo_grep.sh`
Simple `grep` wrapper for searching the sources for TODOs.

### `todo_id.py`
Helper utility for listing and verifying TODO-list item identifiers.

### `unit_test_badness_metrics.py`
Calculates metrics from CSV-file produced by `smother`.

### `vulture.sh`
Find unused code using `vulture`.

### `write_default_config.sh`
Write `default_config.py` as configuration files used by tests.

### `write_sample_textfiles.py`
Write sample text to files using different encodings.
