"""
Caret.

pymdownx.caret
Really simple plugin to add support for

`<ins>test</ins>` tags as `^^test^^` and
`<sup>test</sup>` tags as `^test^`

MIT license.

Copyright (c) 2014 - 2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
from markdown import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor, DoubleTagInlineProcessor, SimpleTextInlineProcessor
from . import util

RE_SMART_CONTENT = r'((?:[^\^]|\^(?=[^\W_]|\^|\s)|(?<=\s)\^+?(?=\s))+?\^*?)'
RE_CONTENT = r'((?:[^\^]|(?<!\^)\^(?=[^\W_]|\^))+?)'
RE_SMART_INS = r'(?:(?<=_)|(?<![\w\^]))(\^{2})(?![\s\^])%s(?<!\s)\1(?:(?=_)|(?![\w\^]))' % RE_SMART_CONTENT
RE_INS = r'(\^{2})(?!\s)%s(?<!\s)\1' % RE_CONTENT

RE_SUP_INS = r'(\^{3})(?!\s)([^\^]+?)(?<!\s)\1'
RE_SMART_SUP_INS = r'(\^{3})(?!\s)%s(?<!\s)\1' % RE_SMART_CONTENT
RE_SUP_INS2 = r'(\^{3})(?!\s)([^\^]+?)(?<!\s)\^{2}([^\^ ]+?)\^'
RE_SMART_SUP_INS2 = r'(\^{3})(?!\s)%s(?<!\s)\^{2}(?:(?=_)|(?![\w\^]))([^\^ ]+?)\^' % RE_SMART_CONTENT
RE_SUP = r'(\^)([^\^ ]+?|\^)\1'

RE_NOT_CARET = r'((^| )(\^)( |$))'


class InsertSubExtension(Extension):
    """Adds insert extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'smart_insert': [True, "Treat ^^connected^^words^^ intelligently - Default: True"],
            'insert': [True, "Enable insert - Default: True"],
            'superscript': [True, "Enable superscript - Default: True"]
        }

        super(InsertSubExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Insert <ins>test</ins> tags as ^^test^^ and/or <sup>test</sup> tags as ^test^."""

        config = self.getConfigs()
        insert = bool(config.get('insert', True))
        superscript = bool(config.get('superscript', True))
        smart = bool(config.get('smart_insert', True))

        escape_chars = []
        if insert or superscript:
            escape_chars.append('^')
        if superscript:
            escape_chars.append(' ')
        util.escape_chars(md, escape_chars)

        ins_rule = RE_SMART_INS if smart else RE_INS
        sup_ins_rule = RE_SUP_INS
        sup_ins2_rule = RE_SMART_SUP_INS2 if smart else RE_SUP_INS2
        sup_rule = RE_SUP

        md.inlinePatterns.register(SimpleTextInlineProcessor(RE_NOT_CARET), "not_caret", 65)
        if insert:
            if superscript:
                md.inlinePatterns.register(DoubleTagInlineProcessor(sup_ins_rule, "sup,ins"), "sup_ins", 64.9)
                md.inlinePatterns.register(DoubleTagInlineProcessor(sup_ins2_rule, "sup,ins"), "sup_ins2", 64.8)

            # If not "smart", this needs to occur before `ins`, but if "smart", this needs to be after `ins`
            if superscript and not smart:
                md.inlinePatterns.register(SimpleTagInlineProcessor(sup_rule, "sup"), "sup", 64.8)

            md.inlinePatterns.register(SimpleTagInlineProcessor(ins_rule, "ins"), "ins", 64)

            # "smart", so this happens after `ins`
            if superscript and smart:
                md.inlinePatterns.register(SimpleTagInlineProcessor(sup_rule, "sup"), "sup", 63.9)
        elif superscript:
            md.inlinePatterns.register(SimpleTagInlineProcessor(sup_rule, "sup"), "sup", 64.8)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return InsertSubExtension(*args, **kwargs)
