`autonameow`
------------
*Copyright(c) 2016-2018 Jonas Sjöberg*  
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

### TL;DR

> 1. Install these executables:
>
>     * `python3` (3.x)
>     * `libmagic`
>     * `exiftool`
>     * `tesseract`
>     * `pdftotext`
>     * `unrtf`
>
> 2. Install these Python modules:
>
>     * `chardet`
>     * `colorama`
>     * `unidecode`
>     * `prompt_toolkit`
>     * `file-magic`
>     * `pytz`
>     * `pyyaml`
>
> 3. Optionally, install additional 3rd party software ("plugins"):
>
>     * `guessit`
>
> 4. Make sure to fetch all Git submodules:
>
>     ```bash
>     git submodule update --init --recursive
>     ```


Getting the sources
-------------------
Grab the sources from the [autonameow GitHub page][1].

Using SSH:
```bash
git clone git@github.com:jonasjberg/autonameow.git
```

Alternatively, using HTTPS:
```bash
git clone https://github.com/jonasjberg/autonameow.git
```

Then initialize all Git submodules:
```bash
git submodule update --init --recursive
```

Make sure to run this command in the directory containing the
`autonameow` sources you just downloaded.


Installing Python 3
-------------------
`autonameow` is developed exclusively for Python 3 and will __NOT__ run with
Python 2.

### Instructions for MacOS
Installing Python using `homebrew`:
```bash
brew install python3
```

Installing `homebrew` itself is out of scope of this guide.
There is a [lot][2] [of][3] [information][4] available online.

Just make sure that this command prints "`OK`":
```bash
command -v python3 2>&1 >/dev/null && echo OK
```

### Instructions for Linux
Most distributions ship with Python 3.x by default.
Assuming you use `apt` for package management, run the following command to
check and install if missing:

```bash
which python3 || sudo apt-get install python3
```


Installing the Dependencies
---------------------------

### Instructions for MacOS
Make sure you can execute `pip3`, which is the package manager that will be
used to install the project dependencies. Also note that `homebrew` is used to
install the non-Python dependencies.

Install the dependencies by running the following commands in a terminal:
```bash
brew install libmagic exiftool tesseract unrtf
brew install poppler # pdftotext
pip3 install chardet colorama unidecode prompt_toolkit file-magic pytz pyyaml
```

You might also want to install additional __optional__ third-party components:
```bash
pip3 install guessit
```

### Instructions for Linux
Install the dependencies by running the following commands in a terminal:

```bash
sudo apt install exiftool tesseract-ocr pdftotext unrtf
pip3 install chardet colorama unidecode prompt_toolkit file-magic pytz pyyaml
```

Alternatively, search the repositories for the packages with `apt-search`.
Make sure to install the `python3-PACKAGE_NAME` versions, many packages are
available as separate `python2` and `python3` versions.

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



[1]: https://github.com/jonasjberg/autonameow
[2]: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-macos
[3]: https://wsvincent.com/install-python3-mac/
[4]: https://www.python.org/downloads/mac-osx/
