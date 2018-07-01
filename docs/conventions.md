`autonameow`
============
*Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>*  
<https://github.com/jonasjberg/autonameow>  
<http://www.jonasjberg.com>  

--------------------------------------------------------------------------------

Conventions used by `autonameow`
================================
Various conventions used in the `autonameow` project.

NOTE: This is still a work in progress!
Should be prioritized if other developers become involved with the project.


File/path-names
----------------
The following naming conventions are used in the source code, originating
primarily from the `FileObject` class.


Given the path `/home/gibson/foo.txt`:

```
Name               Value
=================================================
abspath          : /home/gibson/Documents/foo.txt
pathname         : /home/gibson/Documents
pathparent       :              Documents
filename         :                        foo.txt
basename_prefix  :                        foo
basename_suffix  :                            txt
```


The most obvious deviation from de-facto standards is the treatment of file
extensions.


Given the path `/home/gibson/foo.tar.gz`:

```
Name               Value
====================================================
abspath          : /home/gibson/Documents/foo.tar.gz
pathname         : /home/gibson/Documents
pathparent       :              Documents
filename         :                        foo.tar.gz
basename_prefix  :                        foo
basename_suffix  :                            tar.gz
```



<!-- TODO: Document naming convention for mapping converting extensions to MIME-types. -->

Imports
-------
Imports should follow the top-level license header.

Example:
```
#                       ... LICENSE GOES HERE ...
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from unittest import skipIf, TestCase

try:
    import yaml
except ImportError:
    yaml = None
    print('Missing required module "yaml". '
          'Make sure "pyyaml" is available before running this program.',
          file=sys.stderr)

import unit_utils as uu
import unit_utils_constants as uuconst
from core import constants as C
from core import exceptions
from core.config.configuration import Configuration
from core.config.default_config import DEFAULT_CONFIG
from util import encoding as enc


first_line_of_code = 'is separated from imports with two blank lines'
```


### Import-statement Grouping
Imports are divided into three "groups":

1. Standard library
2. Third-party or potentially unavailable.
3. Project-specific

Example:
```python
import os                    #  1. Standard library

try:                         #  2.
    import yaml              #  Third-party
except ImportError:          #  and/or/maybe
    yaml = None              #  potentially unavailable

from core import exceptions  #  3. Project-specific
```

Statements with multiple clauses should be split up into separate lines, like this;
```python
from core import exceptions
from core import version
```
__Not like this;__
```python
from core import exceptions, version
```
And __not like this;__
```python
from core import (
    exceptions,
    version
)
```

This is motivated primarily by cleaner diffs and merges.
Note that imports of testing functionality are exempt and can be written on a
single line.



### Blank Lines

* One blank line before the imports.
* Two blank lines after the imports.
* One blank line between import groups


### Import-statement Ordering
Imports should be ordered first by *"form"*; E.G. `import core`
goes before `from core import thing`. And then lexicographically.

Refer to above examples.


### Module/package Imports
This is a lot less strict and still partly undecided.


#### Unit Test Code
Unit test code should import each function directly, if possible.

* Use `from util.text.thing import foo`.

__Do not__ do `import util.text.thing` and then write `thing.foo` everywhere.
It makes refactoring more difficult, especially moving stuff between files.

Bind shared utilities to shorthands;

* Import `unit_utils.py` like `import unit_utils as uu`
* Import `unit_utils_constants.py` like `import unit_utils_constants as uuconst`

__TODO: INCOMPLETE!__


#### Core Code
Bind shared utilities to shorthands;

* Import `constants.py` like `from core import constants as C`
* Import `unit_utils_constants.py` like `import unit_utils_constants as uuconst`


__TODO: INCOMPLETE!__


Test Code
---------

### Assertions
Calls to assertions with unordered parameters should pass the argument with the
__expected value first__.

Example:
```python
assertEqual(expect, actual)
```
