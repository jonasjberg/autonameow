#!/usr/bin/env bash

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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
source "$AUTONAMEOW_ROOT_DIR/tests/integration/utils.sh"



# Test Cases
# ____________________________________________________________________________

# Store current time for later calculation of total execution time.
time_start="$(aw_utils.current_unix_time)"

TESTSUITE_NAME='Compatibility'
aw_utils.log_msg "Running the ${TESTSUITE_NAME} test suite .."



# ______________________________________________________________________________
# Reporting program version and related.
# Testing version in the compatilibity section of the config.

aw_utils.assert_true '"$AUTONAMEOW_RUNNER"' \
            'The autonameow launcher script can be started with no arguments'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version' \
            'autonameow should return zero when started with "--version"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version -v' \
            'autonameow should return zero when started with "--version -v"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version 2>&1 | grep -o -- "v[0-9]\.[0-9]\.[0-9]"' \
            'Output should contain a version string matching "vX.X.X" when started with "--version"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version -v 2>&1 | grep -o -- "v[0-9]\.[0-9]\.[0-9]"' \
            'Output should contain a version string matching "vX.X.X" when started with "--version -v"'

current_git_commit_hash="$(cd "$AUTONAMEOW_ROOT_DIR" && git rev-parse --short HEAD)"
# NOTE(jonas): git rev-parse --short HEAD returns different length.
#              Hash string is one extra character on MacOS (git version 2.15.1)
#              compared to Linux (git version 2.7.4).

# Truncate to 7 characters before matching.
current_git_commit_hash="${current_git_commit_hash:0:6}"

aw_utils.assert_false '[ -z "$current_git_commit_hash" ]' \
             'This test script should be able to retrieve the git hash of the current git commit'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version -v 2>&1 | grep -o -- "(commit [a-zA-Z0-9]\{7\})"' \
            'Output should contain a string matching "(commit [a-zA-Z0-9]\{7\})" when started with "--version -v"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --version -v 2>&1 | grep -o -- ".*${current_git_commit_hash}.*"' \
            'Output should contain a string matching the previously retrieved git commit hash when started with "--version -v"'


# Get version string defined in the sources
_version_file="${AUTONAMEOW_ROOT_DIR}/autonameow/core/version.py"
aw_utils.assert_bulk_test "$_version_file" e f r

AUTONAMEOW_SOURCE_VERSION="$(grep -- '__version_info__ = ' "$_version_file" | grep -o -- '[0-9], [0-9], [0-9]' | sed 's/\([0-9]\), \([0-9]\), \([0-9]\)/\1.\2.\3/')"
aw_utils.assert_false '[ -z "$AUTONAMEOW_SOURCE_VERSION" ]' \
             "This test script should be able to retrieve the version from \"${_version_file}\"."

_autonameow_source_version_linecount="$(wc -l <<< "$AUTONAMEOW_SOURCE_VERSION")"
aw_utils.assert_true '[ "$_autonameow_source_version_linecount" -eq "1" ]' \
            "The matched \"${_version_file}\" file version should be a single line, I.E. contains one version string"


# Get version reported by running 'autonameow --version'
AUTONAMEOW_VERSION="$( ( "$AUTONAMEOW_RUNNER" --version 2>&1 ) | grep -o -- "v[0-9]\.[0-9]\.[0-9]" | grep -o -- "[0-9]\.[0-9]\.[0-9]")"
aw_utils.assert_false '[ -z "$AUTONAMEOW_VERSION" ]' \
             'This test script should be able to retrieve the program version.'

_autonameow_version_linecount="$(wc -l <<< "$AUTONAMEOW_VERSION")"
aw_utils.assert_true '[ "$_autonameow_version_linecount" -eq "1" ]' \
            'The matched program version should be a single line, I.E. contains one version string'


# Get the version of the configuration file that is used when running the program
aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --verbose 2>&1 | grep -o -- "Using configuration: \".*\"$"' \
            'The output should include the currently used configuration file when started with "--verbose"'

AUTONAMEOW_CONFIG_PATH="$( ( "$AUTONAMEOW_RUNNER" --verbose 2>&1 ) | grep -o -- "Using configuration: \".*\"$" | grep -o -- "\".*\"")"
aw_utils.assert_false '[ -z "$AUTONAMEOW_CONFIG_PATH" ]' \
             'This test script should be able to retrieve the path of the used configuration file.'

