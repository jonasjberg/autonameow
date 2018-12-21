`autonameow`
------------
Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>  
Source repository: <https://github.com/jonasjberg/autonameow>

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
>     * `pandoc`
>     * `pdftotext`
>     * `unrtf`
>     * `jpeginfo`
>     * `djvutxt`
>
> 2. Run `bin/autonameow --help`
> 3. Run `bin/meowxtract.sh --help`
> 4. Run `bin/autonameow --dry-run --timid --verbose PATH/TO/FILE.txt`
> 5. Be *NOT VERY HAPPY* about lack of documentation; offer to help out
>    somehow, __or wait for v1.0.0__


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


Instructions for MacOS
----------------------

### Installing Python 3
`autonameow` is developed exclusively for Python 3 and will __NOT__ run with
Python 2.

Install Python using `homebrew`:

```bash
brew install python3
```

Installing `homebrew` itself is out of scope of this guide.
There is a [lot][2] [of][3] [information][4] available online.

Check that your version of Python 3 is `v3.5.0` or newer:

```bash
python3 --version
```

### Installing the Dependencies
Install the dependencies by running the following commands in a terminal:

```bash
brew install libmagic exiftool tesseract unrtf pandoc jpeginfo djvulibre
brew install poppler # pdftotext
```


Instructions for Linux
----------------------

### Installing Python 3
`autonameow` is developed exclusively for Python 3 and will __NOT__ run with
Python 2.

Most distributions ship with Python 3.x by default.
Assuming you use `apt` for package management, run the following command to
check and install if missing:

```bash
which python3 || sudo apt-get install python3
```

Check that your version of Python 3 is `v3.5.0` or newer:

```bash
python3 --version
```


### Installing the Dependencies
Install the dependencies by running the following commands in a terminal:

```bash
sudo apt install exiftool tesseract-ocr pdftotext unrtf pandoc jpeginfo djvutxt
```


Instructions for Windows
------------------------
The `autonameow` project does not target any version of Windows.  Getting it
running should not be all too difficult, the core `autonameow` code should run
just fine on Windows.

It unsurprisingly seems to run pretty well in WSL.
Get [Windows WSL][5] and follow the Linux instructions above.

Verified "native" Windows compatibility *might* be included at some later time.


[1]: https://github.com/jonasjberg/autonameow
[2]: https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-macos
[3]: https://wsvincent.com/install-python3-mac/
[4]: https://www.python.org/downloads/mac-osx/
[5]: https://docs.microsoft.com/en-us/windows/wsl/install-win10
