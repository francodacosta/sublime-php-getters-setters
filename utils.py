import sublime
import os

def msg(msg):
    print ("[PHP Getters and Setters] %s" % msg)

class Prefs:
    """
        Plugin preferences
    """
    def __init__(self):
        self.load()

    def load(self):
        settings = sublime.load_settings('php-getters-setters.sublime-settings')

        self.typeHintIgnore = settings.get('type_hint_ignore')
        msg ("ignored type hinting var types %s" % self.typeHintIgnore)

        self.style =  settings.get('style')
        msg ("code style is %s" % self.style)

        templatePath = settings.get('templates', './')
        if False == os.path.isabs(templatePath) :
            msg ('template %s' % templatePath)
            templatePath = os.path.join(sublime.packages_path(), "PHP Getters and Setters", templatePath)
        self.templates =  templatePath

        msg ("templates are in %s" % self.templates)
