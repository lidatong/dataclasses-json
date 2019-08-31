"""Test cases for Highlight."""
from __future__ import unicode_literals
from .. import util


class TestHighlightInline(util.MdCase):
    """Test highlight inline."""

    extension = ['pymdownx.highlight', 'pymdownx.superfences']
    extension_configs = {
        'pymdownx.highlight': {
            'linenums_style': 'pymdownx-inline'
        }
    }

    def test_pymdownx_inline(self):
        """Test new inline mode."""

        self.check_markdown(
            r'''
            ```python linenums="1"
            import test
            test.test()
            ```
            ''',
            r'''
            <div class="highlight"><pre><span></span><span class="lineno" data-linenos="1 "></span><span class="kn">import</span> <span class="nn">test</span>
            <span class="lineno" data-linenos="2 "></span><span class="n">test</span><span class="o">.</span><span class="n">test</span><span class="p">()</span>
            </pre></div>
            ''',  # noqa: E501
            True
        )


class TestHighlightSpecial(util.MdCase):
    """Test highlight global special."""

    extension = ['pymdownx.highlight', 'pymdownx.superfences']
    extension_configs = {
        'pymdownx.highlight': {
            'linenums_style': 'pymdownx-inline',
            'linenums_special': 2
        }
    }

    def test_special(self):
        """Test global special mode."""

        self.check_markdown(
            r'''
            ```python linenums="1"
            import test
            test.test()
            ```
            ''',
            r'''
            <div class="highlight"><pre><span></span><span class="lineno" data-linenos="1 "></span><span class="kn">import</span> <span class="nn">test</span>
            <span class="lineno special" data-linenos="2 "></span><span class="n">test</span><span class="o">.</span><span class="n">test</span><span class="p">()</span>
            </pre></div>
            ''',  # noqa: E501
            True
        )

    def test_special_override(self):
        """Test global special mode override."""

        self.check_markdown(
            r'''
            ```python linenums="1 1 1"
            import test
            test.test()
            ```
            ''',
            r'''
            <div class="highlight"><pre><span></span><span class="lineno special" data-linenos="1 "></span><span class="kn">import</span> <span class="nn">test</span>
            <span class="lineno special" data-linenos="2 "></span><span class="n">test</span><span class="o">.</span><span class="n">test</span><span class="p">()</span>
            </pre></div>
            ''',  # noqa: E501
            True
        )