# Strip quotes from configuration file path.
AUTONAMEOW_CONFIG_PATH="${AUTONAMEOW_CONFIG_PATH//\"/}"
aw_utils.assert_bulk_test "$AUTONAMEOW_CONFIG_PATH" e f r w

aw_utils.assert_true 'grep -oE -- "autonameow_version: v?[0-9]\.[0-9]\.[0-9]$" "$AUTONAMEOW_CONFIG_PATH"' \
            'The retrieved configuration file contents should match "autonameow_version: X.X.X$"'

CONFIG_FILE_VERSION="$(grep -oE -- "autonameow_version: v?[0-9]\.[0-9]\.[0-9]$" "$AUTONAMEOW_CONFIG_PATH" | grep -o -- "[0-9]\.[0-9]\.[0-9]")"
aw_utils.assert_false '[ -z "$CONFIG_FILE_VERSION" ]' \
             'This test script should be able to retrieve the configuration file version.'

_config_file_version_linecount="$(wc -l <<< "$CONFIG_FILE_VERSION")"
aw_utils.assert_true '[ "$_config_file_version_linecount" -eq "1" ]' \
            'The matched configuration file version should be a single line, I.E. contains one version string'


# Check that all gathered version strings are the same.
aw_utils.assert_true '[ "$AUTONAMEOW_SOURCE_VERSION" = "$AUTONAMEOW_VERSION" ]' \
            "The version in \"${_version_file}\" should equal the program version"

aw_utils.assert_true '[ "$AUTONAMEOW_VERSION" = "$CONFIG_FILE_VERSION" ]' \
            'The configuration file version should equal the program version'

aw_utils.assert_true '[ "$AUTONAMEOW_SOURCE_VERSION" = "$CONFIG_FILE_VERSION" ]' \
            "The version in \"${_version_file}\" should equal the configuration file version"


# ______________________________________________________________________________
#
# Handling of various bad configuration files.

EMPTY_CONFIG='/tmp/autonameow_empty_config.yaml'
aw_utils.assert_true 'touch "$EMPTY_CONFIG"' \
            'detect_empty_config Test setup should succeed'
aw_utils.assert_bulk_test "$EMPTY_CONFIG" e f r

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --config-path "$EMPTY_CONFIG"' \
             'detect_empty_config Specifying a empty configuration file with "--config-path" should be handled properly'

aw_utils.assert_true '[ -f "$EMPTY_CONFIG" ] && rm -- "$EMPTY_CONFIG"' \
            'detect_empty_config Test teardown should succeed'

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --config-path /tmp/does_not_exist_surely.mjao' \
             'Specifying an invalid path with "--config-path" should be handled properly'


BAD_CONFIG_FILE="$(aw_utils.abspath_testfile "configs/bad_corrupt_gif.yaml")"
aw_utils.assert_bulk_test "$BAD_CONFIG_FILE" e f r

aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE"' \
             'Attempting to load a invalid configuration file with "--config-path" should be handled properly'


aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-options --verbose' \
            'autonameow should return zero when started with "--dump-options" and "--verbose"'


NONASCII_CONFIG_FILE="$(aw_utils.abspath_testfile "configs/autonam€öw.yaml")"
aw_utils.assert_bulk_test "$NONASCII_CONFIG_FILE" e f r

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --config-path "$NONASCII_CONFIG_FILE"' \
            'Attempting to load a non-ASCII configuration file with "--config-path" should be handled properly'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --verbose --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--verbose"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --debug --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --quiet --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--quiet"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-options --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--dump-options"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-options --verbose --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--dump-options", "--verbose"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-options --debug --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--dump-options", "--debug"'

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --dump-options --quiet --config-path "$NONASCII_CONFIG_FILE"' \
            'Expect exit code 0 for non-ASCII configuration file and "--dump-options", "--quiet"'


set +o pipefail
BAD_CONFIG_FILE_NO_FILE_RULES="$(aw_utils.abspath_testfile "configs/bad_no_file_rules.yaml")"
aw_utils.assert_bulk_test "$BAD_CONFIG_FILE_NO_FILE_RULES" e f r

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE_NO_FILE_RULES" 2>&1 | grep -q "Unable to load configuration"' \
            'Attempting to load a configuration file without any file rules should be handled properly'

