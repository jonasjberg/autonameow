#!/usr/bin/env bash


if ! command -v "wkhtmltopdf" >/dev/null 2>&1
then
    cat >&2 <<EOF

  The executable "wkhtmltopdf" is not available on this system.
       Please install "wkhtmltopdf" before running this script.

EOF
    exit 1
fi



for html_file in integration_log_*.html unittest_log_*.html
do
    [ -f "${html_file}" ] || continue

    dest_file="${html_file%.*}.pdf"
    [ -e "$dest_file" ] && continue

    wkhtmltopdf "$html_file" "${dest_file}"
done

