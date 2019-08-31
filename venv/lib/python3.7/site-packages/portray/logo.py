from portray._version import __version__

ascii_art = """

██████╗  ██████╗ ██████╗ ████████╗██████╗  █████╗ ██╗   ██╗
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗╚██╗ ██╔╝
██████╔╝██║   ██║██████╔╝   ██║   ██████╔╝███████║ ╚████╔╝
██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══██╗██╔══██║  ╚██╔╝
██║     ╚██████╔╝██║  ██║   ██║   ██║  ██║██║  ██║   ██║
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝

        Your Project with Great Documentation.

Version: {}
Copyright Timothy Edmund Crosley 2019 MIT License

""".format(
    __version__
)

__doc__ = """
```python
{}
```
""".format(
    ascii_art
)
