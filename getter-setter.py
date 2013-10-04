import sublime
import sublime_plugin
import re
import os
import json

def msg(msg):
    print "[PHP Getters and Setters] %s" % msg

class Prefs:
    """
        Plugin preferences
    """

    @staticmethod
    def load():
        settings = sublime.load_settings('php-getters-setters.sublime-settings')

        Prefs.typeHintIgnore = settings.get('type_hint_ignore')

        templatePath = settings.get('templates')
        if False == os.path.isabs(templatePath) :
            templatePath = os.path.join(sublime.packages_path(), "PHP Getters and Setters", templatePath)
        Prefs.templates =  templatePath

        Prefs.style =  settings.get('style')

        msg ("ignored type hinting var types %s" % Prefs.typeHintIgnore)
        msg ("code style is %s" % Prefs.style)
        msg ("templates are in %s" % Prefs.templates)




Prefs.load()

class Template(object):
    def __init__(self, name, style = "camelCase"):

        msg("opening template %s" % os.path.join(Prefs.templates, style, name))

        self.content = open(os.path.join(Prefs.templates, style, name)).read()

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
                nameMatches = re.findall('\@(\w+) (:?.*)[ ]?.*', line)
                if len(nameMatches) > 0 :
                    name = nameMatches[0][0]
                    value = nameMatches[0][1]

                    self.addTag(name.strip('@'), value)
                # [name, value, other] = line.split(" ", 2)
                else:
                    msg("Error: could not parse line %s" %line)

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
        self.variableRegExp = '((?:private|public|protected)[ ]{0,}(?:final|static)?[ ]{0,}(?:\$.*?)[ |=|;].*)\n'

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

    def getPartialFunctionName(self):
        style = Prefs.style
        # print style
        name = self.getName()
        name = name.lstrip('_')
        if 'camelCase' == style :
            var = name[0].upper() + name[1:]
        else :
            var = name

        return var

    def getGetterFunctionName(self):
        style = Prefs.style
        if 'camelCase' == style :
            return "get%s" % self.getPartialFunctionName()

        return "get_%s" % self.getPartialFunctionName()

    def getSetterFunctionName(self):
        style = Prefs.style
        if 'camelCase' == style :
            return "set%s" % self.getPartialFunctionName()

        return "set_%s" % self.getPartialFunctionName()

    def getType(self):
        return self.type

    def GetTypeHint(self):
        if self.type in Prefs.typeHintIgnore :
            return ''

        if self.type.find(" ") > -1 or self.type.find("|") > -1:
            msg("'%s' is more thatn one type, switching to no type hint" % self.type)
            return ""

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
            "nameVar"        : variable.getName().lstrip('_'),
            "type"           : variable.getType(),
            "normalizedName" : variable.getPartialFunctionName(),
            "description"    : variable.getDescription(),
            "typeHint"       : variable.GetTypeHint()
        }

        return template.replace(substitutions)

    def generateGetterFunction(self, parser, variable):

        if parser.hasFunction(variable.getGetterFunctionName()):
            msg("function %s already present, skipping" % variable.getGetterFunctionName())
            return ''

        template = Template('getter.tpl', Prefs.style)
        code = self.generateFunctionCode(template, variable)

        return code

    def generateSetterFunction(self, parser, variable):

        if parser.hasFunction(variable.getSetterFunctionName()):
            msg("function %s already present, skipping" % variable.getSetterFunctionName())
            return ''

        template = Template('setter.tpl', Prefs.style)
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

class PhpGenerateFor(Base):
    what = 'getter'


    def run(self, edit):
        self.edit = edit

        parser = self.getParser(self.getContent())

        self.vars = []

        for variable in parser.getClassVariables():
            item =[ variable.getName(), variable.getDescription( )]
            self.vars.append(item)

        self.view.window().show_quick_panel(self.vars, self.write)

    def write(self, index):
        name = self.vars[index][0]
        parser = self.getParser(self.getContent())
        for variable in parser.getClassVariables():
            if name == variable.getName():
                if 'getter' == self.what :
                    code = self.generateGetterFunction(parser, variable)
                else:
                    code = self.generateSetterFunction(parser, variable)
                self.writeAtEnd(self.edit, code)

class PhpGenerateGetterForCommand(PhpGenerateFor):
    what = 'getter'

class PhpGenerateSetterForCommand(PhpGenerateFor):
    what = 'setter'


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