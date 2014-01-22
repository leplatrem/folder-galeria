# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import os
import logging
import optparse
from gettext import gettext as _
from collections import namedtuple
import json

try:
    from jinja2 import Environment
except ImportError, e:
    print _("Error: %s, install with:") % e
    print "sudo apt-get install python-jinja2"
    exit()



logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'folder-galeria.tmpl')
PICTURE_EXT = ('jpg', 'png', 'jpeg')

Folder = namedtuple('Folder', ['name', 'list'])
Picture = namedtuple('Picture', ['path', 'name'])


def list_pictures(path, basepath='', excludes=None, minsize=-1):
    """ Returns a list of files/folders names ordered by time desc. """
    imglist = []
    for name in os.listdir(path):
        if name in (excludes or []):
            continue

        filename = os.path.join(path, name)
        if os.path.isdir(filename):
            sublist = list_pictures(filename, name, excludes, minsize)
            imglist.append(Folder(name, sublist))
            continue

        basename, ext = os.path.splitext(name)
        if ext[1:].lower() not in PICTURE_EXT:
            continue

        picture = Picture(os.path.join(basepath, name),
                          basename.decode('utf-8'))
        imglist.append(picture)
    imglist.sort()
    imglist.reverse()
    return imglist


def preprocess_galeria(listing, urlprefix):
    data = []
    for image in images:
        if isinstance(image, Folder):
            item = {
                'gallery': image.name,
                #'data': preprocess_galeria(image.list, urlprefix)
            }
        else:
            url = os.path.join(urlprefix, image.path)
            item = {
                'thumb': url,
                'image': url,
                'big': url,
                'title': image.name
            }
        data.append(item)
    return data


def render_page(images, output=None, title="", urlprefix=""):
    """ Render the Web page to the specified output """
    data = preprocess_galeria(images, urlprefix)

    env = Environment(extensions=['jinja2.ext.i18n'])
    env.install_null_translations()
    with open(TEMPLATE_PATH) as tpl:
        template = env.from_string(tpl.read().decode('utf-8'))
    # Default output is stdout
    out = open(output, 'w') if output else sys.stdout
    context = {
        'pictures': json.dumps(data),
        'title': title
    }
    page = template.render(**context)
    out.write(page.encode('ascii', 'xmlcharrefreplace'))
    out.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    parser = optparse.OptionParser(usage='%prog [options] FOLDER',
                                   description=_("Generates a fancy Web page"
                                                 "from a folder with pictures"))
    parser.add_option("-o", "--output",
                      dest="output", default=None,
                      help=_("Output to file"))
    parser.add_option("-x", "--exclude",
                      dest="exclude", default="",
                      help=_("Exclude files or folders by name (comma-separated)"))
    parser.add_option("-u", "--url-prefix",
                      dest="urlprefix", default="",
                      help=_("URL prefix for images"))
    parser.add_option("-t", "--title",
                      dest="title", default="Folder Galeria",
                      help=_("Specify page title"))
    (options, args) = parser.parse_args(sys.argv)
    if len(args) < 2:
        parser.print_help()
        parser.exit()
    folder = args[1]

    images = list_pictures(folder, excludes=options.exclude.split(","))
    render_page(images,
                options.output,
                options.title.decode('utf-8'),
                options.urlprefix)
