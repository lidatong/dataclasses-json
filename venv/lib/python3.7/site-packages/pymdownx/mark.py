"""
Mark.

pymdownx.mark
Really simple plugin to add support for
<mark>test</mark> tags as ==test==

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
from markdown.inlinepatterns import SimpleTagInlineProcessor, SimpleTextInlineProcessor
from . import util

RE_SMART_CONTENT = r'((?:[^\=]|\=(?=[^\W_]|\=|\s)|(?<=\s)\=+?(?=\s))+?\=*?)'
RE_DUMB_CONTENT = r'((?:[^\=]|(?<!\=)\=(?=[^\W_]|\=))+?)'
RE_SMART_MARK_BASE = r'(\={2})(?![\s\=])%s(?<!\s)\={2}' % RE_SMART_CONTENT
RE_SMART_MARK = r'(?:(?<=_)|(?<![\w\=]))%s(?:(?=_)|(?![\w\=]))' % RE_SMART_MARK_BASE
RE_MARK_BASE = r'(\={2})(?!\s)%s(?<!\s)\={2}' % RE_DUMB_CONTENT
RE_NOT_MARK = r'((^| )(\=)( |$))'
RE_MARK = RE_MARK_BASE


class MarkExtension(Extension):
    """Add the mark extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'smart_mark': [True, "Treat ==connected==words== intelligently - Default: True"]
        }

        super(MarkExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Add support for <mark>test</mark> tags as ==test==."""

        util.escape_chars(md, ['='])
        config = self.getConfigs()
        pattern = RE_SMART_MARK if config.get('smart_mark', True) else RE_MARK
        md.inlinePatterns.register(SimpleTextInlineProcessor(RE_NOT_MARK), "not_mark", 65)
        md.inlinePatterns.register(SimpleTagInlineProcessor(pattern, "mark"), "mark", 64.9)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return MarkExtension(*args, **kwargs)
