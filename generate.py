#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    CV generator
    ~~~~~~~~~~~~

    :copyright: (c) 2013 by Aurélien Chabot <aurelien@chabot.fr>
    :license: LGPLv3, see COPYING for more details.
"""
try:
    from distutils import dir_util
    import configparser
    import jinja2
    import time
    import sys
    import os
    import re
    import codecs
except ImportError as error:
    print('ImportError: ' + str(error))
    exit(1)

# Settings

config = configparser.RawConfigParser()
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
    with codecs.open(path, mode='w', encoding='utf-8') as f:
        f.write(data)

def parse_file(path, name):

    if not re.match(r'^[0-9].+\.(en)$', name):
        return None

    with codecs.open(path, mode='rU', encoding='utf-8') as f:
        label = f.readline()
        #name = re.sub(r'\.[^\.]+$', '', path.replace(source, ''))
        print('    - ' + name)
        f.readline()
        content = ''
        content += ''.join(f.readlines())
        return {'title': name,
                'label': label,
                'content': content}

def get_name(path,folder):

    try:
        with open(os.path.join(path,folder,"name."+LANG), 'rU') as f:
            return f.readline().replace("\n","")

    except IOError:
        print("[WARNING] No name file, use folder name")
        return folder


def get_tree(source):
    cats = []

    for f in sorted(os.listdir(source), reverse=True) :

        if os.path.isdir(source+f):
            print(" * " + f)

            files = []
            subcats = []
            cats.append({'name':get_name(source,f),
                         'fields':files,
                         'subcats':subcats})

            for f2 in sorted(os.listdir(os.path.join(source+f)), reverse=True):

                p2 = os.path.join(source,f,f2)
                if os.path.isdir(p2):
                    print("  ** " + f2)
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

def generate(e, f, env, name):
    print('  %s%s.html -> %s%s.html' % (TEMPLATE_PATH, name, OUTPUT, name))
    template = e.get_template(name + '.html')
    write_file(name + '.html', template.render({'cats':f, 'site':env}))

@step
def step_index(e):
    generate(e, None, SITE, "index")

@step
def step_cv(e):
    f = get_tree(INPUT)
    generate(e, f, SITE, "cv")

#@step
def step_chabot(e):
    generate(e, None, {'url': 'chabot.fr', 'title' : 'chabot.fr', 'author' : 'Aurélien Chabot' }, "chabot")

if __name__ == '__main__':
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_PATH), **TEMPLATE_OPTIONS)
    print('* Generating HTML...')
    for step in STEPS:
        step(env)
    print('Browse at: <%s>' % (SITE['url']))

