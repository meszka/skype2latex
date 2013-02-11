#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import jinja2, os, re, sys, codecs

initials = {u'Jakub Szwachła': u'K', u'Agnieszka Talaga': u'A'}
escapes = {'#':  '\\#',
           '$':  '\\$',
           '%':  '\\%',
           '^':  '\\textasciicircum{}',
           '&':  '\\&',
           '_':  '\\_',
           '~':  '\\textasciitilde{}',
           '\\': '\\textbackslash{}',
           '<':  '\\textless{}',
           '>':  '\\textgreater{}'}

env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'),
                         block_start_string='@{',
                         block_end_string='}@',
                         variable_start_string='@{{',
                         variable_end_string='}}@')

template = env.get_template('template.tex')

srcdir = sys.argv[1]

def line_to_message(line):
    match = re.search(r'\[\d\d:\d\d:\d\d] ([^:]+): (.*)', line)
    if match == None:
        return {'who': '', 'text': ''}
    name, text = match.groups()
    who = initials[name]
    message = {'who': who, 'text': text}
    return message

def escaped_message(message):
    who = message['who']
    text = message['text']
    for old, new in escapes.items():
        text = text.replace(old, new)
    message = {'who': who, 'text': text}
    return message

for f in os.listdir(srcdir):
    filename = os.path.join(srcdir, f)
    with codecs.open(filename, encoding='utf-8') as src:
        lines = src.readlines()
        messages = [line_to_message(line) for line in lines]
        messages = [escaped_message(message) for message in messages]
        print template.render(messages=messages)
