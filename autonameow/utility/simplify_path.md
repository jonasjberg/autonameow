simplify_path

Description:
------------
Given a full path, suggest a simplified alternative by identifying and
combining repeating patterns. No information should be less, with some
exceptions; text case and delimiter tokens.


Example:
--------

### Folder contents:

```
spock@ProBook-6465b ~/projects/zvex_fuzz-factory/hardware/eagle/alternatives
> $ ls
zvex-fuzz-factory-1590B-perfboard-2.brd
zvex-fuzz-factory-1590B-perfboard-2_PCB.png
zvex-fuzz-factory-1590B-perfboard-2.sch
zvex-fuzz-factory-1590B-perfboard-2_SCHEMATIC.png
zvex-fuzz-factory-1590B-perfboard-2.sch.png
zvex-fuzz-factory-1590B-perfboard-2.tar.bz2
zvex-fuzz-factory-1590B-perfboard-3.brd
zvex-fuzz-factory-1590B-perfboard-3_PCB.png
zvex-fuzz-factory-1590B-perfboard-3.sch
zvex-fuzz-factory-1590B-perfboard-3_SCHEMATIC.png
zvex-fuzz-factory-1590B-perfboard-3.sch.png
zvex-fuzz-factory-1590B-perfboard-3.tar.bz2
zvex-fuzz-factory-1590B-perfboard.brd
zvex-fuzz-factory-1590B-perfboard_PCB.png
zvex-fuzz-factory-1590B-perfboard.sch
zvex-fuzz-factory-1590B-perfboard_SCHEMATIC.png
zvex-fuzz-factory-1590B-perfboard.sch.png
zvex-fuzz-factory-1590B-perfboard.tar.bz2
zvex-fuzz-factory-5-rattar-1590B.brd
zvex-fuzz-factory-5-rattar-1590B_PCB.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort.brd
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS.brd
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS_PCB.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS.sch
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS_SCHEMATIC.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS.sch.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS.tar.bz2
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort_PCB.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass-2.brd
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass-2_PCB.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass-2.sch
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass-2.tar.bz2
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass.brd
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass_PCB.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass.sch
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass_SCHEMATIC.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass.sch.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass.tar.bz2
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort.sch
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort_SCHEMATIC.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort.sch.png
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort.tar.bz2
zvex-fuzz-factory-5-rattar-1590B.sch
zvex-fuzz-factory-5-rattar-1590B_SCHEMATIC.png
zvex-fuzz-factory-5-rattar-1590B.sch.png
zvex-fuzz-factory-5-rattar-1590B.tar.bz2
zvex-fuzz-factory-ETS.brd
zvex-fuzz-factory-ETS_PCB.png
zvex-fuzz-factory-ETS.sch
zvex-fuzz-factory-ETS_SCHEMATIC.png
zvex-fuzz-factory-ETS.sch.png
zvex-fuzz-factory-ETS.tar.bz2
zvex-fuzz-factory-FAKTISKT-BYGGE_PCB.png
zvex-fuzz-factory-FAKTISKT-BYGGE.sch.png
zvex-fuzz-factory-FAKTISKT-BYGGE.tar.bz2
zvex-fuzz-factory-w-mods.brd
zvex-fuzz-factory-w-mods_PCB.png
zvex-fuzz-factory-w-mods.sch
zvex-fuzz-factory-w-mods_SCHEMATIC.png
zvex-fuzz-factory-w-mods.sch.png
zvex-fuzz-factory-w-mods.tar.bz2
zvex-fuzz-factory-w-oscillation-cancellation.brd
zvex-fuzz-factory-w-oscillation-cancellation_PCB.png
zvex-fuzz-factory-w-oscillation-cancellation.sch
zvex-fuzz-factory-w-oscillation-cancellation_SCHEMATIC.png
zvex-fuzz-factory-w-oscillation-cancellation.sch.png
zvex-fuzz-factory-w-oscillation-cancellation.tar.bz2
```


###  Strip extensions and remove duplicate entries.

```
spock@ProBook-6465b ~/projects/zvex_fuzz-factory/hardware/eagle/alternatives
> $ for file in *; do echo "${file%%.*}"; done | sort -u | xclip -i -selection c
zvex-fuzz-factory-1590B-perfboard
zvex-fuzz-factory-1590B-perfboard-2
zvex-fuzz-factory-1590B-perfboard-2_PCB
zvex-fuzz-factory-1590B-perfboard-2_SCHEMATIC
zvex-fuzz-factory-1590B-perfboard-3
zvex-fuzz-factory-1590B-perfboard-3_PCB
zvex-fuzz-factory-1590B-perfboard-3_SCHEMATIC
zvex-fuzz-factory-1590B-perfboard_PCB
zvex-fuzz-factory-1590B-perfboard_SCHEMATIC
zvex-fuzz-factory-5-rattar-1590B
zvex-fuzz-factory-5-rattar-1590B_PCB
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS_PCB
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-ETS_SCHEMATIC
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort_PCB
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass-2
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass-2_PCB
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass_PCB
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort-relay-bypass_SCHEMATIC
zvex-fuzz-factory-5-rattar-1590B-pottar-under-kort_SCHEMATIC
zvex-fuzz-factory-5-rattar-1590B_SCHEMATIC
zvex-fuzz-factory-ETS
zvex-fuzz-factory-ETS_PCB
zvex-fuzz-factory-ETS_SCHEMATIC
zvex-fuzz-factory-FAKTISKT-BYGGE
zvex-fuzz-factory-FAKTISKT-BYGGE_PCB
zvex-fuzz-factory-w-mods
zvex-fuzz-factory-w-mods_PCB
zvex-fuzz-factory-w-mods_SCHEMATIC
zvex-fuzz-factory-w-oscillation-cancellation
zvex-fuzz-factory-w-oscillation-cancellation_PCB
zvex-fuzz-factory-w-oscillation-cancellation_SCHEMATIC
```

