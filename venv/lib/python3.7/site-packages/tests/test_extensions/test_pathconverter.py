"""Test cases for PathConverter."""
from __future__ import unicode_literals
from .. import util
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)


class TestRelative(util.MdCase):
    """Test relative paths."""

    extension = ["pymdownx.pathconverter"]
    extension_configs = {
        "pymdownx.pathconverter": {
            "base_path": CURRENT_DIR,
            "relative_path": PARENT_DIR
        }
    }

    def test_comment(self):
        """Test comment."""

        self.check_markdown(
            r'<!-- ![picture](../_assets/bg.png) -->',
            r'<!-- ![picture](../_assets/bg.png) -->'
        )

    def test_relative_path(self):
        """Test relative path."""

        self.check_markdown(
            r'![picture](../extensions/_assets/bg.png)',
            r'<p><img alt="picture" src="extensions/_assets/bg.png" /></p>'
        )

    def test_file_win_file_path_root(self):
        """Test windows file:// path with root slash."""

        self.check_markdown(
            r'[file link windows abs](file:///c:/path/file.html)',
            r'<p><a href="file:///c:/path/file.html">file link windows abs</a></p>'
        )

    def test_win_file_path(self):
        """Test windows file:// path."""

        self.check_markdown(
            r'[file link windows abs2](file://c:/path/file.html)',
            r'<p><a href="file://c:/path/file.html">file link windows abs2</a></p>'
        )

    def test_file_root(self):
        """Test Linux/Unix style root file:// path."""

        self.check_markdown(
            r'[file link abs](file:///path/file.html)',
            r'<p><a href="file:///path/file.html">file link abs</a></p>'
        )

    def test_root(self):
        """Test /root path."""

        self.check_markdown(
            r'[absolute](/absolute)',
            r'<p><a href="/absolute">absolute</a></p>'
        )

    def test_url(self):
        """Test normal URL."""

        self.check_markdown(
            r'[link](http://www.google.com)',
            r'<p><a href="http://www.google.com">link</a></p>'
        )

    def test_fragment(self):
        """Test HTML fragment."""

        self.check_markdown(
            r'[fragment](#fragment)',
            r'<p><a href="#fragment">fragment</a></p>'
        )

    def test_windows(self):
        """Test Windows file path."""

        self.check_markdown(
            r'[windows path abs](c:/path/file.html)',
            r'<p><a href="c:/path/file.html">windows path abs</a></p>'
        )

    def test_network_path(self):
        """Test network path."""

        self.check_markdown(
            r'[windows network path](//network/path/file.html)',
            r'<p><a href="//network/path/file.html">windows network path</a></p>'
        )

    def test_strange_url(self):
        """Test strange URL."""

        self.check_markdown(
            r'[strange link](strange://odd/link/file.html)',
            r'<p><a href="strange://odd/link/file.html">strange link</a></p>'
        )

    def test_strange_url2(self):
        """Test additional strange URL."""

        self.check_markdown(
            r'[strange link 2](strange://www.odd.com/link/file.html)',
            r'<p><a href="strange://www.odd.com/link/file.html">strange link 2</a></p>'
        )

    def test_mail(self):
        """Test mail link."""

        self.check_markdown(
            r'<mail@mail.com>',
            r'<p><a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#109;&#97;&#105;&#108;&#64;&#109;&#97;&#105;&#108;'
            r'&#46;&#99;&#111;&#109;">&#109;&#97;&#105;&#108;&#64;&#109;&#97;&#105;&#108;&#46;&#99;&#111;&#109;</a></p>'
        )


