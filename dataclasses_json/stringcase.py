# Copyright © 2015-2018 Taka Okunishi <okunishinishi@gmail.com>.
# Copyright © 2020 Louis-Philippe Véronneau <pollo@debian.org>

import re


def uplowcase(string, case):
    """Convert string into upper or lower case.

    Args:
        string: String to convert.

    Returns:
        string: Uppercase or lowercase case string.

    """
    if case == 'up':
        return str(string).upper()
    elif case == 'low':
        return str(string).lower()


def capitalcase(string):
    """Convert string into capital case.
    First letters will be uppercase.

    Args:
        string: String to convert.

    Returns:
        string: Capital case string.

    """

    string = str(string)
    if not string:
        return string
    return uplowcase(string[0], 'up') + string[1:]


def camelcase(string):
    """ Convert string into camel case.

    Args:
        string: String to convert.

    Returns:
        string: Camel case string.

    """

    string = re.sub(r"^[\-_\.]", '', str(string))
    if not string:
        return string
    return uplowcase(string[0], 'low') \
        + re.sub(r"[\-_\.\s]([a-z])",
                 lambda matched: uplowcase(matched.group(1), 'up'),
                 string[1:])


def snakecase(string):
    """Convert string into snake case.
    Join punctuation with underscore

    Args:
        string: String to convert.

    Returns:
        string: Snake cased string.

    """

    string = re.sub(r"[\-\.\s]", '_', str(string))
    if not string:
        return string
    return uplowcase(string[0], 'low') \
        + re.sub(r"[A-Z]",
                 lambda matched: '_' + uplowcase(matched.group(0), 'low'),
                 string[1:])


def spinalcase(string):
    """Convert string into spinal case.
    Join punctuation with hyphen.

    Args:
        string: String to convert.

    Returns:
        string: Spinal cased string.

    """

    return re.sub(r"_", "-", snakecase(string))


def pascalcase(string):
    """Convert string into pascal case.

    Args:
        string: String to convert.

    Returns:
        string: Pascal case string.

    """

    return capitalcase(camelcase(string))
