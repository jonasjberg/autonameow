`autonameow`
------------
*Copyright(c) 2016-2017 Jonas Sjöberg*  
<https://github.com/jonasjberg>  
<http://www.jonasjberg.com>  
University mail: `js224eh[a]student.lnu.se`  

--------------------------------------------------------------------------------


Installation Instructions
=========================
These are the __temporary__ installation instructions to get the project
running __in its current state__.  

Simplifying the installation procedure for both users and developers is a
critical `TODO`-list item.

TL;DR
-----

1. Install these executables:

    * `python3` (3.x)
    * `libmagic`
    * `exiftool`
    * `tesseract`

2. Install these Python modules:

    * `chardet`
    * `colorama`
    * `python-dateutil`
    * `unidecode`
    * `PyPDF2`
    * `pytesseract`
    * `python-magic`
    * `pytz`


3. Optionally, install additional 3rd party software ("plugins"):

    * `guessit`


Instructions for MacOS
----------------------
First install `python3`, I prefer using `homebrew` but either way is fine as
long as this command prints "`OK`":

```bash
command -v python3 2>&1 >/dev/null && echo OK
```

Next, make sure you can execute `pip3`; the package manager that will be used
to install the project dependencies. Also note that `homebrew` is used to
install the non-Python dependencies.

### Installing the Dependencies
Install the dependencies by running the following commands in a terminal:

```bash
brew install libmagic exiftool tesseract
pip3 install chardet colorama python-dateutil unidecode PyPDF2 pytesseract python-magic pytz
```

### Installing __optional__ third-party software
You might want to install additional __optional__ third-party components:

```bash
pip3 install guessit
```


Instructions for Linux
----------------------
First make sure `python3` is installed. Most distributions ship with Python 3.x
by default. Assuming you use `apt` for package management, run the following
command to check and install if missing:

```bash
which python3 || sudo apt-get install python3
```

*(If you use something else then `apt`, you probably already know what to do..)*

### Installing the Dependencies
Install the dependencies by running the following commands in a terminal:

```bash
apt install exiftool tesseract-ocr
pip3 install chardet colorama python-dateutil unidecode PyPDF2 pytesseract python-magic pytz
```

Alternatively, search the repositories for the packages with `apt-search`.
Make sure to install the `python3-PACKAGE_NAME` versions, most packages are
available for both `python2` and `python3`.

### Installing __optional__ third-party software
You might want to install additional __optional__ third-party components:

```bash
pip3 install guessit
```


Instructions for Windows
------------------------
The `autonameow` project does not target any version of Windows.  Getting it
running should not be all too difficult, the core `autonameow` code should run
just fine on Windows.

However, and this is a significantly important however;  
The code has *never* been tested on Windows --- __you are on your own!__


Verified Windows compatibility *might* be included at some later time.
