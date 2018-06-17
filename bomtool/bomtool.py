# -*- coding: utf-8 -*-
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

from . import sexp
from .sexp import car, cdr, cadr, findall, assoc

from . import pngen

import re
import logging
from collections import defaultdict

from csv import DictWriter

_manuf_abbr = {
    'TI': "Texas Instruments",
    'DIODESINC': "Diodes Incorporated",
}

_known_pkgs = {
    'MELF-0102': "MELF, 0102",
    'MELF-0204': "MELF, 0204",
    'MELF-0207': "MELF, 0207",
    'MELF-0309': "MELF, 0309",
    '01005': "01005 (0402 Metric)",
    '0201': "0201 (0603 Metric)",
    '0202': "0202 (0505 Metric)",
    '0302': "0302 (0805 Metric)",
    '0306': "0306 (0816 Metric)",
    '0402': "0402 (1005 Metric)",
    '0404': "0404 (1010 Metric)",
    '0406': "Wide 0604 (1610 Metric), 0406",
    '0502': "0502 (1106 Metric)",
    '0503': "0503 (1308 Metric)",
    '0505': "0505 (1313 Metric)",
    '0508': "0508 (1220 Metric)",
    '0603': "0603 (1608 Metric)",
    '0612': "0612 (1632 Metric)",
    '0805': "0805 (2012 Metric)",
    '0815': "Wide 1508 (3720 Metric), 0815",
    '0830': "Wide 3008 (2075 Metric), 0830",
    '1020': "Wide 2010 (5025 Metric), 1020",
    '1111': "1111 (2828 Metric)",
    '1530': "Wide 3015 (7638 Metric), 1530",
    '1808': "1808 (4520 Metric)",
    '1206': "1206 (3216 Metric)",
    '1210': "1210 (3225 Metric)",
    '1218': "1218 (3246 Metric)",
    '1225': "Wide 2512 (6432 Metric), 1225",
    '1625': "Wide 2516 (6440 Metric), 1625",
    '1812': "1812 (4532 Metric)",
    '1835': "Wide 3518 (9045 Metric), 1835",
    '2010': "2010 (5025 Metric)",
    '2043': "Wide 4320 (11050 Metric), 2043",
    '2512': "2512 (6432 Metric)",
    '2615': "2615 (6538 Metric)",
    '2616': "2616 (6740 Metric)",
    '2728': "Wide 2827 (7067 Metric), 2728",
    '5929': "Wide 2959 (7515 Metric), 5929",
}

dielectrics = ['NP0', 'C0G', 'X5R', 'X7R']

class ComponentCache:
    def get(self, key, default=None):
        res = default
        if key[:2] == ('RES', 'SMD'):
            fields = list(key[2:])
            value = parse_eng(fields.pop(0))
            tolerance = 5
            power = None
            package = None
            for f in fields:
                if f[0] + f[-1] == "[]":
                    package = f[1:-1]
                elif f[-1] == '%':
                    tolerance = float(f[:-1])
                elif f[-1] in ['W', 'w']:
                    power = parse_eng(f[:-1])
            res = pngen.RC(value, tolerance, power, package)
        if key[:2] == ('CAP', 'MLCC'):
            fields = list(key[2:])
            value = parse_eng(fields.pop(0))
            tolerance = 10
            dielectric = None
            voltage = 16
            package = None
            for f in fields:
                if f[0] + f[-1] == "[]":
                    package = f[1:-1]
                elif f[-1] == '%':
                    tolerance = float(f[:-1])
                elif f[-1] in ['V', 'v']:
                    voltage = parse_eng(f[:-1])
                elif f in dielectrics:
                    dielectric = f
            if dielectric in ['X7R', 'X5R']:
                res = pngen.CC_XxR(value, tolerance, voltage, package, dielectric=dielectric)
        return res

known_components = ComponentCache()


def parse_comp(comp_data):
    res = {}
    for key in ['ref', 'value', 'footprint']:
        res[key] = cadr(assoc(comp_data, key)) or ''
    fields = cdr(assoc(comp_data, 'fields'))
    for f in fields:
        res[cadr(assoc(f, 'name'))] = f[-1]
    return res


