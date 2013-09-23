import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__))
    )
)

import re
import utils

def msg(msg):
    print ("[PHP Getters and Setters] %s" % msg)

# self.Prefs.load()

class Variable(object):
    def __init__(self, name, typeName = None, description=None):
        self.name        = name
        self.type        = typeName
        self.description = description
        self.Prefs       = utils.Prefs()

    def getName(self):
        return self.name

    def getHumanName(self):
        style = self.Prefs.style
        name = self.getName()

        if 'camelCase' == style :
            name = ' '.join(re.findall('(?:[A-Z]|^)[^A-Z]*', name)).lower()
        else :
            name = name.replace('_', ' ')

        return name

    def getDescription(self):
        if self.description is None or "" == self.description:
            self.description = 'value of %s' %self.getName() #get description from name
        return self.description

    def getPartialFunctionName(self):
        style = self.Prefs.style
        # print style
        name = self.getName()

        if 'camelCase' == style :
            var = name[0].upper() + name[1:]
        else :
            var = name

        return var

    def getGetterFunctionName(self):
        style = self.Prefs.style
        if 'camelCase' == style :
            return "get%s" % self.getPartialFunctionName()

        return "get_%s" % self.getPartialFunctionName()

    def getSetterFunctionName(self):
        style = self.Prefs.style
        if 'camelCase' == style :
            return "set%s" % self.getPartialFunctionName()

        return "set_%s" % self.getPartialFunctionName()

    def getType(self):
        return self.type

    def GetTypeHint(self):
        if self.type in self.Prefs.typeHintIgnore :
            return ''

        if self.type.find(" ") > -1 or self.type.find("|") > -1:
            msg("'%s' is more than one type, switching to no type hint" % self.type)
            return ""

        return self.type


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
            line = line.strip(' \t*/')
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
