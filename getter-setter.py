import sublime
import sublime_plugin
import re
import os
import json

class Prefs:
    """
        Plugin preferences
    """
    @staticmethod
    def getSettingsFile():
        try:
            file = os.path.join(Prefs.packagePath, "php-getters-setters.sublime-settings")

            c = open(file).read()
            c = re.sub(r"//.*\n",'', c)
            c = re.sub(r"/\*.*\*/",'', c)

            settings = json.loads(c)

            return settings
        except Exception, e :
            print "Can not load settings", e
            return {}


    @staticmethod
    def load():
        """
            just because sublime.load_settings() does not goes well with spaces in folder names
        """

        Prefs.packagePath = os.path.join(sublime.packages_path(), "PHP Getters and Setters")

        settings = Prefs.getSettingsFile()


        if 'type_hint_ignore' in settings :
            Prefs.typeHintIgnore = "%s" %settings['type_hint_ignore']
        else:
            Prefs.typeHintIgnore = []



Prefs.load()

class Template(object):
    def __init__(self, name):
        self.content = open(os.path.join(Prefs.packagePath, "templates", name)).read()

    def replace(self, args):
        return self.content % args


class DocBlock(object):
    """
        docblock text to a class
    """
    def __init__(self):
        self.tags = {}
        self.description = ''

    def hasTag(self, name) :
        return name in self.tags

    def hasDescription(self):
        return len(self.description) > 0

    def addTag(self, name, value):
        self.tags[name] = value

    def getTag(self, name):
        if not self.hasTag(name):
            return None

        return self.tags[name]

    def setDescription(self, value):
        self.description = value

    def getDescription(self):
        return self.description

    def fromText(self, content):
        lines = content.split("\n")
        description = []

        for line in lines:
            line = line.strip(' */')
            if (line.startswith('@')) :
                [name, value] = line.split()
                self.addTag(name.strip('@'), value)
            else:
                if len(line) > 0:
                    description.append(line)

        self.setDescription("\n".join(description).rstrip("\n"))

class Parser(object):
    """
        parses text to get class variables so that make the magic can happen
    """
    def __init__(self, content):
        self.content        = content
        self.functionRegExp = ".*function.*%s"
        self.variableRegExp = '((?:private|public|protected)[ ]{0,}(?:final)?[ ]{0,}(?:\$.*?)[ |=|;].*)\n'

    def getContent(self):
        return self.content

    def hasFunction(self, name):
        """
            returns true if the function with the name _name_ is found in the code
        """
        content = self.getContent()
        regExp = self.functionRegExp % name

        return re.search(regExp, content) is not None

    def _getDockBlockOfVariable(self, line):
        content = self.getContent()
        matchPos = content.find(line)



        lineByLine = content[:matchPos].split("\n")
        lineByLine.reverse()
        commentStart = 0
        commentEnd = 0

        for n in range(len(lineByLine)) :
            line = lineByLine[n].strip()
            if "\n" == line :
                continue

            elif "\r\n" == line :
                continue

            elif "" == line :
                continue

            elif '*/' == line :
                commentStart = n +1

            elif '/**' == line :
                commentEnd = n
                break

            elif 0 == commentStart:
                break


        if commentStart == commentEnd :
            return ""

        if (commentStart == 0) or (commentEnd == 0) :
            return ""

        result = lineByLine[commentStart:commentEnd]
        result.reverse()

        return "\n".join(result)

    def _processVariable(self, line):
        """
            Returns a Variable object populated from the parsed code
        """
        nameMatches = re.findall('\$(.*?)[ |=|;]', line)
        name = "Unknown"
        if len(nameMatches) >= 0 :
            name = nameMatches[0]

        dockBlockText = self._getDockBlockOfVariable(line)
        docblock = DocBlock()
        docblock.fromText(dockBlockText)

        typeName = 'mixed'
        if docblock.hasTag('var'):
            typeName    =  docblock.getTag('var')
        description = docblock.getDescription()

        return Variable(name = name, typeName = typeName, description = description)

    def getClassVariables(self):
        """
            returns a list of Variable objects, created from the parsed code
        """
        content       = self.getContent()
        variablesList = []

        matches = re.findall(self.variableRegExp, content,  re.IGNORECASE)
        for match in matches :
            variable = self._processVariable(match)
            variablesList.append(variable)

        return variablesList

class Variable(object):
    def __init__(self, name, typeName = None, description=None):
        self.name        = name
        self.type        = typeName
        self.description = description

    def getName(self):
        return self.name

    def getDescription(self):
        if self.description is None or "" == self.description:
            self.description = 'value of %s' %self.getName() #get description from name
        return self.description

    def getGetterFunctionName(self, style = 'camelCase'):
        return "get%s" %self.getName().title()

    def getSetterFunctionName(self, style = 'camelCase'):
        return "set%s" %self.getName().title()

    def getType(self):
        return self.type

    def GetTypeHint(self):
        if self.type in Prefs.typeHintIgnore :
            return ''

        return self.type



class Base(sublime_plugin.TextCommand):
    def __init__(self, arg):
        sublime_plugin.TextCommand.__init__(self, arg)
        self.variables = None
        self.parser = None

    def getContent(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def getParser(self, content = ''):
        self.parser = Parser(content)

        return  self.parser

    def findLastBracket(self):
        view =self.view
        pos = long(0)
        lastPos = 0
        while pos is not None:
            pos = view.find('\}', pos);

            if pos is not None:
                lastPos = pos
                if type(pos) == sublime.Region:
                    pos = pos.end()

        return lastPos.begin()

    def getVariables(self, parser):
        filename = self.view.file_name()
        parser = self.getParser(open(filename).read())
        self.variables = parser.getClassVariables()

        return self.variables

    def generateFunctionCode(self, template, variable):
        substitutions = {
            "name"           : variable.getName(),
            "type"           : variable.getType(),
            "normalizedName" : variable.getName().title(),
            "description"    : variable.getDescription(),
            "typeHint"       : variable.GetTypeHint()
        }

        return template.replace(substitutions)

    def generateGetterFunction(self, parser, variable):

        if parser.hasFunction(variable.getGetterFunctionName()):
            print "function %s already present, skipping" % variable.getGetterFunctionName()
            return ''

        template = Template('getter.tpl')
        code = self.generateFunctionCode(template, variable)

        return code

    def generateSetterFunction(self, parser, variable):

        if parser.hasFunction(variable.getSetterFunctionName()):
            print "function %s already present, skipping" % variable.getSetterFunctionName()
            return ''

        template = Template('setter.tpl')
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

class PhpGenerateGettersCommand(Base):
    def run(self, edit):
        parser = self.getParser(self.getContent())
        code = ''
        for variable in parser.getClassVariables():
            code += self.generateGetterFunction(parser, variable)

        self.writeAtEnd(edit, code)

class PhpGenerateSettersCommand(Base):
    def run(self, edit):
        parser = self.getParser(self.getContent())
        code = ''
        for variable in parser.getClassVariables():
            code += self.generateSetterFunction(parser, variable)

        self.writeAtEnd(edit, code)

class PhpGenerateGettersSettersCommand(Base):
    def run(self, edit):

        parser = self.getParser(self.getContent())
        code = ''
        for variable in parser.getClassVariables():
            code += self.generateGetterFunction(parser, variable)
            code += self.generateSetterFunction(parser, variable)

        self.writeAtEnd(edit, code)


class PhpGenerateGettersSetterUnavailable(Base):
    def run(self, edit):
        pass

    def is_enabled(self):
        return False

    def is_visible(self):
        return not self.isPhpSyntax()

    def description(self):
        return "Only available for PHP syntax buffers"