`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------


Testing TL;DR
=============

| File Name               | Execute this to run .. |
| ----------------------- | -----------------------|
| `common_runner.sh`      | __All tests__          |
| `integration_runner.sh` | Integration Tests      |
| `regression_runner.sh`  | Regression Tests       |
| `unit_runner.sh`        | Unit Tests             |

All runner scripts will print usage information if started with `-h`.


Notes on `autonameow` testing
=============================
Tests are separated into three main types, "*unit tests*", "*integration
tests*" and "*regression tests*".
This separation is not enforced. Some of the "integration tests" are not
strictly correct integration tests; in practice, all code that was easier to
write as a bash script ended up in this pile.

Moving forward, the "integration tests" will be used less in favor of the new
"regression tests". The unit tests should be fast and test very small parts of
the system, like individual classes, methods and functions.
The regression tests should exercise the entire system with actual use-cases.


Unit Tests
----------
All unit tests are written in Python and uses the `unittest` library.

Unit test source files are located in the `tests/unit` directory.

File names that start with `test_property_` uses the Python library
[hypothesis](http://hypothesis.works/) to do property-based testing.
These are skipped if `hypothesis` is unavailable.


### Running the Unit Tests
All unit tests can be executed with the bash script `tests/unit_runner.sh`.


This script accepts optional argument flags, described in the usage text;

```
"unit_runner.sh"  --  autonameow unit tests runner

  USAGE:  unit_runner.sh ([OPTIONS])

  OPTIONS:     -h   Display usage information and exit.
               -c   Enable checking unit test coverage.
               -w   Write HTML test reports to disk.
                    Note: the "raw" log file is always written.
               -q   Suppress output from test suites.

  All options are optional. Default behaviour is to not write any
  reports and print the test results to stdout/stderr in real-time.

  EXIT CODES:   0   All tests/assertions passed.
                1   Any tests/assertions FAILED.
                2   Runner itself failed or aborted.


Project website: www.github.com/jonasjberg/autonameow
```


Integration Tests
-----------------
These are not strictly integration tests, written in bash.

Integration test source files are located in the `tests/integration` directory.


### Running the Integration Tests
In order to run all tests, execute the script `tests/integration_runner.sh`.

This script accepts optional argument flags, as described in the usage text;

```
"integration_runner.sh"  --  autonameow integration test suite runner

  USAGE:  integration_runner.sh ([OPTIONS])

  OPTIONS:     -f [EXP]   Execute scripts by filtering basenames.
                          Argument [EXP] is passed to grep as-is.
                          Scripts whose basename does not match the
                          expression are skipped.
               -h         Display usage information and exit.
               -q         Suppress output from test suites.
               -w         Write HTML test reports to disk.
                          Note: The "raw" log file is always written.

  All options are optional. Default behaviour is to export test result
  reports and print the test results to stdout/stderr in real-time.

  EXIT CODES:   0         All tests/assertions passed.
                1         Any tests/assertions FAILED.
                2         Runner itself failed or aborted.

  Project website: www.github.com/jonasjberg/autonameow
