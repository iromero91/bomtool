# -*- coding: utf-8 -*-
# Macrofab XYRS tool
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

from .sexp import car, cdr, cadr, findall, assoc

from . import pngen

from .bomtool import parse_bomline

import re
import logging
from collections import defaultdict


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


def do_xyrs(data, comps):
    raw_modules = list(findall(data, 'module'))
    modules = [parse_module(m) for m in raw_modules]
    xyrs = []
    for m in modules:
        xyrs_line = {}
        comp = None
        for c in comps:
            if c.get('ref', 'SOFTDOG') == m.get('ref', 'NOSAME'):
                comp = c
                break
        if not comp:
            logging.error("Component '{}' missing in netlist!".format(m['ref']))
        elif comp.get('BOM', '') == '':
            logging.error("Component '{}' has no BOM line!".format(comp['ref']))
        elif comp['BOM'] == 'VIRTUAL':
            logging.warning(
                "Component '{}' is VIRTUAL, will be excluded from the BOM."
                .format(comp['ref']))
        else:
            bomline = parse_bomline(comp['BOM'])[0]
            qty = bomline.get('mult', 1)
            xyrs_line['Designator'] = m.get('ref', '')
            xyrs_line['X-Loc'] = round(m.get('xpos', 0.0) / 0.0254, 2) #XXX the board lower X bound must be added
            xyrs_line['Y-Loc'] = -round(m.get('ypos', 0.0) / 0.0254, 2) # XXX the board upper Y bound must be added
            xyrs_line['Rotation'] = m.get('rot', 0)
            xyrs_line['Side'] = m.get('side', 1)
            xyrs_line['Type'] = 1 # XXX implement properly (read attr smd?)
            xyrs_line['X-Size'] = round(m.get('size_x', 0.0) / 0.0254,2)
            xyrs_line['Y-Size'] = round(m.get('size_y', 0.0) / 0.0254,2)
            xyrs_line['Value'] = bomline.get('description', '')
            xyrs_line['Footprint'] = bomline.get('package','')
            xyrs_line['Populate'] = 1 if qty else 0
            xyrs_line['MPN'] = bomline.get('MPN', '')
            xyrs.append(xyrs_line)
    return xyrs
            
