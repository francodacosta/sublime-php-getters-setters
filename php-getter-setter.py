import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__))
    )
)

from utils import *
from Command import *

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
