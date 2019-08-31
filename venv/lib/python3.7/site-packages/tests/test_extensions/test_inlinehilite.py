"""Test cases for Highlight."""
from __future__ import unicode_literals
from .. import util
import pymdownx.arithmatex as arithmatex


def _format(src, language, class_name, md):
    """Inline math formatter."""

    return '<span class="lang-%s %s">%s</span>' % (language, class_name, src)


class TestInlineHilite(util.MdCase):
    """Test general cases for inline highlight."""

    extension = [
        'markdown.extensions.attr_list',
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.inlinehilite': {
            'style_plain_text': True,
            'css_class': 'inlinehilite'
        }
    }

    def test_language(self):
        """Test language handling."""

        # Test #! original syntax
        self.check_markdown(
            r'`#!python import module`.',
            r'<p><code class="inlinehilite"><span class="kn">import</span> <span class="nn">module</span></code>.</p>'
        )

        # Test ::: syntax
        self.check_markdown(
            r'`:::python import module`.',
            r'<p><code class="inlinehilite"><span class="kn">import</span> <span class="nn">module</span></code>.</p>'
        )

        # Test escaping language with space
        self.check_markdown(
            r'` #!python import module`.',
            r'<p><code class="inlinehilite">#!python import module</code>.</p>'
        )

        # Test bad language
        self.check_markdown(
            r'`#!bad import module`.',
            r'<p><code class="inlinehilite">import module</code>.</p>'
        )

    def test_escape(self):
        """Test backtick escape logic."""

        self.check_markdown(
            r'`Code`',
            r'<p><code class="inlinehilite">Code</code></p>'
        )

        self.check_markdown(
            r'\`Not code`',
            r'<p>`Not code`</p>'
        )

        self.check_markdown(
            r'\\`Code`',
            r'<p>\<code class="inlinehilite">Code</code></p>'
        )

        self.check_markdown(
            r'\\\`Not code`',
            r'<p>\`Not code`</p>'
        )

        self.check_markdown(
            r'\\\\`Code`',
            r'<p>\\<code class="inlinehilite">Code</code></p>'
        )

    def test_attributes(self):
        """Test with attribute extension."""

        self.check_markdown(
            r'`#!python import module`{: .test}',
            r'<p><code class="inlinehilite test">'
            r'<span class="kn">import</span> <span class="nn">module</span>'
            r'</code></p>'
        )


class TestInlineHilitePlainText(util.MdCase):
    """Test inline highlight when not styling plain text."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.inlinehilite': {
            'style_plain_text': False
        }
    }

    def test_unstyled_plaintext(self):
        """Test unstyled plain text."""

        self.check_markdown(
            r'Lets test inline highlight no guessing and no text styling `import module`.',
            r'<p>Lets test inline highlight no guessing and no text styling <code>import module</code>.</p>'
        )


class TestInlineHiliteNoPygments(util.MdCase):
    """Test inline highlight without Pygments."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.highlight': {
            'use_pygments': False
        },
        'pymdownx.inlinehilite': {
            'css_class': 'inlinehilite'
        }
    }

    def test_no_pygments(self):
        """Ensure proper behavior when disabling Pygments."""

        self.check_markdown(
            r'`#!python import module`.',
            r'<p><code class="inlinehilite language-python">import module</code>.</p>'
        )


class TestInlineHiliteGuess(util.MdCase):
    """Test inline highlight with guessing."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.highlight': {
            'guess_lang': True
        },
        'pymdownx.inlinehilite': {
            'css_class': 'inlinehilite',
            'style_plain_text': True
        }
    }

    def test_guessing(self):
        """Ensure guessing can be enabled."""

        self.check_markdown(
            r'`import module`.',
            r'<p><code class="inlinehilite"><span class="kn">import</span> <span class="nn">module</span></code>.</p>'
        )


class TestInlineHiliteCodeHilite(util.MdCase):
    """Test inline highlight with CodeHilite."""

    extension = [
        'markdown.extensions.codehilite',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'markdown.extensions.codehilite': {
            'guess_lang': False
        },
        'pymdownx.inlinehilite': {
            'style_plain_text': True
        }
    }

    def test_codehilite(self):
        """Test CodeHilite."""

        # Test #! original syntax
        self.check_markdown(
            r'`#!python import module`.',
            r'<p><code class="codehilite"><span class="kn">import</span> <span class="nn">module</span></code>.</p>'
        )

        # Test ::: syntax
        self.check_markdown(
            r'`:::python import module`.',
            r'<p><code class="codehilite"><span class="kn">import</span> <span class="nn">module</span></code>.</p>'
        )

        # Test escaping language with space
        self.check_markdown(
            r'` #!python import module`.',
            r'<p><code class="codehilite">#!python import module</code>.</p>'
        )

        # Test bad language
        self.check_markdown(
            r'`#!bad import module`.',
            r'<p><code class="codehilite">import module</code>.</p>'
        )


class TestInlineHiliteCustom1(util.MdCase):
    """Test custom InlineHilite cases."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.inlinehilite': {
            'css_class': 'inlinehilite',
            'custom_inline': [
                {
                    'name': 'math',
                    'class': 'arithmatex',
                    'format': arithmatex.inline_mathjax_format
                }
            ]
        }
    }

    def test_arithmatex(self):
        """Test Arithmatex."""

        self.check_markdown(
            r'`#!math 3 + 3`',
            r'''
            <p>
            <script type="math/tex">3 + 3</script>
            </p>
            ''',
            True
        )


class TestInlineHiliteCustom2(util.MdCase):
    """Test custom InlineHilite cases."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.inlinehilite': {
            'css_class': 'inlinehilite',
            'custom_inline': [
                {
                    'name': 'math',
                    'class': 'arithmatex',
                    'format': arithmatex.inline_mathjax_preview_format
                }
            ]
        }
    }

    def test_preview_arithmatex(self):
        """Test preview Arithmatex."""

        self.check_markdown(
            r'`#!math 3 + 3`',
            r'<p><span><span class="MathJax_Preview">3 + 3</span><script type="math/tex">3 + 3</script></span></p>'
        )


class TestInlineHiliteCustom3(util.MdCase):
    """Test custom InlineHilite cases."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.inlinehilite': {
            'css_class': 'inlinehilite',
            'custom_inline': [
                {
                    'name': 'math',
                    'class': 'arithmatex',
                    'format': arithmatex.inline_generic_format
                }
            ]
        }
    }

    def test_arithmatex_generic(self):
        """Test generic Arithmatex."""

        self.check_markdown(
            r'`#!math 3 + 3`',
            r'<p><span class="arithmatex">\(3 + 3\)</span></p>'
        )


class TestInlineHiliteCustom4(util.MdCase):
    """Test custom InlineHilite cases."""

    extension = [
        'pymdownx.highlight',
        'pymdownx.inlinehilite',
    ]
    extension_configs = {
        'pymdownx.inlinehilite': {
            'css_class': 'inlinehilite',
            'custom_inline': [
                {
                    'name': 'test',
                    'class': 'class-test',
                    'format': _format
                }
            ]
        }
    }

    def test_custom(self):
        """Test custom formatter."""

        self.check_markdown(
            r'`#!test src test`',
            r'<p><span class="lang-test class-test">src test</span></p>'
        )