class TestAbsolute(util.MdCase):
    """Test absolute paths."""

    extension = ["pymdownx.pathconverter"]
    extension_configs = {
        "pymdownx.pathconverter": {
            "base_path": "/Some/fake/path",
            "absolute": True
        }
    }

    def test_comment(self):
        """Test comment."""

        self.check_markdown(
            r'<!-- ![picture](../_assets/bg.png) -->',
            r'<!-- ![picture](../_assets/bg.png) -->'
        )

    def test_relative_path(self):
        """Test relative path."""

        self.check_markdown(
            r'![picture](./extensions/_assets/bg.png)',
            r'<p><img alt="picture" src="/Some/fake/path/extensions/_assets/bg.png" /></p>'
        )

    def test_file_win_file_path_root(self):
        """Test windows file:// path with root slash."""

        self.check_markdown(
            r'[file link windows abs](file:///c:/path/file.html)',
            r'<p><a href="file:///c:/path/file.html">file link windows abs</a></p>'
        )

    def test_win_file_path(self):
        """Test windows file:// path."""

        self.check_markdown(
            r'[file link windows abs2](file://c:/path/file.html)',
            r'<p><a href="file://c:/path/file.html">file link windows abs2</a></p>'
        )

    def test_file_root(self):
        """Test Linux/Unix style root file:// path."""

        self.check_markdown(
            r'[file link abs](file:///path/file.html)',
            r'<p><a href="file:///path/file.html">file link abs</a></p>'
        )

    def test_root(self):
        """Test /root path."""

        self.check_markdown(
            r'[absolute](/absolute)',
            r'<p><a href="/absolute">absolute</a></p>'
        )

    def test_url(self):
        """Test normal URL."""

        self.check_markdown(
            r'[link](http://www.google.com)',
            r'<p><a href="http://www.google.com">link</a></p>'
        )

    def test_fragment(self):
        """Test HTML fragment."""

        self.check_markdown(
            r'[fragment](#fragment)',
            r'<p><a href="#fragment">fragment</a></p>'
        )

    def test_windows(self):
        """Test Windows file path."""

        self.check_markdown(
            r'[windows path abs](c:/path/file.html)',
            r'<p><a href="c:/path/file.html">windows path abs</a></p>'
        )

    def test_network_path(self):
        """Test network path."""

        self.check_markdown(
            r'[windows network path](//network/path/file.html)',
            r'<p><a href="//network/path/file.html">windows network path</a></p>'
        )

    def test_strange_url(self):
        """Test strange URL."""

        self.check_markdown(
            r'[strange link](strange://odd/link/file.html)',
            r'<p><a href="strange://odd/link/file.html">strange link</a></p>'
        )

    def test_strange_url2(self):
        """Test additional strange URL."""

        self.check_markdown(
            r'[strange link 2](strange://www.odd.com/link/file.html)',
            r'<p><a href="strange://www.odd.com/link/file.html">strange link 2</a></p>'
        )

    def test_mail(self):
        """Test mail link."""

        self.check_markdown(
            r'<mail@mail.com>',
            r'<p><a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#109;&#97;&#105;&#108;&#64;&#109;&#97;&#105;&#108;'
            r'&#46;&#99;&#111;&#109;">&#109;&#97;&#105;&#108;&#64;&#109;&#97;&#105;&#108;&#46;&#99;&#111;&#109;</a></p>'
        )


class TestWindowsAbs(util.MdCase):
    """Test windows specific cases for absolute."""

    extension = ["pymdownx.pathconverter"]
    extension_configs = {
        "pymdownx.pathconverter": {
            "base_path": "C:/Some/fake/path",
            "absolute": True
        }
    }

    def test_windows_root_conversion(self):
        """Test Windows c:/ Conversion."""

        if util.is_win():
            self.check_markdown(
                r'![picture](./extensions/_assets/bg.png)',
                r'<p><img alt="picture" src="C:/Some/fake/path/extensions/_assets/bg.png" /></p>'
            )
        else:
            self.check_markdown(
                r'![picture](./extensions/_assets/bg.png)',
                r'<p><img alt="picture" src="C%3A/Some/fake/path/extensions/_assets/bg.png" /></p>'
            )


class TestWindowsRel(util.MdCase):
    """Test windows specific cases for relative."""

    extension = ["pymdownx.pathconverter"]
    extension_configs = {
        "pymdownx.pathconverter": {
            "base_path": "C:/Some/fake/path",
            "relative_path": "C:/Some/other/path"
        }
    }

    def test_windows_root_conversion(self):
        """Test Windows c:/ Conversion."""

        if util.is_win():
            self.check_markdown(
                r'![picture](./extensions/_assets/bg.png)',
                r'<p><img alt="picture" src="../../fake/path/extensions/_assets/bg.png" /></p>'
            )
        else:
            self.check_markdown(
                r'![picture](./extensions/_assets/bg.png)',
                r'<p><img alt="picture" src="../../fake/path/extensions/_assets/bg.png" /></p>'
            )
