#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import codecs
import locale
import os
import re
import sys
import textwrap

import jinja2
import clize

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
MARKDOWN_ESCAPES = [('\\', '\\\\'),
                    ('_', '\\_'),
                    ('*', '\\*')]
LATEX_URL_REPL = r'\\url{\1}'
MARKDOWN_URL_REPL = r'<\1>'


def line_to_message(line, out_format='latex'):
    match = re.search(r'\[\d\d:\d\d:\d\d] ([^:]+): (.*)', line)
    if not match:
        return None
    name, text = match.groups()
    who = INITIALS[name]
    if out_format == 'latex':
        text = transform(text, repl=LATEX_URL_REPL, escapes=LATEX_ESCAPES)
    elif out_format == 'markdown':
        text = transform(text, repl=MARKDOWN_URL_REPL, escapes=MARKDOWN_ESCAPES)
    text = textwrap.fill(text, width=70, break_long_words=False,
                         break_on_hyphens=False)
    message = {'who': who, 'text': text}
    return message


def transform(text, repl=LATEX_URL_REPL, escapes=LATEX_ESCAPES):
    new_words = []
    for word in text.split():
        if is_url(word):
            new_word = urlize(word, repl)
            new_words.append(new_word)
        else:
            new_word = escape(word, escapes)
            new_words.append(new_word)
    return ' '.join(new_words)


def escape(text, escapes):
    for old, new in escapes:
        text = text.replace(old, new)
    return text


def is_url(text):
    return re.search(r'https?://[^ ]+', text)


def urlize(text, repl):
    return re.sub(r'(https?://[^ ]+)', repl, text)


@clize.clize
def cli_main(src_dir, template_file, fmt='latex'):
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
            block_start_string='@{',
            block_end_string='}@',
            variable_start_string='@{{',
            variable_end_string='}}@')

    template = env.get_template(template_file)

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
    clize.run(cli_main)
