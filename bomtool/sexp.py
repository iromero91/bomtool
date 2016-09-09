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

from string import whitespace

_atom_end = set('()"\'') | set(whitespace)
_escapes = {'n': '\n', 'r': '\r', 't': '\t'}

def contains_any(lst, s):
    return True in [c in lst for c in s]


# Based on a Gist by Paul Bonser (pib)
# https://gist.github.com/pib/240957
def loads(s):
    stack, i, length = [[]], 0, len(s)
    while i < length:
        c = s[i]
        reading = type(stack[-1])
        if reading == list:
            if c == '(': stack.append([])
            elif c == ')': 
                stack[-2].append(stack.pop())
                if stack[-1][0] == ('quote',): stack[-2].append(stack.pop())
            elif c == '"': stack.append('')
            elif c == "'": stack.append([('quote',)])
            elif c in whitespace: pass
            else: stack.append((c,))
        elif reading == str:
            if c == '"': 
                stack[-2].append(stack.pop())
                if stack[-1][0] == ('quote',): stack[-2].append(stack.pop())
            elif c == '\\': 
                i += 1
                stack[-1] += _escapes.get(s[i], s[i])
            else: stack[-1] += c
        elif reading == tuple:
            if c in _atom_end:
                atom = stack.pop()
                stack[-1].append(atom[0])
                if stack[-1][0] == ('quote',): stack[-2].append(stack.pop())
                continue
            else: stack[-1] = ((stack[-1][0] + c),)
        i += 1
    return stack.pop()

def load(f):
    return loads(f.read())

def dumps(sexpr, retarded=True):
    if type(sexpr) == list:
        return "(" + " ".join((dumps(s, retarded) for s in sexpr)) + ")"
    elif retarded and sexpr and type(sexpr) == str and not contains_any(sexpr, _atom_end):
        return sexpr
    elif type(sexpr) == str:
        return '"{}"'.format(sexpr.replace('\\', '\\\\').replace('"', '\\"'))
    else:
        return repr(sexpr)

def dump(sexpr, f, retarded=True):
    f.write(dumps(sexpr, retarded))

def car(lst):
    if type(lst) != list or len(lst) == 0:
        return lst
    else:
        return lst[0]

def cdr(lst):
    return lst[1:]

def cadr(lst):
    return car(cdr(lst))

def findall(lst, name):
    return (x for x in lst if car(x) == name)

def assoc(lst, key):
    for itm in lst:
        if car(itm) == key:
            return itm
    else:
        return []
            
