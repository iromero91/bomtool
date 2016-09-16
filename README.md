# BOM tool

This is a work in progress script to create beautiful Bills of
Materials from KiCad netlist files.

# How to use

To make use of this tool, every component in the schematic must have a
`BOM` field with a specific format (see below). Components that are in
the schematic but do not have a corresponding BOM item (like solder
jumpers, net ties, mounting holes) should have their `BOM` field to
`VIRTUAL`. Components with missing `BOM` items will be marked with a
"!!MISSING!!" tag in the description and the script will show a
warning.

Right now the script just outputs a fixed format CSV file, after
grouping, counting and filling every BOM line the best it can from the
available data. To call it you first need to export a netlist from
eeschema and then call the script like this:

    $ python3 -m bomtool myproject.net myproject-bom.csv

# Installation

To install bomtool you can do it in a virtualenv

    $ mkvirtualenv bomtool
    $ workon bomtool
    (bomtool)$ pip install --editable .
    
After that you can run the code from anywhere with the "bomtool"
command.

# BOM format

## Multiple items

For components that need multiple bom items (say, assemblies, battery
holders with their batteries, jumper headers and links) you can
combine as many BOM lines as you need, separating them with a
semicolon (;), for example:

    HOLDER MPD BU2032; BATTERY CR2032
    (3) CONN MILL-MAX 0364-0-15-01-13-27-10-0; IC CITY ECO-SURE

In the second case there is another special field, a number in
parentheses at the beginning of the line (`(3)`). That number acts as a
multiplier, the script will multiply that by the amount of components
calling out that BOM line.

## Packages

At the end of the BOM line you can specify the package name of that
item as a name in square brackets, like `[0603]` refers to the
imperial 0603 package (1608 Metric). To avoid confusion, if you wish
to specify metric package sizes, add an 'm' at the end, like
`[1608m]`. 

In the near future I plan to implement a cross check with the
footprint field in the symbol, to ensure they match.

## Specific parts

For all kinds of parts it's allowed to specify a manufacturer and/or part
number directly, for example:

    RES VISHAY AC03000001008JAC00
    IC TI LMV761MF [SOT-23-6]
    IC NE555 [DIP-8]
    
For certain "Jellybean" components it's possible to specify
_parameters_, which (in the future) will enable a parametric search of
candidates to fill the specific manufacturer and part number
fields. 

Those parameters are listed in the following sections:

## Resistors

Examples:

    RES SMD 1k 5% [0603]
    RES AXIAL 1k 5% 0.25W

Fields: TODO

## Capacitors

Examples:

    CAP MLCC 100nF X7R [0603]
    CAP TANT 3.3µF 10% 16V [AVX-B]

Fields: TODO

## Beads

Examples:

    BEAD SMD 100 @120Mhz [0402]

Fields: TODO

# License

Copyright (c) 2016 Jose I Romero

All this code is licensed under the MIT license, see the LICENSE file
for more details.
