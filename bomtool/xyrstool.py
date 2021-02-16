# -*- coding: utf-8 -*-
# Macrofab XYRS tool
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

from . import sexp
from .sexp import car, cdr, cadr, findall, assoc

import re
import logging

from csv import DictWriter, excel_tab

def parse_module(data):
    m = {}
    layer = cadr(assoc(data, 'layer'))
    if layer == "F.Cu":
        m['side'] = 1
    else:
        m['side'] = 2
    texts = findall(data, 'fp_text')
    for t in texts:
        if t[1] == 'reference':
            m['ref'] = t[2]
    xyrot = assoc(data, 'at')
    if xyrot:
        m['xpos'] = float(xyrot[1])
        m['ypos'] = float(xyrot[2])
        if len(xyrot) == 4:
            m['rot'] = float(xyrot[3])
        else:
            m['rot'] = 0.0
    lines = (l for l in findall(data, 'fp_line') if 'CrtYd' in cadr(assoc(l, 'layer')))
    max_x, max_y = 0, 0
    min_x, min_y = 0, 0
    for line in lines:
        start = assoc(line, 'start')
        end = assoc(line, 'end')
        for point in (start, end):
            x = float(point[1])
            y = float(point[2])
            if x < min_x: min_x = x
            if y < min_y: min_y = y
            if x > max_x: max_x = x
            if y > max_y: max_y = y
    m["size_x"] = 2*min(max_x, -min_x)
    m["size_y"] = 2*min(max_y, -min_y)
    return m


def generate_xyrs(pcb_file, bom):
    pcb_data = car(sexp.load(pcb_file))
    raw_modules = list(findall(pcb_data, 'module'))
    modules = [parse_module(m) for m in raw_modules]
    xyrs = []
    for m in modules:
        #XXX Discard virtual components earlier!
        xyrs_line = {}
        bomline = None
        for line in bom:
            if m.get('ref', '') in line['refs'].split(', '):
                bomline = line
                break
        if not bomline:
            logging.warning(
                "Component '{}' not in the BOM."
                .format(m['ref']))
        else:
            xyrs_line['#Designator'] = m.get('ref', '')
            xyrs_line['X-Loc'] = round(m.get('xpos', 0.0) / 0.0254, 2) #XXX the board lower X bound must be added
            xyrs_line['Y-Loc'] = -round(m.get('ypos', 0.0) / 0.0254, 2) # XXX the board upper Y bound must be added
            xyrs_line['Rotation'] = m.get('rot', 0)
            xyrs_line['Side'] = m.get('side', 1)
            xyrs_line['Type'] = 1 # XXX implement properly (read attr smd?)
            xyrs_line['X-Size'] = round(m.get('size_x', 0.0) / 0.0254,2)
            xyrs_line['Y-Size'] = round(m.get('size_y', 0.0) / 0.0254,2)
            xyrs_line['Value'] = bomline['description']
            xyrs_line['Footprint'] = bomline.get('package', '')
            xyrs_line['Populate'] = 1 if bomline['qty'] != "DO NOT POPULATE" else 0
            xyrs_line['MPN'] = bomline.get('MPN', '')
            xyrs.append(xyrs_line)
    return xyrs

_xyrs_fields = ['#Designator', 'X-Loc', 'Y-Loc', 'Rotation', 'Side', 'Type', 'X-Size', 'Y-Size', 'Value', 'Footprint', 'Populate', 'MPN']

def write_xyrs_tsv(xyrs, xyrs_file):
    xyrs_writer = DictWriter(xyrs_file, fieldnames=_xyrs_fields, dialect=excel_tab,
                             extrasaction='ignore')
    xyrs_writer.writeheader()
    for r in xyrs:
        xyrs_writer.writerow(r)
