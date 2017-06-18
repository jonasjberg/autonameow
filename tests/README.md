`autonameow`
============
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------


Testing TL;DR
=============

| File Name                   | Execute this to run ..                    |
| --------------------------- | ----------------------------------------- |
| `common_runner.sh`          | __ALL tests__ (`-h` for help)             |
| `integration_runner.sh`     | __ALL Integration Tests__ (`-h` for help) |
| `integration_test_cli.sh`   | The "Command-Line Interface" test suite   |
| `integration_test_docs.sh`  | The "Documentation" test suite            |
| `integration_test_src.sh`   | The "Source Code" test suite              |
| `integration_test_tests.sh` | The "Test Suite" test suite"              |
| `unit_runner.sh`            | __ALL Unit Tests__ (`-h` for help)        |



Notes on `autonameow` testing
=============================
Tests are separated into two main types, "*unit tests*" and
"*integration tests*". This separation is not enforced. Some of the
"integration tests" are not strictly correct integration tests; in practice,
all code that was easier to write as a bash script ended up in this pile.

Unit Tests
----------
All unit tests are written in Python and uses the `unittest` library.

Unit test source files share the common prefix `unit_test_`.

### Running the Unit Tests
All unit tests can be executed with the bash script `tests/unit_runner.sh`.


This script accepts optional argument flags, described in the usage text;

```
"unit_runner.sh"  --  autonameow unit tests runner

  USAGE:  unit_runner.sh ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -w   Write HTML test reports to disk.
                 Note: the "raw" log file is always written.
            -q   Suppress output from test suites.

  All options are optional. Default behaviour is to export test result
  reports and print the test results to stdout/stderr in real-time.
```


Integration Tests
-----------------
These are not strictly integration tests, written in bash.

Integration test source files share the common prefix `integration_test_`.

### Running the Integration Tests
In order to run all tests, execute the script `tests/integration_runner.sh`.

This script accepts optional argument flags, as described in the usage text;


```
"integration_runner.sh"  --  autonameow integration test suite runner

  USAGE:  integration_runner.sh ([OPTIONS])

  OPTIONS:  -h   Display usage information and exit.
            -q   Suppress output from test suites.
            -w   Write HTML test reports to disk.
                 Note: The "raw" log file is always written.

  All options are optional. Default behaviour is to export test result
  reports and print the test results to stdout/stderr in real-time.
```
