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

from . import sexp
from .sexp import car

_bom_fields = ['qty','refs', 'description', 'package', 'manufacturer', 'MPN']


def main():
    from sys import argv, stdout
    from csv import DictWriter
    data = car(sexp.load(open(argv[1])))
    comps = comps_from_netlist(data)
    bom = bom_from_comps(comps)
    of = open(argv[2], 'w')
    bom_writer = DictWriter(of, fieldnames=_bom_fields,
                            extrasaction='ignore')
    bom_writer.writeheader()
    for b in bom:
        bom_writer.writerow(b)

if __name__ == "__main__":
    main()