def load_netlist(net_file):
    net_data = car(sexp.load(net_file))
    comps_data = findall(cdr(assoc(net_data, 'components')), 'comp')
    return [parse_comp(c) for c in comps_data]

_re_eng = re.compile(
    r'(?P<whole>\d*)'
    r'(?P<sep>[.pnuµmkMGRRr])?'
    r'(?P<decimals>\d*)'
    r'(?P<suffix>[.pnuµmkMG])?'
)

_eng_suffixes = {
    'p': 1e-12,
    'n': 1e-9,
    'u': 1e-6,
    'µ': 1e-6,
    'm': 1e-3,
    'k': 1e3,
    'M': 1e6,
    'G': 1e9
}

def parse_eng(s):
    value = None
    match = _re_eng.match(s)
    if match and (match.group('whole') or match.group('decimals')):
        value = float(match.group('whole') + '.' + match.group('decimals'))
        if match.group('sep') in _eng_suffixes:
            value *= _eng_suffixes[match.group('sep')]
        else:
            value *= _eng_suffixes.get(match.group('suffix'), 1)
    return value

def parse_bomline(line):
    # If we have multiple bom lines, recurse
    if ';' in line:
        bomlines = []
        for l in line.split(';'):
            if l.strip():
                bomlines += parse_bomline(l.strip())
        return bomlines
    #
    # Otherwise parse a single bom line
    attrs = {}
    fields = line.strip().split()
    attrs['description'] = line
    # Extract quantity if it exists (first field)
    if fields[0][0] + fields[0][-1] == "()":
        multiplier = fields.pop(0)[1:-1]
        try:
            if multiplier == "DNP":
                attrs['mult'] = 0
            else:
                attrs['mult'] = int(multiplier, 10)
        except:
            logging.error("Invalid multiplier ({})".format(multiplier))
            
    known_component = known_components.get(tuple(fields))
    # Extract package if it exists (last field)
    if fields[-1][0] + fields[-1][-1] == "[]":
        package = fields.pop(-1)[1:-1]
        attrs['package'] = _known_pkgs.get(package, package)
    # Extract the attributes depending on the kind of component
    kind = attrs['kind'] = fields[0]

    if known_component:
        attrs.update(known_component)
    elif kind in ['RES', 'BEAD'] and cadr(fields) in ['SMD', 'AXIAL']:
        attrs['value'] = " ".join(fields[2:])
    elif kind == 'CAP' and cadr(fields) in ['MLCC', 'TANT']:
        attrs['value'] = " ".join(fields[2:])
    elif len(fields) == 3:
        attrs['manufacturer'] = _manuf_abbr.get(fields[1], fields[1].capitalize())
        attrs['MPN'] = fields[2]
    elif len(fields) == 2:
        attrs['MPN'] = fields[1]

    return [attrs]


def generate_bom(comps):
    grouped = defaultdict(list)
    for c in comps:
        if c.get('BOM', '') == '':
            logging.error("Component '{}' has no BOM line!".format(c['ref']))
            grouped['!!MISSING!! '+c['value']].append(c)
        elif c['BOM'] == 'VIRTUAL':
            logging.warning(
                "Component '{}' is VIRTUAL, will be excluded from the BOM."
                .format(c['ref']))
        else:
            grouped[c['BOM']].append(c)
    bom = []
    for l in sorted(grouped.keys()):
        bomlines = parse_bomline(l)
        for bomline in bomlines:
            bomline['qty'] = len(grouped[l]) * bomline.get('mult', 1) or 'DO NOT POPULATE'
            bomline['refs'] = ", ".join([c['ref'] for c in grouped[l]])
            for component in grouped[l]:
                # Allow component attributes to override the bomline
                if component.get('MPN'):
                    bomline['MPN'] = component['MPN']
                if component.get('manufacturer'):
                    bomline['manufacturer'] = component['manufacturer']
                elif component.get('Manuf'):
                    bomline['manufacturer'] = component['Manuf']
            bom.append(bomline)
    return bom

_bom_fields = ['qty','refs', 'description', 'package', 'manufacturer', 'MPN']

def write_bom_csv(bom, bom_file):
    bom_writer = DictWriter(bom_file, fieldnames=_bom_fields,
                            extrasaction='ignore')
    bom_writer.writeheader()
    for b in bom:
        bom_writer.writerow(b)
