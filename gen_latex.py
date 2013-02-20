#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import codecs
import locale
import os
import re
import sys
import textwrap

import jinja2

# Wrap sys.stdout into a StreamWriter to allow writing unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

INITIALS = {u'Jakub Szwachła': u'K', u'Agnieszka Talaga': u'A'}
LATEX_ESCAPES = [('\\',  '\\textbackslash{}'),
           ('#',  '\\#'),
           ('$',  '\\$'),
           ('%',  '\\%'),
           ('^',  '\\^{}'),
           ('&',  '\\&'),
           ('_',  '\\_'),
           ('~',  '\\~{}'),
           ('<',  '\\textless{}'),
           ('>',  '\\textgreater{}')]


def line_to_message(line, out_format='latex'):
    match = re.search(r'\[\d\d:\d\d:\d\d] ([^:]+): (.*)', line)
    if not match:
        return None
    name, text = match.groups()
    who = INITIALS[name]
    if out_format == 'latex':
        text = latexify(text)
    elif out_format == 'markdown':
        text = markdownify(text)
    text = textwrap.fill(text, width=70, break_long_words=False,
                         break_on_hyphens=False)
    message = {'who': who, 'text': text}
    return message


def latexify(text):
    new_words = []
    for word in text.split():
        if is_url(word):
            new_word = latex_urlize(word)
            new_words.append(new_word)
        else:
            new_word = escape(word, LATEX_ESCAPES)
            new_words.append(new_word)
    return ' '.join(new_words)


def markdownify(text):
    new_words = []
    for word in text.split():
        if is_url(word):
            new_word = markdown_urlize(word)
            new_words.append(new_word)
        else:
            new_word = re.escape(word)
            new_words.append(new_word)
    return ' '.join(new_words)


def escape(text, escapes):
    for old, new in escapes:
        text = text.replace(old, new)
    return text


def is_url(text):
    return re.search(r'https?://[^ ]+', text)


def latex_urlize(text):
    return re.sub(r'(https?://[^ ]+)', r'\\url{\1}', text)


def markdown_urlize(text):
    return re.sub(r'(https?://[^ ]+)', r'<\1>', text)


def main():
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
            block_start_string='@{',
            block_end_string='}@',
            variable_start_string='@{{',
            variable_end_string='}}@')

    src_dir = sys.argv[1]
    template = env.get_template(sys.argv[2])

    fmt = 'latex'
    if (sys.argv[3]):
        fmt = sys.argv[3]

    history = []
    for src_file in sorted(os.listdir(src_dir)):
        filename = os.path.join(src_dir, src_file)
        with codecs.open(filename, encoding='utf-8') as src:
            lines = src.readlines()
            conversation = [line_to_message(line, fmt) for line in lines]
            conversation = [m for m in conversation if m is not None]
            history.append(conversation)
    print template.render(history=history)


if __name__ == '__main__':
    main()