BAD_CONFIG_FILE_EMPTY_BUT_SECTIONS="$(aw_utils.abspath_testfile "configs/bad_empty_but_sections.yaml")"
aw_utils.assert_bulk_test "$BAD_CONFIG_FILE_EMPTY_BUT_SECTIONS" e f r

aw_utils.assert_true '"$AUTONAMEOW_RUNNER" --config-path "$BAD_CONFIG_FILE_EMPTY_BUT_SECTIONS" 2>&1 | grep -q "Unable to load configuration"' \
            'Attempting to load a configuration file with just bare sections should be handled properly'
set -o pipefail


# Find all files matching "samplefiles/configs/bad_0*.yaml"
# and check for non-zero return codes in various options.
while IFS= read -r -d '' bad_config_file
do
    config_file_abspath="$(realpath --canonicalize-existing -- "$bad_config_file")"
    config_file_basename="$(basename -- "$bad_config_file")"
    aw_utils.assert_true '[ -e "$config_file_abspath" ]' \
                "Bad configuration file exists: \"${config_file_basename}\""

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\""

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" -v --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in batch, verbose mode"

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --debug --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in batch, debug mode"

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --quiet --dry-run --batch --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in batch, quiet mode"

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" -v --dry-run --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in verbose mode"

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --debug --dry-run --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in debug mode"

    aw_utils.assert_false '"$AUTONAMEOW_RUNNER" --quiet --dry-run --config-path "$BAD_CONFIG_FILE"' \
                 "Expect non-zero exit code for bad config: \"${config_file_basename}\" in quiet mode"

done < <(find "${AUTONAMEOW_SAMPLEFILES_DIR}/configs" -maxdepth 1 -xdev -type f -name 'bad_0*.yaml' -print0 | sort -z)


# ______________________________________________________________________________
#
# START of testing that persistence options from the config are used.
#
# Tests the assumption that autonameow writes at least one file to the
# persistence path set in the config.

TEMPLATED_DEFAULT_CONFIG="$(aw_utils.abspath_testfile "configs/integration_default_templated.yaml")"
aw_utils.assert_bulk_test "$TEMPLATED_DEFAULT_CONFIG" f r w

TEMP_PERSISTENCE_DIR="$(realpath --canonicalize-existing -- "$(mktemp -d -t aw_test_persistence.XXXXXX)")"
aw_utils.assert_bulk_test "$TEMP_PERSISTENCE_DIR" d r w x

_sed_backup_suffix='.orig'
aw_utils.assert_true 'sed -i${_sed_backup_suffix} "s@___cache_directory___@${TEMP_PERSISTENCE_DIR}@g" "$TEMPLATED_DEFAULT_CONFIG"' \
            'Expect OK exit status for sed call replacing template placeholder ___cache_directory___'

templated_default_config_backup="${TEMPLATED_DEFAULT_CONFIG}${_sed_backup_suffix}"
aw_utils.assert_bulk_test "$templated_default_config_backup" f r w

_number_files_in_temp_persistence_dir="$(find "$TEMP_PERSISTENCE_DIR" -type f -mindepth 1 -type f | wc -l)"
aw_utils.assert_true '[ "$_number_files_in_temp_persistence_dir" -eq "0" ]' \
            'Temporary persistence directory should initially not contain any files'

# Arbitrary execution just to do *something* with the persistence directory.
"$AUTONAMEOW_RUNNER" --quiet --dry-run --batch --config-path "$TEMPLATED_DEFAULT_CONFIG" -- "${AUTONAMEOW_SAMPLEFILES_DIR}" &>/dev/null

_number_files_in_temp_persistence_dir="$(find "$TEMP_PERSISTENCE_DIR" -type f -mindepth 1 -type f | wc -l)"
aw_utils.assert_true '[ "$_number_files_in_temp_persistence_dir" -ge "1" ]' \
            'Temporary persistence directory should contain at least one file after autonameow execution'

aw_utils.assert_true '[ -f "$templated_default_config_backup" ] && mv -- "$templated_default_config_backup" "$TEMPLATED_DEFAULT_CONFIG"' \
            'Successfully restored the original templated configuration file'

# END of testing that persistence options from the config are used.
# ______________________________________________________________________________




# Calculate total execution time.
time_end="$(aw_utils.current_unix_time)"
total_time="$(aw_utils.calculate_execution_time "$time_start" "$time_end")"

aw_utils.log_test_suite_results_summary "$TESTSUITE_NAME" "$total_time"
aw_utils.update_global_test_results
