`autonameow`
============
*Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>*  
Source repository: <https://github.com/jonasjberg/autonameow>

--------------------------------------------------------------------------------

Vendoring Dependencies
======================
Notes on attempt at including all dependencies in the main repository.

#### Revisions
* 2018-12-07 --- `jonasjberg` Initial.
* 2018-12-21 --- `jonasjberg` Updates.




Notes
-----

Download packages listed in `requirements.txt` to the directory `DESTDIR` as `.tar.gz`-files:

```bash
pip install --download DESTDIR -r requirements.txt --no-binary :all:
```

Extract downloaded `.tar.gz`-files:

```bash
cd DESTDIR && for f in *.tar.gz ; do [ -d "${f%.tar.gz}" ] && continue ; tar -xf "$f" ; done
```

Then run ad-hoc hack script `modify_extracted_pip_archives.sh`.



See also
--------

- <https://github.com/pypa/pip/blob/master/src/pip/_vendor/README.rst>
- <https://github.com/pypa/pip/blob/master/tasks/vendoring/__init__.py>