### Remove first part, common to all entries.
Common part `zvex-fuzz-factory` should be made part of the path name 
instead of individual file names.
Lets say all files were to be moved to a new shared root directory,
not shown below for clarity.

```
1590B-perfboard-2.brd
1590B-perfboard-2_PCB.png
1590B-perfboard-2.sch
1590B-perfboard-2_SCHEMATIC.png
1590B-perfboard-2.sch.png
1590B-perfboard-2.tar.bz2
1590B-perfboard-3.brd
1590B-perfboard-3_PCB.png
1590B-perfboard-3.sch
1590B-perfboard-3_SCHEMATIC.png
1590B-perfboard-3.sch.png
1590B-perfboard-3.tar.bz2
1590B-perfboard.brd
1590B-perfboard_PCB.png
1590B-perfboard.sch
1590B-perfboard_SCHEMATIC.png
1590B-perfboard.sch.png
1590B-perfboard.tar.bz2
5-rattar-1590B.brd
5-rattar-1590B_PCB.png
5-rattar-1590B-pottar-under-kort.brd
5-rattar-1590B-pottar-under-kort-ETS.brd
5-rattar-1590B-pottar-under-kort-ETS_PCB.png
5-rattar-1590B-pottar-under-kort-ETS.sch
5-rattar-1590B-pottar-under-kort-ETS_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort-ETS.sch.png
5-rattar-1590B-pottar-under-kort-ETS.tar.bz2
5-rattar-1590B-pottar-under-kort_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass-2.brd
5-rattar-1590B-pottar-under-kort-relay-bypass-2_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass-2.sch
5-rattar-1590B-pottar-under-kort-relay-bypass-2.tar.bz2
5-rattar-1590B-pottar-under-kort-relay-bypass.brd
5-rattar-1590B-pottar-under-kort-relay-bypass_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass.sch
5-rattar-1590B-pottar-under-kort-relay-bypass_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort-relay-bypass.sch.png
5-rattar-1590B-pottar-under-kort-relay-bypass.tar.bz2
5-rattar-1590B-pottar-under-kort.sch
5-rattar-1590B-pottar-under-kort_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort.sch.png
5-rattar-1590B-pottar-under-kort.tar.bz2
5-rattar-1590B.sch
5-rattar-1590B_SCHEMATIC.png
5-rattar-1590B.sch.png
5-rattar-1590B.tar.bz2
ETS.brd
ETS_PCB.png
ETS.sch
ETS_SCHEMATIC.png
ETS.sch.png
ETS.tar.bz2
FAKTISKT-BYGGE_PCB.png
FAKTISKT-BYGGE.sch.png
FAKTISKT-BYGGE.tar.bz2
w-mods.brd
w-mods_PCB.png
w-mods.sch
w-mods_SCHEMATIC.png
w-mods.sch.png
w-mods.tar.bz2
w-oscillation-cancellation.brd
w-oscillation-cancellation_PCB.png
w-oscillation-cancellation.sch
w-oscillation-cancellation_SCHEMATIC.png
w-oscillation-cancellation.sch.png
w-oscillation-cancellation.tar.bz2
```


### Identify new directories from common parts.

