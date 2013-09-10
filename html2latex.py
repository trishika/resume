#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Produces a latex file from an html file. And might work with
pdflatex afterwards.
"""

import sys
import os
import re
from argparse import ArgumentParser, RawTextHelpFormatter as hlpfmt


def main():
    parser = ArgumentParser(description=__doc__, formatter_class=hlpfmt)
    parser.add_argument('html_file', help='input file ("-" for stdin)')
    parser.add_argument('-o', '--outfile', help='output file ("-" for stdout)')
    args = parser.parse_args()

    if args.html_file == '-':
        text = sys.stdin.read()
    else:
        try:
            text = open(args.html_file).read()
        except IOError as e:
            sys.exit('Cannot open file %s : %s' % (args.html_file, e))

    if not args.outfile or args.outfile == '-':
        fout = sys.stdout
    else:
        if os.path.exists(args.outfile):
            sys.exit('Output file %s already exists. Exiting.' % args.outfile)
        fout = open(args.outfile, 'wt')

    # Remove all before "<body>"
    m = re.search('<body.*?>', text, re.IGNORECASE)
    text = text[m.end():]

    # Process text
    text = replace_begins(text)
    text = replace_ends(text)
    text = cleanup(text)

    # Output results
    fout.write(text)

def replace_begins(text):
    "Return text with replacements like  <h1> --> \section{  etc"

    html2tex = {
        'sup': '$^{\\textrm{',
        'font': '',
        'div': '',
        'span': '',
        'p': '\n',
        'b': '\\textbf{',
        'i': '\\textit{',
        'u': '\\underline{',
        'dt': '\\item[',
        'dd': ']',
        'br': '',
        'em': '\\emph{',
        'h1': '\\section{',
        'h2': '\\subsection{',
        'h3': '\\subsubsection{',
        'h4': '\\paragraph{',
        'h5': '\\subparagraph{',
        'h6': '\\subparagraph{',
        'li': '\\item ',
        'ul': '\\begin{itemize}',
        'ol': '\\begin{enumerate}',
        'dl': '\\begin{description}',
        'tt': '\\texttt{',
        'kbd': '{\\tt\\bf ',
        'va': '\\textit{',
        'dfn': '{\\bf\\it ',
        'cite': '{\\sc ',
        'samp': '\\texttt{',
        'strong': '\\textbf{',
        'listing': '\\begin{verbatim}',
        'code': '\\texttt{',
        'pre': '\\begin{verbatim}',
        'blockquote': '\\begin{quotation}'}

    last = 0
    text_new = ''
    for m in re.finditer('<([^/ >]+)(.*?)>', text):
        tag, args = m.groups()

        if tag.lower() == 'img':
            text_new += text[last:m.start()]
            src = re.search('src=["\'](.*?)["\']', args, flags=re.IGNORECASE)
            name = re.search('name=["\'](.*?)["\']', args, flags=re.IGNORECASE)
            text_new += """
\\begin{figure}
\\centering
\\includegraphics{%s}
\\caption{%s}
\\end{figure}

\\clearpage
""" % (src.groups()[0].replace('.gif', '.png') if src else '',
       name.groups()[0] if name else '')
            last = m.end()
        elif tag.lower() == 'a':
            text_new += text[last:m.start()]
            m2 = re.search('href=["\'](http.*)["\']', args, flags=re.IGNORECASE)
            if m2:
                text_new += ' \url{%s} ' % m2.groups()[0]
            last = m.end()
        else:
            text_new += text[last:m.start()] + html2tex[tag.lower()]
            last = m.end()
    text_new += text[last:]

    return text_new



def replace_ends(text):
    "Return text with replacements like  </h1> --> }  etc"

    html2tex = {
        'sup': '}}$',
        'font': '',
        'div': '',
        'span': '',
        'body': '',
        'html': '',
        'a': '',
        'p': '\n\n',
        'ul': '\\end{itemize}',
        'ol': '\\end{enumerate}',
        'dl': '\\end{description}',
        'listing': '\\end{verbatim}',
        'pre': '\\end{verbatim}',
        'blockquote': '\\end{quotation}'}

    last = 0
    text_new = ''
    for m in re.finditer('</(.+?)>', text):
        tag = m.groups()[0]
        text_new += text[last:m.start()] + html2tex.get(tag.lower(), '}')
        last = m.end()
    text_new += text[last:]

    return text_new



def cleanup(text):
    "Return text without triple spaces, etc"

    text = re.sub('\n\n+', '\n\n', text)
    text = text.replace('&amp;', '\\&')
    text = text.replace('&quot;', '"')
    text = text.replace('&nbsp;', ' ')
    #text = text.replace('―', '---')
    #text = text.replace('─', '--')
    #text = text.replace('─', '--')
    #text = text.replace('…', '...')
    #text = text.replace('´', "'")
    #text = text.replace('', '')

    text = re.sub(r'\\[A-Za-z]+?{[ \t\n]*}', '', text)  # remove empty fields
    text = re.sub('([^{])(https?://[^ \n\t"\']+)', '\\1\\url{\\2}', text)
    text = text.strip()

    return text



if __name__ == '__main__':
    main()
