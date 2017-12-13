# Bom tool
#
# Copyright (c) 2016 Jose I Romero

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from .bomtool import comps_from_netlist, bom_from_comps
from .xyrstool import do_xyrs

from . import sexp
from .sexp import car

_bom_fields = ['qty','refs', 'description', 'package', 'manufacturer', 'MPN']

_xyrs_fields = ['Designator', 'X-Loc', 'Y-Loc', 'Rotation', 'Side', 'Type', 'X-Size', 'Y-Size', 'Value', 'Footprint', 'Populate', 'MPN']

def main():
    from sys import argv, stdout
    from csv import DictWriter, excel_tab
    net_data = car(sexp.load(open(argv[1])))
    pcb_data = car(sexp.load(open(argv[2])))
    
    comps = comps_from_netlist(net_data)
    bom = bom_from_comps(comps)
    bof = open(argv[3], 'w')
    bom_writer = DictWriter(bof, fieldnames=_bom_fields,
                            extrasaction='ignore')
    bom_writer.writeheader()
    for b in bom:
        bom_writer.writerow(b)

    xyrs = do_xyrs(pcb_data, comps)
    xof = open(argv[4], 'w')
    xyrs_writer = DictWriter(xof, fieldnames=_xyrs_fields, dialect=excel_tab,
                             extrasaction='ignore')
    xyrs_writer.writeheader()
    for r in xyrs:
        xyrs_writer.writerow(r)

if __name__ == "__main__":
    main()
