# PYTHON 3
# syntax.py

"""
This file contains external code, see the description of each classes
"""
import sys,re

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont,QSyntaxHighlighter,QBrush,QPalette,QTextCursor,QTextLayout
from PyQt5.QtWidgets import QTextEdit


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword' : format('orange','bold'),
    'operator': format('red'),
    'brace'   : format('darkGray'),
    'defclass': format('darkBlue', 'bold'),
    'string'  : format('grey'),
    'string2' : format('darkCyan'),
    'comment' : format('darkGreen', 'italic'),
    'self'    : format('black', 'italic'),
    'numbers' : format('red'),
}


class PythonHighlighter (QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    Found on https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
    Published under  BSD License:

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

    (1) Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

    (2) Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

    (3)The name of the author may not be used to
    endorse or promote products derived from this software without
    specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
    IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
    INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
    STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
    IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = text.length() - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class MarkdownHighlighter(QSyntaxHighlighter):
    """Found on https://github.com/rupeshk/MarkdownHighlighter/blob/master/markdownhighlighter.py
    under  GNU General Public License.
    """
    MARKDOWN_KEYS_REGEX = {
        'Bold' : re.compile(u'(?P<delim>\*\*)(?P<text>.+)(?P=delim)'),
        'uBold': re.compile(u'(?P<delim>__)(?P<text>[^_]{2,})(?P=delim)'),
        'Italic': re.compile(u'(?P<delim>\*)(?P<text>[^*]{2,})(?P=delim)'),
        'uItalic': re.compile(u'(?P<delim>_)(?P<text>[^_]+)(?P=delim)'),
        'Link': re.compile(u'(?u)(^|(?P<pre>[^!]))\[.*?\]:?[ \t]*\(?[^)]+\)?'),
        'Image': re.compile(u'(?u)!\[.*?\]\(.+?\)'),
        'HeaderAtx': re.compile(u'(?u)^\#{1,6}(.*?)\#*(\n|$)'),
        'Header': re.compile(u'^(.+)[ \t]*\n(=+|-+)[ \t]*\n+'),
        'CodeBlock': re.compile(u'^([ ]{4,}|\t).*'),
        'UnorderedList': re.compile(u'(?u)^\s*(\* |\+ |- )+\s*'),
        'UnorderedListStar': re.compile(u'^\s*(\* )+\s*'),
        'OrderedList': re.compile(u'(?u)^\s*(\d+\. )\s*'),
        'BlockQuote': re.compile(u'(?u)^\s*>+\s*'),
        'BlockQuoteCount': re.compile(u'^[ \t]*>[ \t]?'),
        'CodeSpan': re.compile(u'(?P<delim>`+).+?(?P=delim)'),
        'HR': re.compile(u'(?u)^(\s*(\*|-)\s*){3,}$'),
        'eHR': re.compile(u'(?u)^(\s*(\*|=)\s*){3,}$'),
        'Html': re.compile(u'<.+?>')
    }

    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
        self.parent.setTabStopWidth(self.parent.fontMetrics().width(' ')*8)

        self.defaultTheme =  {"background-color":"#d7d7d7", "color":"#191970", "bold": {"color":"#859900", "font-weight":"bold", "font-style":"normal"}, "emphasis": {"color":"#b58900", "font-weight":"bold", "font-style":"italic"}, "link": {"color":"#cb4b16", "font-weight":"normal", "font-style":"normal"}, "image": {"color":"#cb4b16", "font-weight":"normal", "font-style":"normal"}, "header": {"color":"#2aa198", "font-weight":"bold", "font-style":"normal"}, "unorderedlist": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "orderedlist": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "blockquote": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "codespan": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "codeblock": {"color":"#ff9900", "font-weight":"normal", "font-style":"normal"}, "line": {"color":"#2aa198", "font-weight":"normal", "font-style":"normal"}, "html": {"color":"#c000c0", "font-weight":"normal", "font-style":"normal"}}
        self.setTheme(self.defaultTheme)

    def setTheme(self, theme):
        self.theme = theme
        self.MARKDOWN_KWS_FORMAT = {}

        pal = self.parent.palette()
        pal.setColor(QPalette.Base, QColor(theme['background-color']))
        self.parent.setPalette(pal)
        self.parent.setTextColor(QColor(theme['color']))

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['bold']['color'])))
        format.setFontWeight(QFont.Bold if theme['bold']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['bold']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Bold'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['bold']['color'])))
        format.setFontWeight(QFont.Bold if theme['bold']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['bold']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['uBold'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['emphasis']['color'])))
        format.setFontWeight(QFont.Bold if theme['emphasis']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['emphasis']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Italic'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['emphasis']['color'])))
        format.setFontWeight(QFont.Bold if theme['emphasis']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['emphasis']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['uItalic'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['link']['color'])))
        format.setFontWeight(QFont.Bold if theme['link']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['link']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Link'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['image']['color'])))
        format.setFontWeight(QFont.Bold if theme['image']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['image']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Image'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['header']['color'])))
        format.setFontWeight(QFont.Bold if theme['header']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['header']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['Header'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['header']['color'])))
        format.setFontWeight(QFont.Bold if theme['header']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['header']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HeaderAtx'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['unorderedlist']['color'])))
        format.setFontWeight(QFont.Bold if theme['unorderedlist']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['unorderedlist']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['UnorderedList'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['orderedlist']['color'])))
        format.setFontWeight(QFont.Bold if theme['orderedlist']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['orderedlist']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['OrderedList'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['blockquote']['color'])))
        format.setFontWeight(QFont.Bold if theme['blockquote']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['blockquote']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['BlockQuote'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['codespan']['color'])))
        format.setFontWeight(QFont.Bold if theme['codespan']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['codespan']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeSpan'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['codeblock']['color'])))
        format.setFontWeight(QFont.Bold if theme['codeblock']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['codeblock']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['CodeBlock'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['line']['color'])))
        format.setFontWeight(QFont.Bold if theme['line']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['line']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HR'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['line']['color'])))
        format.setFontWeight(QFont.Bold if theme['line']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['line']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['eHR'] = format

        format = QTextCharFormat()
        format.setForeground(QBrush(QColor(theme['html']['color'])))
        format.setFontWeight(QFont.Bold if theme['html']['font-weight']=='bold' else QFont.Normal)
        format.setFontItalic(True if theme['html']['font-style']=='italic' else False)
        self.MARKDOWN_KWS_FORMAT['HTML'] = format

        self.rehighlight()

    def highlightBlock(self, text):
        text = str(text)
        self.highlightMarkdown(text,0)
        self.highlightHtml(text)

    def highlightMarkdown(self, text, strt):
        cursor = QTextCursor(self.document())
        bf = cursor.blockFormat()
        self.setFormat(0, len(text), QColor(self.theme['color']))
        #bf.clearBackground()
        #cursor.movePosition(QTextCursor.End)
        #cursor.setBlockFormat(bf)

        #Block quotes can contain all elements so process it first
        self.highlightBlockQuote(text, cursor, bf, strt)

        #If empty line no need to check for below elements just return
        if self.highlightEmptyLine(text, cursor, bf, strt):
            return

        #If horizontal line, look at pevious line to see if its a header, process and return
        if self.highlightHorizontalLine(text, cursor, bf, strt):
            return

        if self.highlightAtxHeader(text, cursor, bf, strt):
            return

        self.highlightList(text, cursor, bf, strt)

        self.highlightLink(text, cursor, bf, strt)

        self.highlightImage(text, cursor, bf, strt)

        self.highlightCodeSpan(text, cursor, bf, strt)

        self.highlightEmphasis(text, cursor, bf, strt)

        self.highlightBold(text, cursor, bf, strt)

        self.highlightCodeBlock(text, cursor, bf, strt)

    def highlightBlockQuote(self, text, cursor, bf, strt):
        found = False
        mo = re.search(self.MARKDOWN_KEYS_REGEX['BlockQuote'],text)
        if mo:
            self.setFormat(mo.start(), mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['BlockQuote'])
            unquote = re.sub(self.MARKDOWN_KEYS_REGEX['BlockQuoteCount'],'',text)
            spcs = re.match(self.MARKDOWN_KEYS_REGEX['BlockQuoteCount'],text)
            spcslen = 0
            if spcs:
                spcslen = len(spcs.group(0))
            self.highlightMarkdown(unquote,spcslen)
            found = True
        return found

    def highlightEmptyLine(self, text, cursor, bf, strt):
        textAscii = str(text.replace(u'\u2029','\n'))
        if textAscii.strip():
            return False
        else:
            return True

    def highlightHorizontalLine(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['HR'],text):
            prevBlock = self.currentBlock().previous()
            prevCursor = QTextCursor(prevBlock)
            prev = prevBlock.text()
            prevAscii = str(prev.replace(u'\u2029','\n'))
            if prevAscii.strip():
                #print "Its a header"
                prevCursor.select(QTextCursor.LineUnderCursor)
                #prevCursor.setCharFormat(self.MARKDOWN_KWS_FORMAT['Header'])
                formatRange = QTextLayout.FormatRange()
                formatRange.format = self.MARKDOWN_KWS_FORMAT['Header']
                formatRange.length = prevCursor.block().length()
                formatRange.start = 0
                prevCursor.block().layout().setAdditionalFormats([formatRange])
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HR'])

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['eHR'],text):
            prevBlock = self.currentBlock().previous()
            prevCursor = QTextCursor(prevBlock)
            prev = prevBlock.text()
            prevAscii = str(prev.replace(u'\u2029','\n'))
            if prevAscii.strip():
                #print "Its a header"
                prevCursor.select(QTextCursor.LineUnderCursor)
                #prevCursor.setCharFormat(self.MARKDOWN_KWS_FORMAT['Header'])
                formatRange = QTextLayout.FormatRange()
                formatRange.format = self.MARKDOWN_KWS_FORMAT['Header']
                formatRange.length = prevCursor.block().length()
                formatRange.start = 0
                prevCursor.block().layout().setAdditionalFormats([formatRange])
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HR'])
        return found

    def highlightAtxHeader(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['HeaderAtx'],text):
            #bf.setBackground(QBrush(QColor(7,54,65)))
            #cursor.movePosition(QTextCursor.End)
            #cursor.mergeBlockFormat(bf)
            self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HeaderAtx'])
            found = True
        return found

    def highlightList(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['UnorderedList'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['UnorderedList'])
            found = True

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['OrderedList'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['OrderedList'])
            found = True
        return found

    def highlightLink(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Link'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Link'])
            found = True
        return found

    def highlightImage(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Image'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Image'])
            found = True
        return found

    def highlightCodeSpan(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['CodeSpan'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['CodeSpan'])
            found = True
        return found

    def highlightBold(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Bold'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Bold'])
            found = True

        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['uBold'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['uBold'])
            found = True
        return found

    def highlightEmphasis(self, text, cursor, bf, strt):
        found = False
        unlist = re.sub(self.MARKDOWN_KEYS_REGEX['UnorderedListStar'],'',text)
        spcs = re.match(self.MARKDOWN_KEYS_REGEX['UnorderedListStar'],text)
        spcslen = 0
        if spcs:
            spcslen = len(spcs.group(0))
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Italic'],unlist):
            self.setFormat(mo.start()+strt+spcslen, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['Italic'])
            found = True
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['uItalic'],text):
            self.setFormat(mo.start()+strt, mo.end() - mo.start()-strt, self.MARKDOWN_KWS_FORMAT['uItalic'])
            found = True
        return found

    def highlightCodeBlock(self, text, cursor, bf, strt):
        found = False
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['CodeBlock'],text):
            stripped = text.lstrip()
            if stripped[0] not in ('*','-','+','>'):
                self.setFormat(mo.start()+strt, mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['CodeBlock'])
                found = True
        return found

    def highlightHtml(self, text):
        for mo in re.finditer(self.MARKDOWN_KEYS_REGEX['Html'], text):
            self.setFormat(mo.start(), mo.end() - mo.start(), self.MARKDOWN_KWS_FORMAT['HTML'])
