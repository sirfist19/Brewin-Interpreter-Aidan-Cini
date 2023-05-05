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


class ClassDef:
    # constructor for a ClassDefinition
    def __init__(self, name):
        self.name = name
        self.methods = {} # a dict of MethodDefs of name to the method
        self.fields = {} # a dictionary of variables of names to values
    
    def add_method(self, method): # method should be of type MethodDef
        self.methods[method.name] = method

    def add_field(self, field): # field should be of type VariableDef (I think...)
        self.fields[field.name] = field.value

    # uses the definition of a class to create and return an instance of it
    
    def instantiate_object(self):
        obj = ObjectDef(self.name)
        for method in self.methods.values():
            obj.add_method(method)
        for field_name, field_value in self.fields.items():
            #obj.add_field(field.name(), field.initial_value())
            obj.add_field(field_name, field_value)
        return obj
    
class ExpressionDef:
    pass

class ObjectDef: # the instanciation of a class
    def __init__(self, name):
        self.name = name
        self.methods = {}
        self.fields = {}

    def add_method(self, method): # method should be of type MethodDef
        self.methods[method.name] = method

    def add_field(self, field_name, field_value): # field should be of type VariableDef (I think...)
        self.fields[field_name] = field_value

    def __find_method(self, method_name):
        return self.methods[method_name] # returns the method itself

    def __find_field(self, field_name):
        return self.fields[field_name] # returns the value of the field
    
    # Interpret the specified method using the provided parameters
    #def call_method(self, method_name, parameters):
    #    method = self.__find_method(method_name)
    #    statement = method.get_top_level_statement()
    #    result = self.__run_statement(statement)
    #    return result
    
    # runs the method (currently SIMPLISTIC)
    def run_method(self, method_name, interpreter):
        method = self.__find_method(method_name)
        #statement = method.get_top_level_statement()
        result = self.__run_statement(method.statement, interpreter)
        return result 
    
    def __execute_inputs(self, statement, interpreter):
        #get string input
        temp = interpreter.get_input()
        #temp = input()
        if not self.is_string(temp):
            print("Not instance of a string inputed to inputs")
        
        input_var_name = statement.args[0]

        # the input_var_name could be a fxn param or a field name

        # for Field name
        if input_var_name in self.fields: # if the field name exists then set the field to that value
            self.fields[input_var_name] = ValueDef(type(temp), temp)
            return True
        return False

    def __execute_inputi(self, statement, interpreter):
        #get string input
        temp = interpreter.get_input()
        #temp = input()
        if not self.is_number(temp):
            print("Not instance of an int inputed to inputi")
            #raise RuntimeError
        
        input_var_name = statement.args[0]

        # the input_var_name could be a fxn param or a field name

        # for Field name
        if input_var_name in self.fields: # if the field name exists then set the field to that value
            self.fields[input_var_name] = ValueDef(type(temp), temp)
            return True
        return False
    
    def is_number(self, cur):
        return cur.isdigit() or (cur[1:].isdigit() and cur[0] == '-')
    
    def is_string(self, cur):
        return cur[0] == '\"' and cur[-1] == '\"'
    
    def __execute_print(self, statement, interpreter):
        to_print = ""
        for arg in statement.args:
            cur = arg.strip('\'')

            # if cur is a string
            if self.is_string(cur):
                #print("IS A STRING")
                to_print += cur.strip('"')

            # if cur is an integer (positive or negative)
            elif self.is_number(cur):
                #print("Is a number!")
                to_print += cur
            elif cur == "true" or cur == "false":
                to_print += cur
            elif cur in self.fields:
                to_print += str(self.fields[cur].value)
            else:  
                print(f"ERROR: Unknown arg to print: {cur}")
                #exit(1) 
        interpreter.output(to_print)
        #print(to_print)
        return True
    
    def __execute_begin(self, statement, interpreter):
        sub_statements = statement.args
        if len(sub_statements) == 0:
            print("ERROR: Cannot have an empty begin statement.")
            #exit(1)
        for statement in sub_statements:
            self.__run_statement(statement, interpreter)
        return True
    
    def __execute_set(self, statement):
        var_name, value_to_set = statement.args[0], statement.args[1]
        
        # the variable to set could be in either self.fields or a parameter

        # if a field
        if var_name in self.fields:
            self.fields[var_name] = ValueDef(type(value_to_set), value_to_set)
            return True
        # elif a parameter
        return False
    
    # runs/interprets the passed-in statement until completion and gets the result, if any
    def __run_statement(self, statement, interpreter):
        if statement.statement_type == StatementType.PRINT:
            return self.__execute_print(statement, interpreter)
        elif statement.statement_type == StatementType.BEGIN:
            return self.__execute_begin(statement, interpreter)
        elif statement.statement_type == StatementType.CALL:
            return True
        elif statement.statement_type == StatementType.WHILE:
            return True
        elif statement.statement_type == StatementType.RETURN:
            return True
        elif statement.statement_type == StatementType.INPUTI:
            return self.__execute_inputi(statement, interpreter)
        elif statement.statement_type == StatementType.INPUTS:
            return self.__execute_inputs(statement, interpreter)
        elif statement.statement_type == StatementType.IF:
            return True
        elif statement.statement_type == StatementType.SET:
            return self.__execute_set(statement)
        return False
        
        '''
            Pseudocode from the spec
        
        if is_a_print_statement(statement):
            result = self.__execute_print_statement(statement)
        elif is_an_input_statement(statement):
            result = self.__execute_input_statement(statement)
        elif is_a_call_statement(statement):
            result = self.__execute_call_statement(statement)
        elif is_a_while_statement(statement):
            result = self.__execute_while_statement(statement)
        elif is_an_if_statement(statement):
            result = self.__execute_if_statement(statement)
        elif is_a_return_statement(statement):
            result = self.__execute_return_statement(statement)
        elif is_a_begin_statement(statement):
            result = self.__execute_all_sub_statements_of_begin_statement(statement)
        #...
        return result
        '''

    
 