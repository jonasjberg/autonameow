#!/usr/bin/env bash

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

set -o noclobber -o nounset -o pipefail

if [ -z "${AUTONAMEOW_ROOT_DIR:-}" ]
then
    cat >&2 <<EOF

[ERROR] Integration test suites can no longer be run stand-alone.
        Please use use the designated integration test runner.

EOF
    exit 1
fi

# Resets test suite counter variables.
source "${AUTONAMEOW_ROOT_DIR}/tests/integration/utils.sh"

vendor_dirpath="${AUTONAMEOW_ROOT_DIR}/autonameow/vendor"
echo $vendor_dirpath

assert_can_import_python_module()
{
    local -r _module_name="$1"
    assert_true 'python3 -c "import sys ; sys.path.insert(0, \"${vendor_dirpath}\") ; import ${_module_name}"' \
                "python3 can import required module \"${_module_name}\""
}

assert_can_import_python_module_member()
{
    local -r _module_name="$1"
    local -r _member_name="$2"
    assert_true 'python3 -c "import sys ; sys.path.insert(0, \"${vendor_dirpath}\") ; from ${_module_name} import ${_member_name}"' \
                "python3 can import required module \"${_module_name}\" member \"${_member_name}\""
}



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(current_unix_time)"

TESTSUITE_NAME='Dependencies'
logmsg "Running the ${TESTSUITE_NAME} test suite .."



# ______________________________________________________________________________
#
# Verify that required commands are available.

assert_true 'case $OSTYPE in darwin*) ;; linux*) ;; *) false ;; esac' \
            'Should be running a target operating system'

assert_false '[ -z "$TERM" ]' \
             'Environment variable "$TERM" should be set'

assert_has_command 'python3'
assert_true 'python3 --version | grep "Python 3\.[5-9]\.[0-9]"' \
            'System python3 is version v3.5.0 or newer'

assert_has_command 'git'
assert_true 'git --version | grep "git version 2\..*"' \
            'System git version is newer than v2.x.x'


# Developer scripts and testing dependencies.
assert_has_command 'pytest'
_pytesthelp="$(pytest --help 2>&1)"
assert_true 'grep -q -- "--html" <<< "$_pytesthelp"' \
            'Module "pytest-html" is available on the system'

# assert_has_command 'vulture'
# assert_has_command 'aha'
# assert_has_command 'pylint'


# ______________________________________________________________________________
#
# Verify Python dependencies by running imports with python3.

assert_can_import_python_module 'bs4'
assert_can_import_python_module_member 'bs4' 'BeautifulSoup'
assert_can_import_python_module 'ebooklib'
assert_can_import_python_module_member 'ebooklib' 'epub'
assert_can_import_python_module 'chardet'
assert_can_import_python_module 'colorama'
assert_can_import_python_module 'guessit'
assert_can_import_python_module 'prompt_toolkit'
assert_can_import_python_module_member 'prompt_toolkit' 'prompt'
assert_can_import_python_module_member 'prompt_toolkit.completion' 'Completer'
assert_can_import_python_module_member 'prompt_toolkit.history' 'InMemoryHistory'
assert_can_import_python_module 'pytz'
assert_can_import_python_module 'unidecode'
assert_can_import_python_module_member 'unidecode' 'unidecode'
assert_can_import_python_module 'yaml'  # pyyaml


# ______________________________________________________________________________
#
# Make sure that binary dependencies are available.

assert_has_command 'exiftool'
assert_has_command 'jpeginfo'
assert_has_command 'pandoc'  # MarkdownTextExtractor
assert_has_command 'pdftotext'
assert_has_command 'tesseract'
assert_has_command 'unrtf'
assert_has_command 'djvutxt'




# Calculate total execution time.
time_end="$(current_unix_time)"
total_time="$(calculate_execution_time "$time_start" "$time_end")"

log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
update_global_test_results
