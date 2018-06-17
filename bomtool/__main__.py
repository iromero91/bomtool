# Bom tool
#
# Copyright (c) 2016-2018 Jose I Romero

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

from .bomtool import load_netlist, generate_bom, write_bom_csv
from .xyrstool import generate_xyrs, write_xyrs_tsv


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Create Bills of Materials from KiCad netlist files")
    parser.add_argument("netlist", help="Netlist to process")
    parser.add_argument("pcb", help="PCB File (used for XYRS)", nargs='?')
    parser.add_argument("--xyrs", help="Output XYRS format", type=str, metavar="FILE")
    parser.add_argument("--bom", help="Output BOM in csv format", type=str, metavar="FILE")
    args = parser.parse_args()

    if not args.xyrs and not args.bom:
        parser.error("No task specified")
    elif args.xyrs and not args.pcb:
        parser.error("A PCB file is needed when generating XYRS")

    try:
        netlist = load_netlist(open(args.netlist))
    except Exception as e:
        parser.error("Error loading netlist '{}': {}".format(args.netlist, str(e)))

    bom = generate_bom(netlist)
    if args.bom:
        try:
            bom_file = open(args.bom, 'w')
            write_bom_csv(bom, bom_file)
        except Exception as e:
            parser.error("Error writing BOM file '{}': {}".format(args.bom, str(e)))

    if args.xyrs:
        try:
            xyrs = generate_xyrs(open(args.pcb), bom)
        except Exception as e:
            parser.error("Error parsing PCB '{}': {}".format(args.pcb, str(e))) 
        try:
            write_xyrs_tsv(xyrs, open(args.xyrs, 'w'))
        except Exception as e:
            parser.error("Error writing XYRS file '{}': {}".format(args.xyrs, str(e)))

if __name__ == "__main__":
    main()