```
1590B-perfboard-2.brd
1590B-perfboard-2_PCB.png
1590B-perfboard-2.sch
1590B-perfboard-2_SCHEMATIC.png
1590B-perfboard-2.sch.png
1590B-perfboard-2.tar.bz2

1590B-perfboard-3.brd
1590B-perfboard-3_PCB.png
1590B-perfboard-3.sch
1590B-perfboard-3_SCHEMATIC.png
1590B-perfboard-3.sch.png
1590B-perfboard-3.tar.bz2

1590B-perfboard.brd
1590B-perfboard_PCB.png
1590B-perfboard.sch
1590B-perfboard_SCHEMATIC.png
1590B-perfboard.sch.png
1590B-perfboard.tar.bz2

5-rattar-1590B.brd
5-rattar-1590B_PCB.png
5-rattar-1590B.sch
5-rattar-1590B_SCHEMATIC.png
5-rattar-1590B.sch.png
5-rattar-1590B.tar.bz2

5-rattar-1590B-pottar-under-kort.brd
5-rattar-1590B-pottar-under-kort-ETS.brd
5-rattar-1590B-pottar-under-kort-ETS_PCB.png
5-rattar-1590B-pottar-under-kort-ETS.sch
5-rattar-1590B-pottar-under-kort-ETS_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort-ETS.sch.png
5-rattar-1590B-pottar-under-kort-ETS.tar.bz2
5-rattar-1590B-pottar-under-kort_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass-2.brd
5-rattar-1590B-pottar-under-kort-relay-bypass-2_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass-2.sch
5-rattar-1590B-pottar-under-kort-relay-bypass-2.tar.bz2
5-rattar-1590B-pottar-under-kort-relay-bypass.brd
5-rattar-1590B-pottar-under-kort-relay-bypass_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass.sch
5-rattar-1590B-pottar-under-kort-relay-bypass_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort-relay-bypass.sch.png
5-rattar-1590B-pottar-under-kort-relay-bypass.tar.bz2
5-rattar-1590B-pottar-under-kort.sch
5-rattar-1590B-pottar-under-kort_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort.sch.png
5-rattar-1590B-pottar-under-kort.tar.bz2

ETS.brd
ETS_PCB.png
ETS.sch
ETS_SCHEMATIC.png
ETS.sch.png
ETS.tar.bz2

FAKTISKT-BYGGE_PCB.png
FAKTISKT-BYGGE.sch.png
FAKTISKT-BYGGE.tar.bz2

w-mods.brd
w-mods_PCB.png
w-mods.sch
w-mods_SCHEMATIC.png
w-mods.sch.png
w-mods.tar.bz2

w-oscillation-cancellation.brd
w-oscillation-cancellation_PCB.png
w-oscillation-cancellation.sch
w-oscillation-cancellation_SCHEMATIC.png
w-oscillation-cancellation.sch.png
w-oscillation-cancellation.tar.bz2
```


### Identify new directories from common parts ..

```
1590B-perfboard-2.brd
1590B-perfboard-2_PCB.png
1590B-perfboard-2.sch
1590B-perfboard-2_SCHEMATIC.png
1590B-perfboard-2.sch.png
1590B-perfboard-2.tar.bz2

1590B-perfboard-3.brd
1590B-perfboard-3_PCB.png
1590B-perfboard-3.sch
1590B-perfboard-3_SCHEMATIC.png
1590B-perfboard-3.sch.png
1590B-perfboard-3.tar.bz2

1590B-perfboard.brd
1590B-perfboard_PCB.png
1590B-perfboard.sch
1590B-perfboard_SCHEMATIC.png
1590B-perfboard.sch.png
1590B-perfboard.tar.bz2

5-rattar-1590B.brd
5-rattar-1590B_PCB.png
5-rattar-1590B.sch
5-rattar-1590B_SCHEMATIC.png
5-rattar-1590B.sch.png
5-rattar-1590B.tar.bz2

5-rattar-1590B-pottar-under-kort.brd
5-rattar-1590B-pottar-under-kort-ETS.brd
5-rattar-1590B-pottar-under-kort-ETS_PCB.png
5-rattar-1590B-pottar-under-kort-ETS.sch
5-rattar-1590B-pottar-under-kort-ETS_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort-ETS.sch.png
5-rattar-1590B-pottar-under-kort-ETS.tar.bz2
5-rattar-1590B-pottar-under-kort_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass-2.brd
5-rattar-1590B-pottar-under-kort-relay-bypass-2_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass-2.sch
5-rattar-1590B-pottar-under-kort-relay-bypass-2.tar.bz2
5-rattar-1590B-pottar-under-kort-relay-bypass.brd
5-rattar-1590B-pottar-under-kort-relay-bypass_PCB.png
5-rattar-1590B-pottar-under-kort-relay-bypass.sch
5-rattar-1590B-pottar-under-kort-relay-bypass_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort-relay-bypass.sch.png
5-rattar-1590B-pottar-under-kort-relay-bypass.tar.bz2
5-rattar-1590B-pottar-under-kort.sch
5-rattar-1590B-pottar-under-kort_SCHEMATIC.png
5-rattar-1590B-pottar-under-kort.sch.png
5-rattar-1590B-pottar-under-kort.tar.bz2

ETS.brd
ETS_PCB.png
ETS.sch
ETS_SCHEMATIC.png
ETS.sch.png
ETS.tar.bz2

FAKTISKT-BYGGE_PCB.png
FAKTISKT-BYGGE.sch.png
FAKTISKT-BYGGE.tar.bz2

w-mods.brd
w-mods_PCB.png
w-mods.sch
w-mods_SCHEMATIC.png
w-mods.sch.png
w-mods.tar.bz2

w-oscillation-cancellation.brd
w-oscillation-cancellation_PCB.png
w-oscillation-cancellation.sch
w-oscillation-cancellation_SCHEMATIC.png
w-oscillation-cancellation.sch.png
w-oscillation-cancellation.tar.bz2
```


