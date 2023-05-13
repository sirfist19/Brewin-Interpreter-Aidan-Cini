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
class VariableDef:
    def __init__(self, name, value, type_):
        self.name = name
        self.value = value # of type ValueDef
        self.type = type_ # should by of type DataType

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

class BaseDataType(Enum):
    INT = 1
    STRING = 2
    BOOL = 3
    VOID = 4 # only a return data type ... if a function is marked this it either has (return) or no return statement
    OBJECT = 5

    def str_to_data_type(in_type):
        if in_type == 'void':
            return BaseDataType.VOID
        elif in_type == 'int':
            return BaseDataType.INT
        elif in_type == 'bool':
            return BaseDataType.BOOL
        elif in_type == 'string':
            return BaseDataType.STRING
        else:
            #print("str_to_data_type input is ", in_type, ". Converting to DataType.OBJECT")
            return BaseDataType.OBJECT
    def get_default_value(dataType):
        if dataType == BaseDataType.INT:
            return 0
        elif dataType == BaseDataType.STRING:
            return ""
        elif dataType == BaseDataType.BOOL:
            return False
        elif dataType == BaseDataType.OBJECT:
            return NullType(True) # is_null is true
        elif dataType == BaseDataType.VOID:
            print("ERROR: Getting default value for void")
            return None
        else:
            print("ERROR: Translating unrecognized data type")

class DataType:
    def __init__(self, base_data_type, class_name = ""):
        self.base_data_type = base_data_type
        if base_data_type == BaseDataType.OBJECT:
            self.class_name = class_name
        else:
            self.class_name = ""

class NullType(): # to return from (return) and (return null)
        def __init__(self, is_null): 
            self.is_null = is_null # if null is returned this is true, 
                    #if returning from an empty return, this is false

class StatementDef:
    # if, begin, print, set, inputi, inputs, call, while, return
    #def __init__(self, statement_type, args):
    #    self.statement_type = statement_type
    #    self.args = args # if it is a begin statement the args are themselves statements

    def __init__(self, statement_data):
        statement_type, args = self.create_statement(statement_data)
        self.type = statement_type
        self.args = args 

    def create_statement(self, statement_data): # statement data is the list of everything that will be the statement
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

class MethodDef:
    def __init__(self, name, 
                 param_map_name_to_value, 
                 param_map_name_to_type, 
                 statement, 
                 return_type):
        self.name = name
        self.param_map_name_to_value = param_map_name_to_value # of variable names to values -> initially all vars are set to None
        self.param_map_name_to_type = param_map_name_to_type
        self.statement = statement
        self.return_type = return_type

    def set_method_values(self, method_values):
        # method_values is all of the values that are passed into the fxn
        # set the values of each of the items in the param map to the method_values by index

        param_name_list = list(self.param_map_name_to_value.keys())
        for i in range(len(method_values)):
            required_type = self.param_map_name_to_type[param_name_list[i]]
            print("Required type: ", required_type.base_data_type, method_values[i])

            # if the passed in value is false or true, convert it to a python bool
            if method_values[i] == InterpreterBase.FALSE_DEF:
                method_values[i] = False
            elif method_values[i] == InterpreterBase.TRUE_DEF:
                method_values[i] = True

            # set the value to the value provided (type check is before)
            self.param_map_name_to_value[param_name_list[i]] = method_values[i]

            