```


Regression Tests
----------------
Actually not strictly regression tests, written in Python.
These tests will hit a lot of systems, depending on the test case.
The proper name would probable be "functional tests" or "system tests"..

Regression tests are located in the `tests/regression` directory.

Regression test cases are executed sequentially, each using a fresh instance
of `autonameow`. Only a few parts of the system are patched; execution time
measurement, exit status, and the function that actually performs renaming of
files.

This means that __regression tests never actually rename files__, even without
the `--dry-run` option. The state of this option is captured by does not
actually matter, the rename function call is captured and always results in a
no-op.


The test cases are stored as directories in `tests/regression`. Parameters and
options for the test case is split up across different files in the directory.

Example regression test case directory contents:

```
0003_filetags_c
|
|-- asserts.yaml
|-- config.yaml
|-- description
'-- options.yaml
```

The directory basename is the short-form name of the test, used by the runner
to refer to the test case. It also determines the order of execution.

In order for the regression test loader to recognize a directory as a test,
the directory name should match this regular expression:

```python
\d{4}(_[\w]+)?
```

.. E.G. `1234`, `1337_foo` and `6666_foo_bar` are all valid regression test
directory names.


The directory contains the following files:

* `description` --- Plain-text file with a longer description of
  the test.

* `asserts.yaml` --- __[REQUIRED]__ Assertions to be evaluated to
  determine whether the test passes or fails.

    * Example `asserts.yaml`:
        ```yaml
        exit_code: 0
        renames:
            2017-09-12 foo -- tag2 a tag1.txt: '2017-09-12 foo -- a tag1 tag2.txt'
            2017-11-20 bar -- tag1.txt: '2017-11-20T020738 bar -- tag1.txt'
        ```

* `options.yaml` --- Options to pass to the `autonameow` instance.
  These mirror the "internal format" options dict passed to the program
  in `autonameow/core/main.py`.

    * Example `options.yaml`:
        ```yaml
        config_path: $THISTEST/config.yaml
        debug: true
        dry_run: true
        dump_config: false
        dump_meowuris: false
        dump_options: false
        input_paths:
        - '$TESTFILES/2017-11-20 bar -- tag1.txt'
        - '$TESTFILES/2017-09-12 foo -- tag2 a tag1.txt'
        list_all: false
        mode_automagic: true
        mode_batch: true
        mode_interactive: false
        quiet: false
        recurse_paths: false
        show_version: false
        verbose: false
        ```

* `config.yaml` --- Configuration file, stored with the test for convenience.
  Use `config_path: $THISTEST/config.yaml` in `options.yaml` to refer to the
  config in the current test directory without having to pass in a full path.


### Special Variables in `options.yaml`
Paths can include the special keywords `$THISTEST` and `$TESTFILES`, this is
pretty ad-hoc and very likely to change. Refer to existing tests for hints on
how to write your own.

The following holds true as of version `v0.5.2`:

#### The `config_path` field
If the `config_path` entry..

* .. is missing, the path of the default (unit test) config is used.

    ```
    -->  'config_path': (Path to the default config)
    ```

* .. starts with `$TESTFILES/`, the full absolute path to the
     "test_files" directory is inserted in place of `$TESTFILES/`.

    ```
         'config_path': '$TESTFILES/config.yaml'
    -->  'config_path': '$SRCROOT/test_files/config.yaml'
    ```

* .. starts with `$THISTEST/`, the full absolute path to the current
     regression test directory is inserted in place of `$THISTEST/`.

    ```
         'config_path': '$THISTEST/config.yaml'
    -->  'config_path': 'self.abspath/config.yaml'
    ```

#### The `input_paths` field
The string `$TESTFILES` is replaced with the full absolute path to the
`test_files` directory.
For instance; `'$TESTFILES/foo.txt' --> '$SRCROOT/test_files/foo.txt'`,
where `$SRCROOT` is the full absolute path to the autonameow sources.


### Running the Regression Tests
In order to run all tests, execute the script `tests/regression_runner.sh`.

This script accepts optional argument flags, as described in the usage text;

```
Usage: regression_runner.py [-h] [-v] [--stderr] [--stdout] [-f GLOB]
                            [--last-failed] [--list] [--get-cmd] [--run]

autonameow v0.5.3 -- regression test suite runner

Optional arguments:
  -h, --help            Show this help message and exit.
  -v, --verbose         Enables verbose mode, prints additional information.
  --stderr              Print captured stderr.
  --stdout              Print captured stdout.

Test Selection:
  Selection is performed in the order in which the options are listed here.
  I.E. first any glob filtering, then selecting last failed, etc.

  -f GLOB, --filter GLOB
                        Select tests whose "TEST_NAME" (dirname) matches
                        "GLOB". Matching is case-sensitive. An asterisk
                        matches anything and if "GLOB" begins with "!", the
                        matching is inverted.
  --last-failed         Select only the test cases that failed during the last
                        completed run. Selects all if none failed.

Actions to Perform:
  Only the first active option is used, ordered as per this listing.

  --list                Print the "short name" (directory basename) of the
                        selected test case(s) and exit.
  --get-cmd             Print equivalent command-line invocations for the
                        selected test case(s) and exit. If executed
                        "manually", these would produce the same behaviour and
                        results as the corresponding regression test. Each
                        result is printed as two lines; first being "#
                        TEST_NAME", where "TEST_NAME" is the directory
                        basename of the test case. The second line is the
                        equivalent command-line. Use "test selection" options
                        to narrow down the results.
  --run                 Run the selected test case(s). (DEFAULT: True)

Project website: www.github.com/jonasjberg/autonameow
```
