#from bparser import *
#from intbase import *
from fundamental_defs import ValueDef, StatementType

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
        if cur == None or cur == True or cur == False:
            return False
        return isinstance(cur, int) or \
                (cur.isdigit() or (cur[1:].isdigit() and cur[0] == '-'))
    
    def is_string(self, cur):
        if cur == None or cur == True or cur == False or isinstance(cur, int):
            return False
        return cur[0] == '\"' and cur[-1] == '\"'
    
    def is_expression(self, cur):
        exp_starts = {'+', '-', '*', '/', 
                      '>','<','==','!=', 
                      '>=', '<=', '&', '|'
                      ,'!'}
        # bool function that checks to see if cur is an expression
        return (isinstance(cur, list) and cur[0] in exp_starts)

    def __handle_expression(self, expression):
        # returns the result of the computed expression!
        if len(expression) < 2:
            print("Expression length is not long enough. Needs to have at least an op and a value")
        elif len(expression) == 2:
            op, a = expression[0:2]
            b = None
        else:
            op, a, b = expression[0:3]
        
        # need to verify that a or b is not another list
        if self.is_expression(a):
            a = self.__handle_expression(a)
        if b and self.is_expression(b):
            b = self.__handle_expression(b)
        
        # check to see if a or b is a field or parameter STILL NEED TO ADD PARAMETER CHECKING HERE!!
        if a in self.fields:
            a = str(self.fields[a].value)
        if b in self.fields:
            b = str(self.fields[b].value)

        # if a or b is a number convert to an int
        if self.is_number(a):
            a = int(a)
        if b and self.is_number(b):
            b = int(b)

        # if a or b is a bool, convert to a bool
        if a == "true":
            a = True
        if a == "false":
            a = False
        if b == "true":
            b = True
        if b == "false":
            b = False
        #print("OPAB: ",op, a, b)
        #print(self.is_string(a))
        #print(self.is_number(a))
        #print(self.is_string(b))
        #print(self.is_number(b))
        # op, a and b are now all valid
        res = self.simple_calculate(a,b,op)
        return res
        
    def simple_calculate(self, a, b, op):
        one_op = (b == None)
        two_op = (a != None and b!= None)
        a_is_bool = isinstance(a, bool)
        b_is_bool = isinstance(b, bool)
        a_is_int = (isinstance(a, int) and not a_is_bool)
        b_is_int = (isinstance(b, int) and not b_is_bool)
        a_is_string = self.is_string(a)
        b_is_string = self.is_string(b)

        if one_op:
            if op == "!":
                if a_is_bool:
                    return not a
                else:
                    print(a)
                    print("Error with the not operator")
        elif two_op:
            if a_is_string and b_is_string:
                a = a.strip('"')
                b = b.strip('"')
                if op == "+": # concat
                    return a + b
                else:
                    print("Unsupported operation between strings")
            elif a_is_int and b_is_int:
                if op == "+":
                    return a + b
                elif op == "*":
                    return a * b
                elif op == "/":
                    return a//b # int division
                elif op == "-":
                    return a - b
                elif op == ">":
                    return a > b
                elif op == "<":
                    return a < b
                elif op == "<=":
                    return a<=b
                elif op == ">=":
                    return a>=b
                elif op == "==":
                    return a == b
                else:
                    print(op, a, b)
                    print("Unsupported operation between ints")
            elif a_is_bool and b_is_bool:
                if op == "!=":
                    return a != b
                elif op == "==":
                    return a == b
                elif op == "&":
                    return a and b
                elif op == "|":
                    return a or b
                else:
                    print("Unsupported operation between bools")
            else:
                print(a)
                print(b)
                print("Expression: The type of a and b is not consistent")
        else:
            return "Expression ERROR, operation not supported"

    def __execute_print(self, statement, interpreter):
        to_print = ""
        for arg in statement.args:
            cur = arg
            if not isinstance(arg, list):
                cur = arg.strip('\'')
            
            if self.is_expression(cur):
                res = self.__handle_expression(cur)
                if isinstance(res, bool):
                    if res:
                        res = "true"
                    else:
                        res = "false"
                else:
                    res = str(res)
                to_print += res
            elif self.is_string(cur):
                #print("DEBUG:IS A STRING")
                to_print += cur.strip('"')
            elif self.is_number(cur): # if cur is an integer (positive or negative)
                #print("DEBUG:Is a number!")
                to_print += cur
            elif cur == "true" or cur == "false":
                #print("DEBUG:Is a bool")
                to_print += cur
            elif cur in self.fields:
                #print("DEBUG:Is a field.")
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
        
        # if value_to_set is an expression evaluate it!
        if self.is_expression(value_to_set):
            value_to_set = self.__handle_expression(value_to_set)
            if isinstance(value_to_set, bool):
                if value_to_set:
                    value_to_set = "true"
                else:
                    value_to_set = "false"

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