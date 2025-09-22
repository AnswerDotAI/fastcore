"Filters for processing ANSI colors."

# Copyright (c) IPython Development Team.
# Modifications by Jeremy Howard.

import re
from html import escape

__all__ = ["strip_ansi", "ansi2html", "ansi2latex"]

_ANSI_RE = re.compile("\x1b\\[(.*?)([@-~])")
_ANSI_COLORS = ( "ansi-black", "ansi-red", "ansi-green", "ansi-yellow", "ansi-blue", "ansi-magenta", "ansi-cyan", "ansi-white", "ansi-black-intense",
    "ansi-red-intense", "ansi-green-intense", "ansi-yellow-intense", "ansi-blue-intense", "ansi-magenta-intense", "ansi-cyan-intense", "ansi-white-intense")

def strip_terminal_queries(text):
    # Remove OSC sequences (like background color queries)
    text = re.sub(r'\x1b\][^\\x07]*\x07', '', text)
    # Remove DSR sequences (device status reports)
    return re.sub(r'\x1b\[[0-9]*n', '', text)


def strip_ansi(source):
    "Remove ANSI escape codes from text."
    return _ANSI_RE.sub("", source)


def ansi2html(text):
    "Convert ANSI colors to HTML colors."
    text = escape(strip_terminal_queries(text))
    return _ansi2anything(text, _htmlconverter)


def ansi2latex(text):
    "Convert ANSI colors to LaTeX colors."
    return _ansi2anything(text, _latexconverter)


def _htmlconverter(fg, bg, bold, underline, inverse):
    "Return start and end tags for given foreground/background/bold/underline."
    if (fg, bg, bold, underline, inverse) == (None, None, False, False, False): return "", ""

    classes,styles = [],[]
    if inverse: fg, bg = bg, fg
    if isinstance(fg, int): classes.append(_ANSI_COLORS[fg] + "-fg")
    elif fg: styles.append("color: rgb({},{},{})".format(*fg))
    elif inverse: classes.append("ansi-default-inverse-fg")

    if isinstance(bg, int): classes.append(_ANSI_COLORS[bg] + "-bg")
    elif bg: styles.append("background-color: rgb({},{},{})".format(*bg))
    elif inverse: classes.append("ansi-default-inverse-bg")

    if bold: classes.append("ansi-bold")
    if underline: classes.append("ansi-underline")

    starttag = "<span"
    if classes: starttag += ' class="' + " ".join(classes) + '"'
    if styles: starttag += ' style="' + "; ".join(styles) + '"'
    starttag += ">"
    return starttag, "</span>"


def _latexconverter(fg, bg, bold, underline, inverse):
    "Return start and end markup given foreground/background/bold/underline."
    if (fg, bg, bold, underline, inverse) == (None, None, False, False, False): return "", ""
    starttag, endtag = "", ""
    if inverse: fg, bg = bg, fg
    if isinstance(fg, int):
        starttag += r"\textcolor{" + _ANSI_COLORS[fg] + "}{"
        endtag = "}" + endtag
    elif fg:
        # See http://tex.stackexchange.com/a/291102/13684
        starttag += r"\def\tcRGB{\textcolor[RGB]}\expandafter"
        starttag += r"\tcRGB\expandafter{{\detokenize{{{},{},{}}}}}{{".format(*fg)
        endtag = "}" + endtag
    elif inverse:
        starttag += r"\textcolor{ansi-default-inverse-fg}{"
        endtag = "}" + endtag

    if isinstance(bg, int):
        starttag += r"\setlength{\fboxsep}{0pt}"
        starttag += r"\colorbox{" + _ANSI_COLORS[bg] + "}{"
        endtag = r"\strut}" + endtag
    elif bg:
        starttag += r"\setlength{\fboxsep}{0pt}"
        # See http://tex.stackexchange.com/a/291102/13684
        starttag += r"\def\cbRGB{\colorbox[RGB]}\expandafter"
        starttag += r"\cbRGB\expandafter{{\detokenize{{{},{},{}}}}}{{".format(*bg)
        endtag = r"\strut}" + endtag
    elif inverse:
        starttag += r"\setlength{\fboxsep}{0pt}"
        starttag += r"\colorbox{ansi-default-inverse-bg}{"
        endtag = r"\strut}" + endtag

    if bold:
        starttag += r"\textbf{"
        endtag = "}" + endtag

    if underline:
        starttag += r"\underline{"
        endtag = "}" + endtag

    return starttag, endtag


def _ansi2anything(text, converter):
    "Convert ANSI colors to HTML or LaTeX."
    fg, bg = None, None
    bold, underline, inverse = False, False, False
    numbers,out = [],[]

    while text:
        m = _ANSI_RE.search(text)
        if m:
            if m.group(2) == "m":
                # Empty code is same as code 0
                try: numbers = [int(n) if n else 0 for n in m.group(1).split(";")]
                except ValueError: pass  # Invalid color specification
            else: pass  # Not a color code
            chunk, text = text[: m.start()], text[m.end() :]
        else: chunk, text = text, ""

        if chunk:
            starttag, endtag = converter(
                fg + 8 if bold and fg in range(8) else fg,  # type:ignore[operator]
                bg, bold, underline, inverse)
            out.append(starttag)
            out.append(chunk)
            out.append(endtag)

        while numbers:
            n = numbers.pop(0)
            if n == 0:
                # Code 0 (same as empty code): reset everything
                fg = bg = None
                bold = underline = inverse = False
            elif n == 1: bold = True
            elif n == 4: underline = True
            # Code 5: blinking
            elif n == 5: bold = True
            elif n == 7: inverse = True
            elif n in (21, 22): bold = False
            elif n == 24: underline = False
            elif n == 27: inverse = False
            elif 30 <= n <= 37: fg = n - 30
            elif n == 38:
                try: fg = _get_extended_color(numbers)
                except ValueError: numbers.clear()
            elif n == 39: fg = None
            elif 40 <= n <= 47: bg = n - 40
            elif n == 48:
                try: bg = _get_extended_color(numbers)
                except ValueError: numbers.clear()
            elif n == 49: bg = None
            elif 90 <= n <= 97: fg = n - 90 + 8
            elif 100 <= n <= 107: bg = n - 100 + 8
            else: pass  # Unknown codes are ignored
    return "".join(out)


def _get_extended_color(numbers):
    n = numbers.pop(0)
    if n == 2 and len(numbers) >= 3:
        # 24-bit RGB
        r = numbers.pop(0)
        g = numbers.pop(0)
        b = numbers.pop(0)
        if not all(0 <= c <= 255 for c in (r, g, b)): raise ValueError()
    elif n == 5 and len(numbers) >= 1:
        # 256 colors
        idx = numbers.pop(0)
        if idx < 0: raise ValueError()
        # 16 default terminal colors
        if idx < 16: return idx
        if idx < 232:
            # 6x6x6 color cube, see http://stackoverflow.com/a/27165165/500098
            r = (idx - 16) // 36
            r = 55 + r * 40 if r > 0 else 0
            g = ((idx - 16) % 36) // 6
            g = 55 + g * 40 if g > 0 else 0
            b = (idx - 16) % 6
            b = 55 + b * 40 if b > 0 else 0
        # grayscale, see http://stackoverflow.com/a/27165165/500098
        elif idx < 256: r = g = b = (idx - 232) * 10 + 8
        else: raise ValueError()
    else: raise ValueError()
    return r, g, b

