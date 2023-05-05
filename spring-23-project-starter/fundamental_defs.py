from bparser import *
from intbase import *

'''
 THIS FILE HAS CLASS DEFINITIONS FOR BREWIN'
 - VALUES
 - VARIABLES
 - STATEMENTS
 - FUNCTIONS/METHODS
 - CLASSES
 - OBJECTS
 
'''
class ValueDef:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class VariableDef:
    def __init__(self, name, value):
        self.name = name
        self.value = value # of type ValueDef

class StatementType(Enum):
    IF = 1
    BEGIN = 2
    PRINT = 3
    SET = 4
    INPUTI = 5
    INPUTS = 6
    CALL = 7
    WHILE = 8
    RETURN = 9

class StatementDef:
    # if, begin, print, set, inputi, inputs, call, while, return
    #def __init__(self, statement_type, args):
    #    self.statement_type = statement_type
    #    self.args = args # if it is a begin statement the args are themselves statements

    def __init__(self, statement_data):
        statement_type, args = self.create_statement(statement_data)
        self.statement_type = statement_type
        self.args = args 

    def create_statement(self, statement_data):
        if statement_data[0] == InterpreterBase.PRINT_DEF:
            #handle print statement
            return (StatementType.PRINT, statement_data[1:])
        elif statement_data[0] == InterpreterBase.BEGIN_DEF:
            args = []
            sub_statements = statement_data[1:]
            for sub in sub_statements:
                args.append(StatementDef(sub))
            return (StatementType.BEGIN, args)
        elif statement_data[0] == InterpreterBase.CALL_DEF:
            return (StatementType.CALL, statement_data[1:])
        elif statement_data[0] == InterpreterBase.WHILE_DEF:
            return (StatementType.WHILE, statement_data[1:])
        elif statement_data[0] == InterpreterBase.RETURN_DEF:
            return (StatementType.RETURN, statement_data[1:])
        elif statement_data[0] == InterpreterBase.INPUT_INT_DEF:
            return (StatementType.INPUTI, statement_data[1:])
        elif statement_data[0] == InterpreterBase.INPUT_STRING_DEF:
            return (StatementType.INPUTS, statement_data[1:])
        elif statement_data[0] == InterpreterBase.SET_DEF:
            return (StatementType.SET, statement_data[1:])
        elif statement_data[0] == InterpreterBase.IF_DEF:
            return (StatementType.IF, statement_data[1:])
        else:
            print("Unrecognized statement!")
            print(statement_data)
            #exit(1)

class MethodDef:
    def __init__(self, name, parameters, statement):
        self.name = name
        self.parameters = parameters
        self.statement = statement

class ExpressionDef: # NOT IMPLEMENTED YET
    pass

