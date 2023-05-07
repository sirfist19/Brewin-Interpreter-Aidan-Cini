from bparser import *
from intbase import *
from fundamental_defs import ValueDef, StatementType, StatementDef
import copy

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
        if method_name in self.methods:
            return self.methods[method_name] # returns the method itself
        return None
    
    # runs the method (currently SIMPLISTIC)
    def run_method(self, method_name, param_values, interpreter):
        method = self.__find_method(method_name)

        if method:
            if len(param_values) != len(method.param_map.keys()):
                print("Wrong number of args provided to fxn call")
                interpreter.error(ErrorType.TYPE_ERROR)
            method.set_method_values(param_values)
            #print("method_map from run_method: ", method.param_map)
            result = self.__run_statement(method.statement, method.param_map, interpreter)
            return result 
        else:
            print("Cannot find function to run!")
            interpreter.error(ErrorType.NAME_ERROR)
    
    def __execute_inputs(self, statement, params, interpreter):
        #get string input
        temp = interpreter.get_input()
        if not self.is_string(temp):
            print("Not instance of a string inputed to inputs")
        
        input_var_name = statement.args[0]

        # the input_var_name could be a fxn param or a field name

        # for Field name and parameters
        if input_var_name in params:
            params[input_var_name] = temp
        elif input_var_name in self.fields: # if the field name exists then set the field to that value
            self.fields[input_var_name] = ValueDef(type(temp), temp)
            #return True
        #return False

    def __execute_inputi(self, statement, params, interpreter):
        #get string input
        temp = interpreter.get_input()
        #temp = input()
        if not self.is_number(temp):
            print("Not instance of an int inputed to inputi")
            #raise RuntimeError
        
        input_var_name = statement.args[0]

        # the input_var_name could be a fxn param or a field name

        # for Field and parameters 
        if input_var_name in params:
            params[input_var_name] = temp
        elif input_var_name in self.fields: # if the field name exists then set the field to that value
            self.fields[input_var_name] = ValueDef(type(temp), temp)
            #return True
        #return False
    
    def is_number(self, cur):
        if not isinstance(cur, int) and \
                (cur == None or cur == True or cur == False):
            return False
        return isinstance(cur, int) or \
                (cur.isdigit() or (cur[1:].isdigit() and cur[0] == '-'))
    
    def is_string(self, cur):
        if cur == None or \
            cur == True or \
                cur == False or \
                    isinstance(cur, int) or \
                        isinstance(cur, ObjectDef):
            return False
        return cur[0] == '\"' and cur[-1] == '\"'
    
    def is_expression(self, cur):
        exp_starts = {'+', '-', '*', '/', 
                      '>','<','==','!=', 
                      '>=', '<=', '&', '|'
                      ,'!', '%', 'call', 'new'}
        # bool function that checks to see if cur is an expression
        return (isinstance(cur, list) and cur[0] in exp_starts)

    def __handle_expression(self, expression, params, interpreter):
        # handling the call expression
        if expression[0] == InterpreterBase.CALL_DEF:
            # Ex: (print (call me echo 5)) -> the call statement
            call_statement = StatementDef(expression)
            res = self.__run_statement(call_statement, params, interpreter)
            #print("res from __handle_expression: ", res)
            return res
        
        # handling the new expression
        if expression[0] == InterpreterBase.NEW_DEF:
            # instantiate the required class
            new_class_name = expression[1]
            new_class = interpreter.find_definition_for_class(new_class_name)
            new_object = new_class.instantiate_object()
            return new_object
        
        # returns the result of the computed expression!
        if len(expression) < 2:
            print("Expression length is not long enough. Needs to have at least an op and a value")
        elif len(expression) == 2:
            op, a = expression[0:2]
            b = None
        else:
            op, a, b = expression[0:3]
        
        # check to see if a or b is a field or parameter 
        if not isinstance(a, list):
            if a in params:
                a = params[a]
            if a in self.fields:
                a = self.fields[a].value
            elif not self.is_string(a) and \
                not self.is_number(a) and \
                a != None and \
                a != True and a != False and a != "true" and a != "false" and a != "null":
                print("unknown variable in expression", a)
                interpreter.error(ErrorType.NAME_ERROR)
        if not isinstance(b, list):
            if b in params:
                b = params[b]
            elif b in self.fields:
                b = self.fields[b].value
            elif not self.is_string(b) and \
                not self.is_number(b) and \
                b != None and \
                b != True and b != False and b != "true" and b != "false" and b != "null":
                print("unknown variable in expression", b)
                interpreter.error(ErrorType.NAME_ERROR)


        # need to verify that a or b is not another list
        if self.is_expression(a):
            a = self.__handle_expression(a, params, interpreter)
        if b and self.is_expression(b):
            b = self.__handle_expression(b, params, interpreter)
        
        
        # HANDLE IF A FIELD IS SPECIFIED BUT DOESN'T EXIST
        
        # if a or b is a number convert to an int
        if isinstance(a, str) and self.is_number(a):
            a = int(a)
        if b and isinstance(b, str) and self.is_number(b):
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
        if a == "null":
            a = None
        if b == "null":
            b = None

        #print("OPAB: ",op, a, b)
        #print("Params: ", params)
        # op, a and b are now all valid
        res = self.simple_calculate(a,b,op, interpreter)
        return res
        
    def simple_calculate(self, a, b, op, interpreter):
        one_op = (b == None)
        two_op = (a != None and b!= None)
        a_is_bool = isinstance(a, bool)
        b_is_bool = isinstance(b, bool)
        a_is_obj = isinstance(a, ObjectDef)
        b_is_obj = isinstance(b, ObjectDef)
        a_is_int = (isinstance(a, int) and not a_is_bool)
        b_is_int = (isinstance(b, int) and not b_is_bool)
        a_is_string = self.is_string(a)
        b_is_string = self.is_string(b)
        a_is_none = (a == None)
        b_is_none = (b == None)
        
        if (a_is_none and b_is_none) or (a_is_none and b_is_obj) or (b_is_none and a_is_obj):
                if op == "==":
                    return a == b
                elif op == "!=":
                    return a != b
                else:
                    print("Unsupported operation between nulls")
                    interpreter.error(ErrorType.TYPE_ERROR)

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
                    interpreter.error(ErrorType.TYPE_ERROR)
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
                elif op == "!=":
                    return a != b
                elif op == "%":
                    return a % b
                else:
                    print(op, a, b)
                    print("Unsupported operation between ints")
                    interpreter.error("ErrorType.TYPE_ERROR")
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
                    interpreter.error("ErrorType.TYPE_ERROR")
            elif a_is_obj and b_is_obj:
                if op == "!=":
                    return a != b
                elif op == "==":
                    return a == b
                else:
                    print("Unsupported operation between objects")
                    interpreter.error("ErrorType.TYPE_ERROR")
            else:
                print(a)
                print(b)
                interpreter.error("ErrorType.TYPE_ERROR")
                print("Expression: The type of a and b is not consistent")
        else:
            return "Expression ERROR, operation not supported"

    def __execute_print(self, statement, params, interpreter):
        to_print = ""
        
        for arg in statement.args:
            cur = arg
            if not isinstance(arg, list):
                cur = arg.strip('\'')
            
            if self.is_expression(cur):
                res = self.__handle_expression(cur, params, interpreter)
                if isinstance(res, bool):
                    if res:
                        res = "true"
                    else:
                        res = "false"
                else:
                    res = str(res)
                to_print += res
                continue

            from_param_or_field = False
            if cur in params:
                #print("Param_map: ", params)
                cur = params[cur]
                from_param_or_field = True
                #print("q: ", cur)
            elif cur in self.fields:
                #print("DEBUG:Field: ", cur, self.fields[cur].value)
                cur = self.fields[cur].value
                from_param_or_field = True
            
            if isinstance(cur, ObjectDef) :
                to_print += str(cur)
            elif cur == None and from_param_or_field:
                to_print += str(cur)
            elif self.is_string(cur) or (from_param_or_field and isinstance(cur, str)):
                #print("DEBUG:IS A STRING")
                to_print += cur.strip('"')
            elif self.is_number(cur): # if cur is an integer (positive or negative)
                #print("DEBUG:Is a number!")
                to_print += str(cur)
            elif cur == "true" or cur == "false":
                #print("DEBUG:Is a bool")
                to_print += cur
            else:  
                print(f"ERROR: Unknown arg to print: {cur}", type(cur))
                interpreter.error(ErrorType.NAME_ERROR)
                #exit(1) 
        interpreter.output(to_print)
        #print(to_print)
        #return True
    
    def __execute_begin(self, statement, params, interpreter):
        sub_statements = statement.args
        if len(sub_statements) == 0:
            print("ERROR: Cannot have an empty begin statement.")
            #exit(1)
        res = None
        for statement in sub_statements:
            res = self.__run_statement(statement, params, interpreter)
            #print("res1: ", res)
            if res:
                return res
        #print("res2: ", res)
        #return res # if there is nothing to return return none
    
    def __execute_set(self, statement, params, interpreter):
        var_name, value_to_set = statement.args[0], statement.args[1]

        # if value_to_set is null then set it to None
        if value_to_set == "null":
            value_to_set = None
        # if value_to_set is an expression evaluate it!
        elif self.is_expression(value_to_set):
            value_to_set = self.__handle_expression(value_to_set, params, interpreter)
            if isinstance(value_to_set, bool):
                if value_to_set:
                    value_to_set = "true"
                else:
                    value_to_set = "false"
        # the value could refer to a field or parameter
        elif value_to_set in params:
            value_to_set = params[value_to_set]
        elif value_to_set in self.fields:
            value_to_set = self.fields[value_to_set].value

        # the variable to set could be in either self.fields or a parameter
        # if a parameter
        if var_name in params:
            params[var_name] = value_to_set
        # if a field
        elif var_name in self.fields:
            self.fields[var_name] = ValueDef(type(value_to_set), value_to_set)
            #return True
        else:
            print("Setting an unknown variable")
            interpreter.error(ErrorType.NAME_ERROR)
        #return False
    
    def __execute_if(self, statement, params, interpreter):
        # Overall Brewin' syntax
        # if with no else
        # (if expression (run_if_expr_is_true)) 
        # ['if', ['==', 'x', '7'], ['print', '"lucky seven"']]

        # if with else
        # (if expression (run_if_expr_is_true) (run_if_expr_is_false))
        # ['if', 'true', ['print', '"that\'s true"'], ['print', '"this won\'t print"']]
        #print("Evaluating if statement!")

        expression = statement.args[0] # statement.args should be [expression,if_clause, else_clause]
        if_clause = statement.args[1]
        else_clause = None
        if len(statement.args) >= 3:
            else_clause = statement.args[2]
        
        #print("Expression: ", expression)
        #print("If clause: ", if_clause)
        #print("Else clause: ", else_clause)

        # handle the expression
        expression_val = self.__execute_expession(expression, params, interpreter)

        # return the statement specified by the result of the expression
        if expression_val == True and isinstance(expression_val, bool): 
            if_clause = StatementDef(if_clause)
            return self.__run_statement(if_clause, params, interpreter) # execute if_clause
        elif expression_val == False and isinstance(expression_val, bool):
            if else_clause != None:
                else_clause = StatementDef(else_clause)
                return self.__run_statement(else_clause, params, interpreter) # execute else_clause
        else:
            interpreter.error(ErrorType.TYPE_ERROR)
            print("ERROR: If Expression did not result in a Boolean")
    
    def __execute_while(self, statement, params, interpreter):
        # Syntax
        # (while expression statement_to_run_while_expression_is_true)
        # ['while', [expression], [statement_to_run_while_expression_is_true]]
        
        condition = statement.args[0]
        statement_to_run = StatementDef(statement.args[1])

        while True: # NEED TO DEAL WITH RETURNS IN THE WHILE STATEMENT
            res = self.__execute_expession(condition, params, interpreter) #execute the condition
            #print("Cond res: ", res)
            #print("Fields: ", [(key,val.value) for key,val in self.fields.items()])
            if res == True and isinstance(res, bool):
                # run the statement
                return_res = self.__run_statement(statement_to_run, params, interpreter) # execute if_clause
                #print("Return res: ", return_res)
                if return_res:
                    return return_res
            elif res == False and isinstance(res, bool):
                break # exit the while loop
            else:
                interpreter.error(ErrorType.TYPE_ERROR)
                print("ERROR: Expression in while loop did not result in a Boolean")
    
    def __execute_expession(self, expression, params, interpreter):
        expression_val = expression

        # if the expression is a param
        if not isinstance(expression, list) and expression in params:
            return params[expression]
        # if the expression is a field
        if not isinstance(expression, list) and expression in self.fields:
            #print("REturning: ", self.fields[expression].value)
            return self.fields[expression].value
        # if the expression is not a constant and needs to be further evaluated
        if self.is_expression(expression):
            expression_val = self.__handle_expression(expression, params, interpreter)
        
        # if the expression is a bool convert to python bool
        if expression_val == "true":
            expression_val = True
        elif expression_val == "false":
            expression_val = False
        elif isinstance(expression_val, str) and self.is_number(expression_val):
            expression_val = int(expression_val)
        elif isinstance(expression_val, int) \
                or isinstance(expression_val, bool) \
                or self.is_string(expression_val):
            #print("Alt:", expression_val)
            return expression_val
        else:
            print("error with expression value: ", expression_val)  
            interpreter.error(ErrorType.NAME_ERROR)
        return expression_val
    
    def __execute_call(self, statement, old_params, interpreter):
        #print("Parsing a call statement")
        # Syntax
        # (call target_object method_name param1 ... paramn)
        # Ex: (call me bar 5)
        obj_to_call_name = statement.args[0]
        
        params = []
        if len(statement.args) > 2:
            params = statement.args[2:]
        #print("Printing from __execute_call", obj_to_call_name, func_to_call, params)
        
        # params could be from a field or the old parameters or could be an expression
        for i in range(len(params)):
            if self.is_expression(params[i]):
                params[i] = self.__execute_expession(params[i], old_params, interpreter) 
            elif params[i] in self.fields: # handle field
                params[i] = self.fields[params[i]].value
            elif params[i] in old_params: # handle param
                params[i] = old_params[params[i]]
        #print("Old_params: ", old_params, params)

        # call me
        if obj_to_call_name == InterpreterBase.ME_DEF:
            func_to_call = statement.args[1]
            res = self.run_method(func_to_call, params, interpreter)
            #print("From exec call: ", res)
            return res
        # otherwise look in the fields (where the value of the field is set to the class)
        for name, obj in self.fields.items():
            #print(name, obj_to_call_name)
            if name == obj_to_call_name:
                obj_to_call = obj.value
                if obj_to_call == None:
                    print("Cannot call function on null object!")
                    interpreter.error(ErrorType.FAULT_ERROR) 
                func_to_call = statement.args[1]
                return obj_to_call.run_method(func_to_call, params, interpreter)
        
        # if the object is not found in a field or is itself
        print("Object to call function on not found or the object is null!")
        interpreter.error(ErrorType.FAULT_ERROR) 
        
    def __execute_return(self, statement, params, interpreter):
        #print("args: ", statement.args)
        if len(statement.args) == 0: # for the (return) statement
            return None
        expression_to_return = statement.args[0]
        #print("expression_to_return", expression_to_return, params)
        res = self.__execute_expession(expression_to_return, params, interpreter) #execute the condition
        #print("res: ", res)
        return res
    
    # runs/interprets the passed-in statement until completion and gets the result, if any
    def __run_statement(self, statement, params, interpreter):
        if statement.statement_type == StatementType.PRINT:
            #print("exec print")
            return self.__execute_print(statement, params, interpreter)
        elif statement.statement_type == StatementType.BEGIN:
            return self.__execute_begin(statement, params, interpreter)
        elif statement.statement_type == StatementType.CALL:
            return self.__execute_call(statement, params, interpreter)
        elif statement.statement_type == StatementType.WHILE:
            return self.__execute_while(statement, params, interpreter)
        elif statement.statement_type == StatementType.RETURN:
            res = self.__execute_return(statement, params, interpreter)
            #print("q: ", res)
            return res
        elif statement.statement_type == StatementType.INPUTI:
            return self.__execute_inputi(statement, params, interpreter)
        elif statement.statement_type == StatementType.INPUTS:
            return self.__execute_inputs(statement, params, interpreter)
        elif statement.statement_type == StatementType.IF:
            return self.__execute_if(statement, params, interpreter)
        elif statement.statement_type == StatementType.SET:
            return self.__execute_set(statement, params, interpreter)
        print("Statement type error!")
        return None