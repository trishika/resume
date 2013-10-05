#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
    CV generator
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Aurélien Chabot <aurelien@chabot.fr>
    :license: LGPLv3, see COPYING for more details.
"""
try:
    from docutils.core import publish_string,publish_parts
    from docutils.writers.html4css1 import Writer,HTMLTranslator
    from distutils import dir_util
    import ConfigParser
    import jinja2
    import time
    import sys
    import os
    import re
    from html2latex import replace_begins
    from html2latex import replace_ends
    from html2latex import cleanup
except ImportError as error:
    print 'ImportError: ', str(error)
    exit(1)

# Settings

config = ConfigParser.RawConfigParser()
config.read('site.cfg')

SITE = {
    "url"         : config.get('SITE', 'url' ),
    "title"       : config.get('SITE', 'title' ),
    "author"      : config.get('SITE', 'author' ),
    "description" : config.get('SITE', 'description' ),
    "job"         : config.get('SITE', 'job' )
}

INPUT = './content/'
OUTPUT = './www/'
TEMPLATE_PATH = './templates/'
TEMPLATE_OPTIONS = {}
LANG = "en"

# Parser

def html2latex(text):
    text = replace_begins(text)
    text = replace_ends(text)
    text = cleanup(text)
    return text

# Stuff

STEPS = []

def step(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    STEPS.append(wrapper)
    return wrapper

def write_file(url, data):
    path = OUTPUT + url
    dirs = os.path.dirname(path)
    if not os.path.isdir(dirs):
        os.makedirs(dirs)
    with open(path, 'w') as f:
        f.write(data.encode('UTF-8'))

def parse_file(path, name):

    if not re.match(r'^[0-9].+\.(en)$', name):
        return None

    with open(path, 'rU') as f:
        label = f.readline()
        #name = re.sub(r'\.[^\.]+$', '', path.replace(source, ''))
        print '  -', name
        f.readline()
        content = ''
        content += ''.join(f.readlines()).decode('UTF-8')
        return {'title': name,
                'label': label,
                'content': content}

def get_name(path,folder):

    try:
        with open(os.path.join(path,folder,"name."+LANG), 'rU') as f:
            return f.readline().replace("\n","")

    except IOError:
        print "[WARNING] No name file, use folder name"
        return folder


def get_tree(source):
    cats = []

    for f in sorted(os.listdir(source), reverse=True) :

        if os.path.isdir(source+f):
            print " * ", f

            files = []
            subcats = []
            cats.append({'name':get_name(source,f),
                         'fields':files,
                         'subcats':subcats})

            for f2 in sorted(os.listdir(os.path.join(source+f)), reverse=True):

                p2 = os.path.join(source,f,f2)
                if os.path.isdir(p2):
                    print " ** ", f2
                    subcat_files = []
                    subcats.append({'name':get_name(os.path.join(source,f),f2),
                                    'fields':subcat_files})

                    for f3 in sorted(os.listdir(p2), reverse=True):

                        p3 = os.path.join(source,f,f2,f3)
                        if not os.path.isdir(p3):
                            field_content = parse_file(p3,f3)
                            if field_content != None:
                                subcat_files.append(field_content)
                else:

                    field_content = parse_file(p2,f2)
                    if field_content != None:
                        files.append(field_content)

    return cats

def rest2html(text):
    return publish_parts(source=text,writer_name='html')['body']

def generate_html(e, f, env, name):
    print '  %s%s -> %s%s' % (TEMPLATE_PATH, name, OUTPUT, name)
    template = e.get_template(name)

    if f != None:
        for cat in f:
            if cat["fields"] != None:
                for field in cat["fields"]:
                    print(field["content"])
                    field["content"] = rest2html(field["content"])
                    print field["content"]
            if cat["subcats"] != None:
                for subcat in cat["subcats"]:
                    for field in subcat["fields"]:
                        field["content"] = rest2html(field["content"])
                        #print field["content"]

    write_file(name, template.render({'cats':f, 'site':env}))

def rest2tex(text):
    return publish_parts(source=text,writer_name='latex')['body']

def generate_tex(e, f, env, name):
    print '  %s%s -> %s%s' % (TEMPLATE_PATH, name, OUTPUT, name)
    template = e.get_template(name)

    if f != None:
        for cat in f:
            if cat["fields"] != None:
                for field in cat["fields"]:
                    print(field["content"])
                    field["content"] = rest2tex(field["content"])
                    print field["content"]
            if cat["subcats"] != None:
                for subcat in cat["subcats"]:
                    for field in subcat["fields"]:
                        field["content"] = rest2tex(field["content"])
                        #print field["content"]

    write_file(name, template.render({'cats':f, 'site':env}))

@step
def step_index(e):
    generate_html(e, None, SITE, "index.html")

@step
def step_cv(e):
    f = get_tree(INPUT)
    generate_html(e, f, SITE, "cv.html")

def step_cv_tex(e):
    f = get_tree(INPUT)
    generate_tex(e, f, SITE, "cv.tex")

@step
def step_chabot(e):
    generate_html(e, None, {'url': 'chabot.fr'}, "chabot.html")

if __name__ == '__main__':

    print '* Generating HTML...'
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_PATH), **TEMPLATE_OPTIONS)
    for step in STEPS:
        step(env)
    print 'Browse at: <%s>' % (SITE['url'])

    print '* Generating LaTeX...'

    LATEX_SUBS = (
        (re.compile(r'\\'), r'\\textbackslash'),
        (re.compile(r'([{}_#%&$])'), r'\\\1'),
        (re.compile(r'~'), r'\~{}'),
        (re.compile(r'\^'), r'\^{}'),
        (re.compile(r'"'), r"''"),
        (re.compile(r'\.\.\.+'), r'\\ldots'),
    )

    def escape_tex(value):
        newval = value
        for pattern, replacement in LATEX_SUBS:
            newval = pattern.sub(replacement, newval)
        return newval

    latex_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
        block_start_string = '\BLOCK{',
        block_end_string = '}',
        variable_start_string = '\VAR{',
        variable_end_string = '}',
        comment_start_string = '\#{',
        comment_end_string = '}',
        line_statement_prefix = '%-',
        line_comment_prefix = '%#',
        trim_blocks = True,
        autoescape = False,
    )

    latex_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH),
        block_start_string = '((*',
        block_end_string = '*))',
        variable_start_string = '(((',
        variable_end_string = ')))',
        comment_start_string = '((=',
        comment_end_string = '=))',
        line_statement_prefix = '%-',
        line_comment_prefix = '%#',
        trim_blocks = True,
        autoescape = False,
    )

    step_cv_tex(latex_env)
