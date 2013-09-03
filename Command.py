import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__))
    )
)

import sublime
import sublime_plugin
import sys
import re
from Parser import *
from Template import *
import utils

class Base(sublime_plugin.TextCommand):
    def __init__(self, arg):
        sublime_plugin.TextCommand.__init__(self, arg)
        self.variables = None
        self.parser = None
        self.Prefs = utils.Prefs()

    def getContent(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def getParser(self, content = ''):
        self.parser = Parser(content)

        return  self.parser

    def findLastBracket(self):
        view =self.view
        if sys.version > '3' :
            pos = 0
        else :
            pos = long(0)
        lastPos = 0

        pos = view.find('\{', 0)

        while pos.begin() != lastPos:
            pos = view.find('\}', pos.end());
            utils.msg(pos)
            lastPos = pos.begin()


        return lastPos

    def getVariables(self, parser):
        filename = self.view.file_name()
        parser = self.getParser(open(filename).read())
        self.variables = parser.getClassVariables()

        return self.variables

    def generateFunctionCode(self, template, variable):
        substitutions = {
            "name"           : variable.getName(),
            "type"           : variable.getType(),
            "normalizedName" : variable.getPartialFunctionName(),
            "description"    : variable.getDescription(),
            "typeHint"       : variable.GetTypeHint(),
            "humanName"      : variable.getHumanName()
        }

        return template.replace(substitutions)

    def generateGetterFunction(self, parser, variable):

        if parser.hasFunction(variable.getGetterFunctionName()):
            utils.msg("function %s already present, skipping" % variable.getGetterFunctionName())
            return ''

        template = Template('getter.tpl', self.Prefs.style)
        code = self.generateFunctionCode(template, variable)

        return code

    def generateSetterFunction(self, parser, variable):

        if parser.hasFunction(variable.getSetterFunctionName()):
            utils.msg("function %s already present, skipping" % variable.getSetterFunctionName())
            return ''

        template = Template('setter.tpl', self.Prefs.style)
        code = self.generateFunctionCode(template, variable)
        # if type hinting is not to be show we get "( " instead of (
        code = code.replace('( ', '(')

        return code

    def writeAtEnd(self, edit, text):
        lastPos = self.findLastBracket()
        self.view.insert(edit, lastPos, text)

    def isPhpSyntax(self):
        return re.search(".*\PHP.tmLanguage", self.view.settings().get('syntax')) is not None

    def is_enabled(self):
        return self.isPhpSyntax()

    def is_visible(self):
        return self.is_enabled()
