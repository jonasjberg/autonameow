#!/usr/bin/env bash

set -o nounset -o errexit -o pipefail -o noclobber

exit 1
# TODO: Fix this


[ -d babelfish-?.?.? ] && {
    mv -v -- babelfish-?.?.?/LICENSE babelfish_LICENSE.txt &&
    mv -v -- babelfish-?.?.?/babelfish babelfish &&
    rm -rv -- babelfish-?.?.?

	# Remove tests and test-only data
	rm -v 'babelfish/tests.py'
	rm -v 'babelfish/data/opensubtitles_languages.txt'
}

BS4_BASEDIR='beautifulsoup4-4.4.1'
[ -d "$BS4_BASEDIR" ] && {
	( cd "$BS4_BASEDIR" &&
	  ./convert-py3k &&
	  find . -xdev -type f -name "*.bak" -delete) &&
      mv -v COPYING.txt ../bs4_COPYING.txt &&
      mv -v py3k/bs4/ ../bs4
    ) && rm -rv "$BS4_BASEDIR"
}

[ -d 'chardet-2.3.0' ] && {
    mv -v chardet-2.3.0/LICENSE chardet_LICENSE.txt &&
    mv -v chardet-2.3.0/chardet/ chardet &&
    rm -rv chardet-2.3.0
}

[ -d 'colorama-0.3.7' ] && {
    mv -v colorama-0.3.7/LICENSE.txt colorama_LICENSE.txt &&
    mv -v colorama-0.3.7/colorama/ colorama &&
    rm -rv colorama-0.3.7
}

[ -d 'EbookLib-0.16' ] && {
    mv -v EbookLib-0.16/LICENSE.txt ebooklib_LICENSE.txt &&
    mv -v EbookLib-0.16/ebooklib/ ebooklib &&
    rm -rv EbookLib-0.16
}

[ -d 'file-magic-0.4.0' ] && {
    mv -v file-magic-0.4.0/magic.py magic.py &&
    rm -rv file-magic-0.4.0
}

[ -d 'guessit-2.1.0' ] && {
    mv -v guessit-2.1.0/LICENSE guessit_LICENSE.txt &&
    mv -v guessit-2.1.0/guessit guessit &&
    rm -rv guessit-2.1.0
}

[ -d 'isbnlib-3.5.6' ] && {
    mv -v isbnlib-3.5.6/README.rst isbnlib_README.rst &&
    mv -v isbnlib-3.5.6/isbnlib/ isbnlib &&
    rm -rv isbnlib-3.5.6
}

[ -d 'lxml-4.2.5' ] && {
    mv -v lxml-4.2.5/LICENSES.txt lxml_LICENSES.txt &&
    mv -v lxml-4.2.5/src/lxml/ lxml &&
    rm -rv lxml-4.2.5
}

# TODO: Pillow-5.3.0

[ -d 'prompt_toolkit-1.0.15' ] && {
    mv -v prompt_toolkit-1.0.15/LICENSE prompt_toolkit_LICENSE.txt &&
    mv -v prompt_toolkit-1.0.15/prompt_toolkit/ prompt_toolkit &&
    rm -rv prompt_toolkit-1.0.15
}

[ -d 'python-dateutil-2.7.5' ] && {
    mv -v python-dateutil-2.7.5/LICENSE dateutil_LICENSE.txt &&
    mv -v python-dateutil-2.7.5/dateutil/ dateutil &&
    rm -rv python-dateutil-2.7.5
}

[ -d 'pytz-2018.7' ] && {
    mv -v pytz-2018.7/LICENSE.txt pytz_LICENSE.txt &&
    mv -v pytz-2018.7/pytz/ pytz &&
    rm -rv pytz-2018.7
}

[ -d 'PyYAML-3.11' ] && {
    mv -v PyYAML-3.11/LICENSE yaml_LICENSE.txt &&
    mv -v PyYAML-3.11/lib3/yaml/ yaml &&
    rm -rv PyYAML-3.11
}

[ -d 'rebulk-1.0.0' ] && {
    mv -v rebulk-1.0.0/LICENSE rebulk_LICENSE.txt &&
    mv -v rebulk-1.0.0/rebulk/ rebulk &&
    rm -rv rebulk-1.0.0
}

[ -d 'six-1.11.0' ] && {
    mv -v six-1.11.0/LICENSE six_LICENSE.txt &&
    mv -v six-1.11.0/six.py six.py &&
    rm -rv six-1.11.0
}

[ -d 'Unidecode-0.04.19' ] && {
    mv -v Unidecode-0.04.19/LICENSE unidecode_LICENSE.txt &&
    mv -v Unidecode-0.04.19/unidecode/ unidecode &&
    rm -rv Unidecode-0.04.19
}

[ -d 'wcwidth-0.1.7' ] && {
    mv -v wcwidth-0.1.7/LICENSE.txt wcwidth_LICENSE.txt &&
    mv -v wcwidth-0.1.7/wcwidth/ wcwidth &&
    rm -rv wcwidth-0.1.7
}
