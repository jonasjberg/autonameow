# -*- coding: utf-8 -*-

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

import os
from setuptools import find_packages
from setuptools import setup

# TODO: [TD0008] Simplify installation.
# TODO: [TD0008] Add support for 'pip' or similar package manager.

# Access attributes without importing the file.
# https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
ABSPATH_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
projectmeta = dict()
with open(os.path.realpath(os.path.join(
        ABSPATH_THIS_DIR, 'autonameow', 'core', 'version.py'
))) as fp:
    exec(fp.read(), projectmeta)


setup(
    name=projectmeta['__title__'],
    version=projectmeta['__version__'],
    author=projectmeta['__author__'],
    author_email=projectmeta['__email__'],
    maintainer=projectmeta['__author__'],
    maintainer_email=projectmeta['__email__'],
    description='Automagic File Renamer',
    keywords='automagic filename management metadata pim rename',
    url=projectmeta['__url_repo__'],
    license=projectmeta['__license__'],
    packages=find_packages(exclude=['unit']),

    # TODO: Handle 'lxml' properly!
    # TODO: Handle 'Pillow' properly!
    package_data={
        'autonameow': [
            'analyzers/probable_extension_lookup',
            'core/truths/data/creatortool.yaml',
            'core/truths/data/language.yaml',
            'core/truths/data/publisher.yaml',
            'extractors/filesystem/crossplatform_fieldmeta.yaml',
            'extractors/filesystem/filetags_fieldmeta.yaml',
            'extractors/filesystem/extractor_guessit_fieldmeta.yaml',
            'extractors/metadata/exiftool_fieldmeta.yaml',
            'extractors/metadata/extractor_pandoc_template.plain',
            'extractors/metadata/jpeginfo_fieldmeta.yaml',
            'extractors/metadata/pandoc_fieldmeta.yaml',
            'util/mimemagic.mappings',
            'util/mimemagic.preferred',
            'vendor/babelfish/data/iso-3166-1.txt',
            'vendor/babelfish/data/iso-639-3.tab',
            'vendor/babelfish/data/iso15924-utf8-20131012.txt',
            'vendor/babelfish/data/opensubtitles_languages.txt',
            'vendor/babelfish_LICENSE.txt',
            'vendor/bs4_COPYING.txt',
            'vendor/chardet_LICENSE.txt',
            'vendor/colorama_LICENSE.txt',
            'vendor/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz',
            'vendor/dateutil_LICENSE.txt',
            'vendor/ebooklib_LICENSE.txt',
            'vendor/guessit/rules/properties/website.py',
            'vendor/guessit/tlds-alpha-by-domain.txt',
            'vendor/guessit_LICENSE.txt',
            'vendor/isbnlib_README.rst',
            'vendor/lxml_LICENSES.txt',
            'vendor/prompt_toolkit_LICENSE.txt',
            'vendor/pytz/zoneinfo/Africa/Abidjan',
            'vendor/pytz/zoneinfo/Africa/Accra',
            'vendor/pytz/zoneinfo/Africa/Addis_Ababa',
            'vendor/pytz/zoneinfo/Africa/Algiers',
            'vendor/pytz/zoneinfo/Africa/Asmara',
            'vendor/pytz/zoneinfo/Africa/Asmera',
            'vendor/pytz/zoneinfo/Africa/Bamako',
            'vendor/pytz/zoneinfo/Africa/Bangui',
            'vendor/pytz/zoneinfo/Africa/Banjul',
            'vendor/pytz/zoneinfo/Africa/Bissau',
            'vendor/pytz/zoneinfo/Africa/Blantyre',
            'vendor/pytz/zoneinfo/Africa/Brazzaville',
            'vendor/pytz/zoneinfo/Africa/Bujumbura',
            'vendor/pytz/zoneinfo/Africa/Cairo',
            'vendor/pytz/zoneinfo/Africa/Casablanca',
            'vendor/pytz/zoneinfo/Africa/Ceuta',
            'vendor/pytz/zoneinfo/Africa/Conakry',
            'vendor/pytz/zoneinfo/Africa/Dakar',
            'vendor/pytz/zoneinfo/Africa/Dar_es_Salaam',
            'vendor/pytz/zoneinfo/Africa/Djibouti',
            'vendor/pytz/zoneinfo/Africa/Douala',
            'vendor/pytz/zoneinfo/Africa/El_Aaiun',
            'vendor/pytz/zoneinfo/Africa/Freetown',
            'vendor/pytz/zoneinfo/Africa/Gaborone',
            'vendor/pytz/zoneinfo/Africa/Harare',
            'vendor/pytz/zoneinfo/Africa/Johannesburg',
            'vendor/pytz/zoneinfo/Africa/Juba',
            'vendor/pytz/zoneinfo/Africa/Kampala',
            'vendor/pytz/zoneinfo/Africa/Khartoum',
            'vendor/pytz/zoneinfo/Africa/Kigali',
            'vendor/pytz/zoneinfo/Africa/Kinshasa',
            'vendor/pytz/zoneinfo/Africa/Lagos',
            'vendor/pytz/zoneinfo/Africa/Libreville',
            'vendor/pytz/zoneinfo/Africa/Lome',
            'vendor/pytz/zoneinfo/Africa/Luanda',
            'vendor/pytz/zoneinfo/Africa/Lubumbashi',
            'vendor/pytz/zoneinfo/Africa/Lusaka',
            'vendor/pytz/zoneinfo/Africa/Malabo',
            'vendor/pytz/zoneinfo/Africa/Maputo',
            'vendor/pytz/zoneinfo/Africa/Maseru',
            'vendor/pytz/zoneinfo/Africa/Mbabane',
            'vendor/pytz/zoneinfo/Africa/Mogadishu',
            'vendor/pytz/zoneinfo/Africa/Monrovia',
            'vendor/pytz/zoneinfo/Africa/Nairobi',
            'vendor/pytz/zoneinfo/Africa/Ndjamena',
            'vendor/pytz/zoneinfo/Africa/Niamey',
            'vendor/pytz/zoneinfo/Africa/Nouakchott',
            'vendor/pytz/zoneinfo/Africa/Ouagadougou',
            'vendor/pytz/zoneinfo/Africa/Porto-Novo',
            'vendor/pytz/zoneinfo/Africa/Sao_Tome',
            'vendor/pytz/zoneinfo/Africa/Timbuktu',
            'vendor/pytz/zoneinfo/Africa/Tripoli',
            'vendor/pytz/zoneinfo/Africa/Tunis',
            'vendor/pytz/zoneinfo/Africa/Windhoek',
            'vendor/pytz/zoneinfo/America/Adak',
            'vendor/pytz/zoneinfo/America/Anchorage',
            'vendor/pytz/zoneinfo/America/Anguilla',
            'vendor/pytz/zoneinfo/America/Antigua',
            'vendor/pytz/zoneinfo/America/Araguaina',
            'vendor/pytz/zoneinfo/America/Argentina/Buenos_Aires',
            'vendor/pytz/zoneinfo/America/Argentina/Catamarca',
            'vendor/pytz/zoneinfo/America/Argentina/ComodRivadavia',
            'vendor/pytz/zoneinfo/America/Argentina/Cordoba',
            'vendor/pytz/zoneinfo/America/Argentina/Jujuy',
            'vendor/pytz/zoneinfo/America/Argentina/La_Rioja',
            'vendor/pytz/zoneinfo/America/Argentina/Mendoza',
            'vendor/pytz/zoneinfo/America/Argentina/Rio_Gallegos',
            'vendor/pytz/zoneinfo/America/Argentina/Salta',
            'vendor/pytz/zoneinfo/America/Argentina/San_Juan',
            'vendor/pytz/zoneinfo/America/Argentina/San_Luis',
            'vendor/pytz/zoneinfo/America/Argentina/Tucuman',
            'vendor/pytz/zoneinfo/America/Argentina/Ushuaia',
            'vendor/pytz/zoneinfo/America/Aruba',
            'vendor/pytz/zoneinfo/America/Asuncion',
            'vendor/pytz/zoneinfo/America/Atikokan',
            'vendor/pytz/zoneinfo/America/Atka',
            'vendor/pytz/zoneinfo/America/Bahia',
            'vendor/pytz/zoneinfo/America/Bahia_Banderas',
            'vendor/pytz/zoneinfo/America/Barbados',
            'vendor/pytz/zoneinfo/America/Belem',
            'vendor/pytz/zoneinfo/America/Belize',
            'vendor/pytz/zoneinfo/America/Blanc-Sablon',
            'vendor/pytz/zoneinfo/America/Boa_Vista',
            'vendor/pytz/zoneinfo/America/Bogota',
            'vendor/pytz/zoneinfo/America/Boise',
            'vendor/pytz/zoneinfo/America/Buenos_Aires',
            'vendor/pytz/zoneinfo/America/Cambridge_Bay',
            'vendor/pytz/zoneinfo/America/Campo_Grande',
            'vendor/pytz/zoneinfo/America/Cancun',
            'vendor/pytz/zoneinfo/America/Caracas',
            'vendor/pytz/zoneinfo/America/Catamarca',
            'vendor/pytz/zoneinfo/America/Cayenne',
            'vendor/pytz/zoneinfo/America/Cayman',
            'vendor/pytz/zoneinfo/America/Chicago',
            'vendor/pytz/zoneinfo/America/Chihuahua',
            'vendor/pytz/zoneinfo/America/Coral_Harbour',
            'vendor/pytz/zoneinfo/America/Cordoba',
            'vendor/pytz/zoneinfo/America/Costa_Rica',
            'vendor/pytz/zoneinfo/America/Creston',
            'vendor/pytz/zoneinfo/America/Cuiaba',
            'vendor/pytz/zoneinfo/America/Curacao',
            'vendor/pytz/zoneinfo/America/Danmarkshavn',
            'vendor/pytz/zoneinfo/America/Dawson',
            'vendor/pytz/zoneinfo/America/Dawson_Creek',
            'vendor/pytz/zoneinfo/America/Denver',
            'vendor/pytz/zoneinfo/America/Detroit',
            'vendor/pytz/zoneinfo/America/Dominica',
            'vendor/pytz/zoneinfo/America/Edmonton',
            'vendor/pytz/zoneinfo/America/Eirunepe',
            'vendor/pytz/zoneinfo/America/El_Salvador',
            'vendor/pytz/zoneinfo/America/Ensenada',
            'vendor/pytz/zoneinfo/America/Fort_Nelson',
            'vendor/pytz/zoneinfo/America/Fort_Wayne',
            'vendor/pytz/zoneinfo/America/Fortaleza',
            'vendor/pytz/zoneinfo/America/Glace_Bay',
            'vendor/pytz/zoneinfo/America/Godthab',
            'vendor/pytz/zoneinfo/America/Goose_Bay',
            'vendor/pytz/zoneinfo/America/Grand_Turk',
            'vendor/pytz/zoneinfo/America/Grenada',
            'vendor/pytz/zoneinfo/America/Guadeloupe',
            'vendor/pytz/zoneinfo/America/Guatemala',
            'vendor/pytz/zoneinfo/America/Guayaquil',
            'vendor/pytz/zoneinfo/America/Guyana',
            'vendor/pytz/zoneinfo/America/Halifax',
            'vendor/pytz/zoneinfo/America/Havana',
            'vendor/pytz/zoneinfo/America/Hermosillo',
            'vendor/pytz/zoneinfo/America/Indiana/Indianapolis',
            'vendor/pytz/zoneinfo/America/Indiana/Knox',
            'vendor/pytz/zoneinfo/America/Indiana/Marengo',
            'vendor/pytz/zoneinfo/America/Indiana/Petersburg',
            'vendor/pytz/zoneinfo/America/Indiana/Tell_City',
            'vendor/pytz/zoneinfo/America/Indiana/Vevay',
            'vendor/pytz/zoneinfo/America/Indiana/Vincennes',
            'vendor/pytz/zoneinfo/America/Indiana/Winamac',
            'vendor/pytz/zoneinfo/America/Indianapolis',
            'vendor/pytz/zoneinfo/America/Inuvik',
            'vendor/pytz/zoneinfo/America/Iqaluit',
            'vendor/pytz/zoneinfo/America/Jamaica',
            'vendor/pytz/zoneinfo/America/Jujuy',
            'vendor/pytz/zoneinfo/America/Juneau',
            'vendor/pytz/zoneinfo/America/Kentucky/Louisville',
            'vendor/pytz/zoneinfo/America/Kentucky/Monticello',
            'vendor/pytz/zoneinfo/America/Knox_IN',
            'vendor/pytz/zoneinfo/America/Kralendijk',
            'vendor/pytz/zoneinfo/America/La_Paz',
            'vendor/pytz/zoneinfo/America/Lima',
            'vendor/pytz/zoneinfo/America/Los_Angeles',
            'vendor/pytz/zoneinfo/America/Louisville',
            'vendor/pytz/zoneinfo/America/Lower_Princes',
            'vendor/pytz/zoneinfo/America/Maceio',
            'vendor/pytz/zoneinfo/America/Managua',
            'vendor/pytz/zoneinfo/America/Manaus',
            'vendor/pytz/zoneinfo/America/Marigot',
            'vendor/pytz/zoneinfo/America/Martinique',
            'vendor/pytz/zoneinfo/America/Matamoros',
            'vendor/pytz/zoneinfo/America/Mazatlan',
            'vendor/pytz/zoneinfo/America/Mendoza',
            'vendor/pytz/zoneinfo/America/Menominee',
            'vendor/pytz/zoneinfo/America/Merida',
            'vendor/pytz/zoneinfo/America/Metlakatla',
            'vendor/pytz/zoneinfo/America/Mexico_City',
            'vendor/pytz/zoneinfo/America/Miquelon',
            'vendor/pytz/zoneinfo/America/Moncton',
            'vendor/pytz/zoneinfo/America/Monterrey',
            'vendor/pytz/zoneinfo/America/Montevideo',
            'vendor/pytz/zoneinfo/America/Montreal',
            'vendor/pytz/zoneinfo/America/Montserrat',
            'vendor/pytz/zoneinfo/America/Nassau',
            'vendor/pytz/zoneinfo/America/New_York',
            'vendor/pytz/zoneinfo/America/Nipigon',
            'vendor/pytz/zoneinfo/America/Nome',
            'vendor/pytz/zoneinfo/America/Noronha',
            'vendor/pytz/zoneinfo/America/North_Dakota/Beulah',
            'vendor/pytz/zoneinfo/America/North_Dakota/Center',
            'vendor/pytz/zoneinfo/America/North_Dakota/New_Salem',
            'vendor/pytz/zoneinfo/America/Ojinaga',
            'vendor/pytz/zoneinfo/America/Panama',
            'vendor/pytz/zoneinfo/America/Pangnirtung',
            'vendor/pytz/zoneinfo/America/Paramaribo',
            'vendor/pytz/zoneinfo/America/Phoenix',
            'vendor/pytz/zoneinfo/America/Port-au-Prince',
            'vendor/pytz/zoneinfo/America/Port_of_Spain',
            'vendor/pytz/zoneinfo/America/Porto_Acre',
            'vendor/pytz/zoneinfo/America/Porto_Velho',
            'vendor/pytz/zoneinfo/America/Puerto_Rico',
            'vendor/pytz/zoneinfo/America/Punta_Arenas',
            'vendor/pytz/zoneinfo/America/Rainy_River',
            'vendor/pytz/zoneinfo/America/Rankin_Inlet',
            'vendor/pytz/zoneinfo/America/Recife',
            'vendor/pytz/zoneinfo/America/Regina',
            'vendor/pytz/zoneinfo/America/Resolute',
            'vendor/pytz/zoneinfo/America/Rio_Branco',
            'vendor/pytz/zoneinfo/America/Rosario',
            'vendor/pytz/zoneinfo/America/Santa_Isabel',
            'vendor/pytz/zoneinfo/America/Santarem',
            'vendor/pytz/zoneinfo/America/Santiago',
            'vendor/pytz/zoneinfo/America/Santo_Domingo',
            'vendor/pytz/zoneinfo/America/Sao_Paulo',
            'vendor/pytz/zoneinfo/America/Scoresbysund',
            'vendor/pytz/zoneinfo/America/Shiprock',
            'vendor/pytz/zoneinfo/America/Sitka',
            'vendor/pytz/zoneinfo/America/St_Barthelemy',
            'vendor/pytz/zoneinfo/America/St_Johns',
            'vendor/pytz/zoneinfo/America/St_Kitts',
            'vendor/pytz/zoneinfo/America/St_Lucia',
            'vendor/pytz/zoneinfo/America/St_Thomas',
            'vendor/pytz/zoneinfo/America/St_Vincent',
            'vendor/pytz/zoneinfo/America/Swift_Current',
            'vendor/pytz/zoneinfo/America/Tegucigalpa',
            'vendor/pytz/zoneinfo/America/Thule',
            'vendor/pytz/zoneinfo/America/Thunder_Bay',
            'vendor/pytz/zoneinfo/America/Tijuana',
            'vendor/pytz/zoneinfo/America/Toronto',
            'vendor/pytz/zoneinfo/America/Tortola',
            'vendor/pytz/zoneinfo/America/Vancouver',
            'vendor/pytz/zoneinfo/America/Virgin',
            'vendor/pytz/zoneinfo/America/Whitehorse',
            'vendor/pytz/zoneinfo/America/Winnipeg',
            'vendor/pytz/zoneinfo/America/Yakutat',
            'vendor/pytz/zoneinfo/America/Yellowknife',
            'vendor/pytz/zoneinfo/Antarctica/Casey',
            'vendor/pytz/zoneinfo/Antarctica/Davis',
            'vendor/pytz/zoneinfo/Antarctica/DumontDUrville',
            'vendor/pytz/zoneinfo/Antarctica/Macquarie',
            'vendor/pytz/zoneinfo/Antarctica/Mawson',
            'vendor/pytz/zoneinfo/Antarctica/McMurdo',
            'vendor/pytz/zoneinfo/Antarctica/Palmer',
            'vendor/pytz/zoneinfo/Antarctica/Rothera',
            'vendor/pytz/zoneinfo/Antarctica/South_Pole',
            'vendor/pytz/zoneinfo/Antarctica/Syowa',
            'vendor/pytz/zoneinfo/Antarctica/Troll',
            'vendor/pytz/zoneinfo/Antarctica/Vostok',
            'vendor/pytz/zoneinfo/Arctic/Longyearbyen',
            'vendor/pytz/zoneinfo/Asia/Aden',
            'vendor/pytz/zoneinfo/Asia/Almaty',
            'vendor/pytz/zoneinfo/Asia/Amman',
            'vendor/pytz/zoneinfo/Asia/Anadyr',
            'vendor/pytz/zoneinfo/Asia/Aqtau',
            'vendor/pytz/zoneinfo/Asia/Aqtobe',
            'vendor/pytz/zoneinfo/Asia/Ashgabat',
            'vendor/pytz/zoneinfo/Asia/Ashkhabad',
            'vendor/pytz/zoneinfo/Asia/Atyrau',
            'vendor/pytz/zoneinfo/Asia/Baghdad',
            'vendor/pytz/zoneinfo/Asia/Bahrain',
            'vendor/pytz/zoneinfo/Asia/Baku',
            'vendor/pytz/zoneinfo/Asia/Bangkok',
            'vendor/pytz/zoneinfo/Asia/Barnaul',
            'vendor/pytz/zoneinfo/Asia/Beirut',
            'vendor/pytz/zoneinfo/Asia/Bishkek',
            'vendor/pytz/zoneinfo/Asia/Brunei',
            'vendor/pytz/zoneinfo/Asia/Calcutta',
            'vendor/pytz/zoneinfo/Asia/Chita',
            'vendor/pytz/zoneinfo/Asia/Choibalsan',
            'vendor/pytz/zoneinfo/Asia/Chongqing',
            'vendor/pytz/zoneinfo/Asia/Chungking',
            'vendor/pytz/zoneinfo/Asia/Colombo',
            'vendor/pytz/zoneinfo/Asia/Dacca',
            'vendor/pytz/zoneinfo/Asia/Damascus',
            'vendor/pytz/zoneinfo/Asia/Dhaka',
            'vendor/pytz/zoneinfo/Asia/Dili',
            'vendor/pytz/zoneinfo/Asia/Dubai',
            'vendor/pytz/zoneinfo/Asia/Dushanbe',
            'vendor/pytz/zoneinfo/Asia/Famagusta',
            'vendor/pytz/zoneinfo/Asia/Gaza',
            'vendor/pytz/zoneinfo/Asia/Harbin',
            'vendor/pytz/zoneinfo/Asia/Hebron',
            'vendor/pytz/zoneinfo/Asia/Ho_Chi_Minh',
            'vendor/pytz/zoneinfo/Asia/Hong_Kong',
            'vendor/pytz/zoneinfo/Asia/Hovd',
            'vendor/pytz/zoneinfo/Asia/Irkutsk',
            'vendor/pytz/zoneinfo/Asia/Istanbul',
            'vendor/pytz/zoneinfo/Asia/Jakarta',
            'vendor/pytz/zoneinfo/Asia/Jayapura',
            'vendor/pytz/zoneinfo/Asia/Jerusalem',
            'vendor/pytz/zoneinfo/Asia/Kabul',
            'vendor/pytz/zoneinfo/Asia/Kamchatka',
            'vendor/pytz/zoneinfo/Asia/Karachi',
            'vendor/pytz/zoneinfo/Asia/Kashgar',
            'vendor/pytz/zoneinfo/Asia/Kathmandu',
            'vendor/pytz/zoneinfo/Asia/Katmandu',
            'vendor/pytz/zoneinfo/Asia/Khandyga',
            'vendor/pytz/zoneinfo/Asia/Kolkata',
            'vendor/pytz/zoneinfo/Asia/Krasnoyarsk',
            'vendor/pytz/zoneinfo/Asia/Kuala_Lumpur',
            'vendor/pytz/zoneinfo/Asia/Kuching',
            'vendor/pytz/zoneinfo/Asia/Kuwait',
            'vendor/pytz/zoneinfo/Asia/Macao',
            'vendor/pytz/zoneinfo/Asia/Macau',
            'vendor/pytz/zoneinfo/Asia/Magadan',
            'vendor/pytz/zoneinfo/Asia/Makassar',
            'vendor/pytz/zoneinfo/Asia/Manila',
            'vendor/pytz/zoneinfo/Asia/Muscat',
            'vendor/pytz/zoneinfo/Asia/Nicosia',
            'vendor/pytz/zoneinfo/Asia/Novokuznetsk',
            'vendor/pytz/zoneinfo/Asia/Novosibirsk',
            'vendor/pytz/zoneinfo/Asia/Omsk',
            'vendor/pytz/zoneinfo/Asia/Oral',
            'vendor/pytz/zoneinfo/Asia/Phnom_Penh',
            'vendor/pytz/zoneinfo/Asia/Pontianak',
            'vendor/pytz/zoneinfo/Asia/Pyongyang',
            'vendor/pytz/zoneinfo/Asia/Qatar',
            'vendor/pytz/zoneinfo/Asia/Qyzylorda',
            'vendor/pytz/zoneinfo/Asia/Rangoon',
            'vendor/pytz/zoneinfo/Asia/Riyadh',
            'vendor/pytz/zoneinfo/Asia/Saigon',
            'vendor/pytz/zoneinfo/Asia/Sakhalin',
            'vendor/pytz/zoneinfo/Asia/Samarkand',
            'vendor/pytz/zoneinfo/Asia/Seoul',
            'vendor/pytz/zoneinfo/Asia/Shanghai',
            'vendor/pytz/zoneinfo/Asia/Singapore',
            'vendor/pytz/zoneinfo/Asia/Srednekolymsk',
            'vendor/pytz/zoneinfo/Asia/Taipei',
            'vendor/pytz/zoneinfo/Asia/Tashkent',
            'vendor/pytz/zoneinfo/Asia/Tbilisi',
            'vendor/pytz/zoneinfo/Asia/Tehran',
            'vendor/pytz/zoneinfo/Asia/Tel_Aviv',
            'vendor/pytz/zoneinfo/Asia/Thimbu',
            'vendor/pytz/zoneinfo/Asia/Thimphu',
            'vendor/pytz/zoneinfo/Asia/Tokyo',
            'vendor/pytz/zoneinfo/Asia/Tomsk',
            'vendor/pytz/zoneinfo/Asia/Ujung_Pandang',
            'vendor/pytz/zoneinfo/Asia/Ulaanbaatar',
            'vendor/pytz/zoneinfo/Asia/Ulan_Bator',
            'vendor/pytz/zoneinfo/Asia/Urumqi',
            'vendor/pytz/zoneinfo/Asia/Ust-Nera',
            'vendor/pytz/zoneinfo/Asia/Vientiane',
            'vendor/pytz/zoneinfo/Asia/Vladivostok',
            'vendor/pytz/zoneinfo/Asia/Yakutsk',
            'vendor/pytz/zoneinfo/Asia/Yangon',
            'vendor/pytz/zoneinfo/Asia/Yekaterinburg',
            'vendor/pytz/zoneinfo/Asia/Yerevan',
            'vendor/pytz/zoneinfo/Atlantic/Azores',
            'vendor/pytz/zoneinfo/Atlantic/Bermuda',
            'vendor/pytz/zoneinfo/Atlantic/Canary',
            'vendor/pytz/zoneinfo/Atlantic/Cape_Verde',
            'vendor/pytz/zoneinfo/Atlantic/Faeroe',
            'vendor/pytz/zoneinfo/Atlantic/Faroe',
            'vendor/pytz/zoneinfo/Atlantic/Jan_Mayen',
            'vendor/pytz/zoneinfo/Atlantic/Madeira',
            'vendor/pytz/zoneinfo/Atlantic/Reykjavik',
            'vendor/pytz/zoneinfo/Atlantic/South_Georgia',
            'vendor/pytz/zoneinfo/Atlantic/St_Helena',
            'vendor/pytz/zoneinfo/Atlantic/Stanley',
            'vendor/pytz/zoneinfo/Australia/ACT',
            'vendor/pytz/zoneinfo/Australia/Adelaide',
            'vendor/pytz/zoneinfo/Australia/Brisbane',
            'vendor/pytz/zoneinfo/Australia/Broken_Hill',
            'vendor/pytz/zoneinfo/Australia/Canberra',
            'vendor/pytz/zoneinfo/Australia/Currie',
            'vendor/pytz/zoneinfo/Australia/Darwin',
            'vendor/pytz/zoneinfo/Australia/Eucla',
            'vendor/pytz/zoneinfo/Australia/Hobart',
            'vendor/pytz/zoneinfo/Australia/LHI',
            'vendor/pytz/zoneinfo/Australia/Lindeman',
            'vendor/pytz/zoneinfo/Australia/Lord_Howe',
            'vendor/pytz/zoneinfo/Australia/Melbourne',
            'vendor/pytz/zoneinfo/Australia/North',
            'vendor/pytz/zoneinfo/Australia/NSW',
            'vendor/pytz/zoneinfo/Australia/Perth',
            'vendor/pytz/zoneinfo/Australia/Queensland',
            'vendor/pytz/zoneinfo/Australia/South',
            'vendor/pytz/zoneinfo/Australia/Sydney',
            'vendor/pytz/zoneinfo/Australia/Tasmania',
            'vendor/pytz/zoneinfo/Australia/Victoria',
            'vendor/pytz/zoneinfo/Australia/West',
            'vendor/pytz/zoneinfo/Australia/Yancowinna',
            'vendor/pytz/zoneinfo/Brazil/Acre',
            'vendor/pytz/zoneinfo/Brazil/DeNoronha',
            'vendor/pytz/zoneinfo/Brazil/East',
            'vendor/pytz/zoneinfo/Brazil/West',
            'vendor/pytz/zoneinfo/Canada/Atlantic',
            'vendor/pytz/zoneinfo/Canada/Central',
            'vendor/pytz/zoneinfo/Canada/Eastern',
            'vendor/pytz/zoneinfo/Canada/Mountain',
            'vendor/pytz/zoneinfo/Canada/Newfoundland',
            'vendor/pytz/zoneinfo/Canada/Pacific',
            'vendor/pytz/zoneinfo/Canada/Saskatchewan',
            'vendor/pytz/zoneinfo/Canada/Yukon',
            'vendor/pytz/zoneinfo/CET',
            'vendor/pytz/zoneinfo/Chile/Continental',
            'vendor/pytz/zoneinfo/Chile/EasterIsland',
            'vendor/pytz/zoneinfo/CST6CDT',
            'vendor/pytz/zoneinfo/Cuba',
            'vendor/pytz/zoneinfo/EET',
            'vendor/pytz/zoneinfo/Egypt',
            'vendor/pytz/zoneinfo/Eire',
            'vendor/pytz/zoneinfo/EST',
            'vendor/pytz/zoneinfo/EST5EDT',
            'vendor/pytz/zoneinfo/Etc/GMT',
            'vendor/pytz/zoneinfo/Etc/GMT+0',
            'vendor/pytz/zoneinfo/Etc/GMT+1',
            'vendor/pytz/zoneinfo/Etc/GMT+10',
            'vendor/pytz/zoneinfo/Etc/GMT+11',
            'vendor/pytz/zoneinfo/Etc/GMT+12',
            'vendor/pytz/zoneinfo/Etc/GMT+2',
            'vendor/pytz/zoneinfo/Etc/GMT+3',
            'vendor/pytz/zoneinfo/Etc/GMT+4',
            'vendor/pytz/zoneinfo/Etc/GMT+5',
            'vendor/pytz/zoneinfo/Etc/GMT+6',
            'vendor/pytz/zoneinfo/Etc/GMT+7',
            'vendor/pytz/zoneinfo/Etc/GMT+8',
            'vendor/pytz/zoneinfo/Etc/GMT+9',
            'vendor/pytz/zoneinfo/Etc/GMT-0',
            'vendor/pytz/zoneinfo/Etc/GMT-1',
            'vendor/pytz/zoneinfo/Etc/GMT-10',
            'vendor/pytz/zoneinfo/Etc/GMT-11',
            'vendor/pytz/zoneinfo/Etc/GMT-12',
            'vendor/pytz/zoneinfo/Etc/GMT-13',
            'vendor/pytz/zoneinfo/Etc/GMT-14',
            'vendor/pytz/zoneinfo/Etc/GMT-2',
            'vendor/pytz/zoneinfo/Etc/GMT-3',
            'vendor/pytz/zoneinfo/Etc/GMT-4',
            'vendor/pytz/zoneinfo/Etc/GMT-5',
            'vendor/pytz/zoneinfo/Etc/GMT-6',
            'vendor/pytz/zoneinfo/Etc/GMT-7',
            'vendor/pytz/zoneinfo/Etc/GMT-8',
            'vendor/pytz/zoneinfo/Etc/GMT-9',
            'vendor/pytz/zoneinfo/Etc/GMT0',
            'vendor/pytz/zoneinfo/Etc/Greenwich',
            'vendor/pytz/zoneinfo/Etc/UCT',
            'vendor/pytz/zoneinfo/Etc/Universal',
            'vendor/pytz/zoneinfo/Etc/UTC',
            'vendor/pytz/zoneinfo/Etc/Zulu',
            'vendor/pytz/zoneinfo/Europe/Amsterdam',
            'vendor/pytz/zoneinfo/Europe/Andorra',
            'vendor/pytz/zoneinfo/Europe/Astrakhan',
            'vendor/pytz/zoneinfo/Europe/Athens',
            'vendor/pytz/zoneinfo/Europe/Belfast',
            'vendor/pytz/zoneinfo/Europe/Belgrade',
            'vendor/pytz/zoneinfo/Europe/Berlin',
            'vendor/pytz/zoneinfo/Europe/Bratislava',
            'vendor/pytz/zoneinfo/Europe/Brussels',
            'vendor/pytz/zoneinfo/Europe/Bucharest',
            'vendor/pytz/zoneinfo/Europe/Budapest',
            'vendor/pytz/zoneinfo/Europe/Busingen',
            'vendor/pytz/zoneinfo/Europe/Chisinau',
            'vendor/pytz/zoneinfo/Europe/Copenhagen',
            'vendor/pytz/zoneinfo/Europe/Dublin',
            'vendor/pytz/zoneinfo/Europe/Gibraltar',
            'vendor/pytz/zoneinfo/Europe/Guernsey',
            'vendor/pytz/zoneinfo/Europe/Helsinki',
            'vendor/pytz/zoneinfo/Europe/Isle_of_Man',
            'vendor/pytz/zoneinfo/Europe/Istanbul',
            'vendor/pytz/zoneinfo/Europe/Jersey',
            'vendor/pytz/zoneinfo/Europe/Kaliningrad',
            'vendor/pytz/zoneinfo/Europe/Kiev',
            'vendor/pytz/zoneinfo/Europe/Kirov',
            'vendor/pytz/zoneinfo/Europe/Lisbon',
            'vendor/pytz/zoneinfo/Europe/Ljubljana',
            'vendor/pytz/zoneinfo/Europe/London',
            'vendor/pytz/zoneinfo/Europe/Luxembourg',
            'vendor/pytz/zoneinfo/Europe/Madrid',
            'vendor/pytz/zoneinfo/Europe/Malta',
            'vendor/pytz/zoneinfo/Europe/Mariehamn',
            'vendor/pytz/zoneinfo/Europe/Minsk',
            'vendor/pytz/zoneinfo/Europe/Monaco',
            'vendor/pytz/zoneinfo/Europe/Moscow',
            'vendor/pytz/zoneinfo/Europe/Nicosia',
            'vendor/pytz/zoneinfo/Europe/Oslo',
            'vendor/pytz/zoneinfo/Europe/Paris',
            'vendor/pytz/zoneinfo/Europe/Podgorica',
            'vendor/pytz/zoneinfo/Europe/Prague',
            'vendor/pytz/zoneinfo/Europe/Riga',
            'vendor/pytz/zoneinfo/Europe/Rome',
            'vendor/pytz/zoneinfo/Europe/Samara',
            'vendor/pytz/zoneinfo/Europe/San_Marino',
            'vendor/pytz/zoneinfo/Europe/Sarajevo',
            'vendor/pytz/zoneinfo/Europe/Saratov',
            'vendor/pytz/zoneinfo/Europe/Simferopol',
            'vendor/pytz/zoneinfo/Europe/Skopje',
            'vendor/pytz/zoneinfo/Europe/Sofia',
            'vendor/pytz/zoneinfo/Europe/Stockholm',
            'vendor/pytz/zoneinfo/Europe/Tallinn',
            'vendor/pytz/zoneinfo/Europe/Tirane',
            'vendor/pytz/zoneinfo/Europe/Tiraspol',
            'vendor/pytz/zoneinfo/Europe/Ulyanovsk',
            'vendor/pytz/zoneinfo/Europe/Uzhgorod',
            'vendor/pytz/zoneinfo/Europe/Vaduz',
            'vendor/pytz/zoneinfo/Europe/Vatican',
            'vendor/pytz/zoneinfo/Europe/Vienna',
            'vendor/pytz/zoneinfo/Europe/Vilnius',
            'vendor/pytz/zoneinfo/Europe/Volgograd',
            'vendor/pytz/zoneinfo/Europe/Warsaw',
            'vendor/pytz/zoneinfo/Europe/Zagreb',
            'vendor/pytz/zoneinfo/Europe/Zaporozhye',
            'vendor/pytz/zoneinfo/Europe/Zurich',
            'vendor/pytz/zoneinfo/Factory',
            'vendor/pytz/zoneinfo/GB',
            'vendor/pytz/zoneinfo/GB-Eire',
            'vendor/pytz/zoneinfo/GMT',
            'vendor/pytz/zoneinfo/GMT+0',
            'vendor/pytz/zoneinfo/GMT-0',
            'vendor/pytz/zoneinfo/GMT0',
            'vendor/pytz/zoneinfo/Greenwich',
            'vendor/pytz/zoneinfo/Hongkong',
            'vendor/pytz/zoneinfo/HST',
            'vendor/pytz/zoneinfo/Iceland',
            'vendor/pytz/zoneinfo/Indian/Antananarivo',
            'vendor/pytz/zoneinfo/Indian/Chagos',
            'vendor/pytz/zoneinfo/Indian/Christmas',
            'vendor/pytz/zoneinfo/Indian/Cocos',
            'vendor/pytz/zoneinfo/Indian/Comoro',
            'vendor/pytz/zoneinfo/Indian/Kerguelen',
            'vendor/pytz/zoneinfo/Indian/Mahe',
            'vendor/pytz/zoneinfo/Indian/Maldives',
            'vendor/pytz/zoneinfo/Indian/Mauritius',
            'vendor/pytz/zoneinfo/Indian/Mayotte',
            'vendor/pytz/zoneinfo/Indian/Reunion',
            'vendor/pytz/zoneinfo/Iran',
            'vendor/pytz/zoneinfo/iso3166.tab',
            'vendor/pytz/zoneinfo/Israel',
            'vendor/pytz/zoneinfo/Jamaica',
            'vendor/pytz/zoneinfo/Japan',
            'vendor/pytz/zoneinfo/Kwajalein',
            'vendor/pytz/zoneinfo/leapseconds',
            'vendor/pytz/zoneinfo/Libya',
            'vendor/pytz/zoneinfo/MET',
            'vendor/pytz/zoneinfo/Mexico/BajaNorte',
            'vendor/pytz/zoneinfo/Mexico/BajaSur',
            'vendor/pytz/zoneinfo/Mexico/General',
            'vendor/pytz/zoneinfo/MST',
            'vendor/pytz/zoneinfo/MST7MDT',
            'vendor/pytz/zoneinfo/Navajo',
            'vendor/pytz/zoneinfo/NZ',
            'vendor/pytz/zoneinfo/NZ-CHAT',
            'vendor/pytz/zoneinfo/Pacific/Apia',
            'vendor/pytz/zoneinfo/Pacific/Auckland',
            'vendor/pytz/zoneinfo/Pacific/Bougainville',
            'vendor/pytz/zoneinfo/Pacific/Chatham',
            'vendor/pytz/zoneinfo/Pacific/Chuuk',
            'vendor/pytz/zoneinfo/Pacific/Easter',
            'vendor/pytz/zoneinfo/Pacific/Efate',
            'vendor/pytz/zoneinfo/Pacific/Enderbury',
            'vendor/pytz/zoneinfo/Pacific/Fakaofo',
            'vendor/pytz/zoneinfo/Pacific/Fiji',
            'vendor/pytz/zoneinfo/Pacific/Funafuti',
            'vendor/pytz/zoneinfo/Pacific/Galapagos',
            'vendor/pytz/zoneinfo/Pacific/Gambier',
            'vendor/pytz/zoneinfo/Pacific/Guadalcanal',
            'vendor/pytz/zoneinfo/Pacific/Guam',
            'vendor/pytz/zoneinfo/Pacific/Honolulu',
            'vendor/pytz/zoneinfo/Pacific/Johnston',
            'vendor/pytz/zoneinfo/Pacific/Kiritimati',
            'vendor/pytz/zoneinfo/Pacific/Kosrae',
            'vendor/pytz/zoneinfo/Pacific/Kwajalein',
            'vendor/pytz/zoneinfo/Pacific/Majuro',
            'vendor/pytz/zoneinfo/Pacific/Marquesas',
            'vendor/pytz/zoneinfo/Pacific/Midway',
            'vendor/pytz/zoneinfo/Pacific/Nauru',
            'vendor/pytz/zoneinfo/Pacific/Niue',
            'vendor/pytz/zoneinfo/Pacific/Norfolk',
            'vendor/pytz/zoneinfo/Pacific/Noumea',
            'vendor/pytz/zoneinfo/Pacific/Pago_Pago',
            'vendor/pytz/zoneinfo/Pacific/Palau',
            'vendor/pytz/zoneinfo/Pacific/Pitcairn',
            'vendor/pytz/zoneinfo/Pacific/Pohnpei',
            'vendor/pytz/zoneinfo/Pacific/Ponape',
            'vendor/pytz/zoneinfo/Pacific/Port_Moresby',
            'vendor/pytz/zoneinfo/Pacific/Rarotonga',
            'vendor/pytz/zoneinfo/Pacific/Saipan',
            'vendor/pytz/zoneinfo/Pacific/Samoa',
            'vendor/pytz/zoneinfo/Pacific/Tahiti',
            'vendor/pytz/zoneinfo/Pacific/Tarawa',
            'vendor/pytz/zoneinfo/Pacific/Tongatapu',
            'vendor/pytz/zoneinfo/Pacific/Truk',
            'vendor/pytz/zoneinfo/Pacific/Wake',
            'vendor/pytz/zoneinfo/Pacific/Wallis',
            'vendor/pytz/zoneinfo/Pacific/Yap',
            'vendor/pytz/zoneinfo/Poland',
            'vendor/pytz/zoneinfo/Portugal',
            'vendor/pytz/zoneinfo/posixrules',
            'vendor/pytz/zoneinfo/PRC',
            'vendor/pytz/zoneinfo/PST8PDT',
            'vendor/pytz/zoneinfo/ROC',
            'vendor/pytz/zoneinfo/ROK',
            'vendor/pytz/zoneinfo/Singapore',
            'vendor/pytz/zoneinfo/Turkey',
            'vendor/pytz/zoneinfo/tzdata.zi',
            'vendor/pytz/zoneinfo/UCT',
            'vendor/pytz/zoneinfo/Universal',
            'vendor/pytz/zoneinfo/US/Alaska',
            'vendor/pytz/zoneinfo/US/Aleutian',
            'vendor/pytz/zoneinfo/US/Arizona',
            'vendor/pytz/zoneinfo/US/Central',
            'vendor/pytz/zoneinfo/US/East-Indiana',
            'vendor/pytz/zoneinfo/US/Eastern',
            'vendor/pytz/zoneinfo/US/Hawaii',
            'vendor/pytz/zoneinfo/US/Indiana-Starke',
            'vendor/pytz/zoneinfo/US/Michigan',
            'vendor/pytz/zoneinfo/US/Mountain',
            'vendor/pytz/zoneinfo/US/Pacific',
            'vendor/pytz/zoneinfo/US/Samoa',
            'vendor/pytz/zoneinfo/UTC',
            'vendor/pytz/zoneinfo/W-SU',
            'vendor/pytz/zoneinfo/WET',
            'vendor/pytz/zoneinfo/zone.tab',
            'vendor/pytz/zoneinfo/zone1970.tab',
            'vendor/pytz/zoneinfo/Zulu',
            'vendor/pytz_LICENSE.txt',
            'vendor/rebulk_LICENSE.txt',
            'vendor/six_LICENSE.txt',
            'vendor/unidecode_LICENSE.txt',
            'vendor/wcwidth_LICENSE.txt',
            'vendor/yaml_LICENSE.txt',
        ],
    },
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=[
        # NOTE: Run 'apt install python3-magic' on Debian-derivatives to satisfy the magic dependency.
        # 'python3-magic',   TODO: Which version is actually used??
    ],
    tests_require=[
        # TODO: Move 'hypothesis' to dev-requirements
        'hypothesis==3.38.0',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'autonameow = main:cli_main',
            'meowxtract = extract:cli_main',
        ]
    }
)
