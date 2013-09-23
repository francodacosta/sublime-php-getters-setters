import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__))
    )
)

import utils
import os

def msg(msg):
    print ("[PHP Getters and Setters] %s" % msg)

class Template(object):
    def __init__(self, name, style = "camelCase"):

        Prefs = utils.Prefs()

        utils.msg("opening template %s" % os.path.join(Prefs.templates, style, name))

        self.content = open(os.path.join(Prefs.templates, style, name)).read()

    def replace(self, args):
        return self.content % args
