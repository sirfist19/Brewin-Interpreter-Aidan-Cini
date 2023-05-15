from bparser import *
from intbase import *
from fundamental_defs import StatementType, DataType, BaseDataType, StatementDef, NullType

def is_number(cur): # returns true if the input is an int or a string that contains an integer
        # if cur is False, True, None, or is an object, or is NullType should return False
        # if cur is an int or is a string that holds an int return True
        #OLD VERSION: if not isinstance(cur, int) and \
        #        (cur == None or cur == True or cur == False or isinstance(cur, ObjectDef)):
        if cur is False or cur is True or cur is None or isinstance(cur, ObjectDef) or isinstance(cur, NullType):    
            return False
        return isinstance(cur, int) or \
                (cur.isdigit() or (cur[1:].isdigit() and cur[0] == '-'))
    
def is_string(cur): # returns true if the string is surrounded by double quotes " "
    if cur == None or \
        cur == True or \
            cur == False or \
                isinstance(cur, int) or \
                    isinstance(cur, ObjectDef) or isinstance(cur, NullType):
        return False
    return cur == "" or (cur[0] == '\"' and cur[-1] == '\"')

def basic_type_check(input, expected_type):
        # makes sure the input is of expected type
        #   expected type is of type 
        #print(f"Input: {input}, \
        #      Expected Type: {expected_type}, ")
        expected_base_type = expected_type.base_data_type
        expected_class_name = expected_type.class_name

        if expected_base_type == BaseDataType.OBJECT: 
            if input == InterpreterBase.NULL_DEF or (isinstance(input, NullType) and input.is_null == True):
                return True
            elif isinstance(input, ObjectDef) and \
                input.name == expected_class_name: # name check for objects!
                return True
            # polymorphism type check -> check the base class to see if it is a type match
            elif isinstance(input, ObjectDef) and \
                    input.inherits_from is not None and \
                    basic_type_check(input.inherits_from, expected_type):
                print("Polymorphic type is a match!")
                return True
            elif isinstance(input, ObjectDef):
                print("ERROR: Name of object did not match!")
                return False
            else: # if an object is not passed in
                return False
        elif expected_base_type == BaseDataType.INT:
            return is_number(input)
        elif expected_base_type == BaseDataType.STRING:
            return is_string(input)
        elif expected_base_type == BaseDataType.BOOL:
            return input == InterpreterBase.TRUE_DEF \
                    or input == InterpreterBase.FALSE_DEF or input is True or input is False
        elif expected_base_type == BaseDataType.VOID:
            #print(f"Comparing {input} to VOID data type")
            return ((input == None) # no return statement
                    or 
                    (isinstance(input, NullType) and input.is_null == False) # a (return) statement
                    )
        print("ERROR: Unknown expected_type passed into basic_type_check")
        return False

class ObjectDef: # the instanciation of a class
    def __init__(self, name):
        self.name = name # should be the name of the class defined from
        self.methods = {}
        self.fields = {}
        self.fields_to_type = {}
        self.local_var_stack = []
        self.inherits_from = None # either None or ObjDef of the inherited class (as an object)

    def add_method(self, method): # method should be of type MethodDef
        self.methods[method.name] = method

    def add_field(self, field_name, field_value): 
        self.fields[field_name] = field_value
       
    def add_field_type(self, field_name, field_type):
         self.fields_to_type[field_name] = field_type

    def __find_method(self, method_name, param_values, interpreter): # also runs the method
        if method_name in self.methods and \
            self.method_matches_input_values_TYPE_CHECK(self.methods[method_name],param_values):
            # runs the method using a helper on this obj
            return self.run_method_helper(self.methods[method_name], param_values, interpreter)
        elif self.inherits_from is not None:
            return self.inherits_from.__find_method(method_name, param_values, interpreter) 
        else:
            print("Cannot find function to run ... or the input types or amounts didn't match!")
            interpreter.error(ErrorType.NAME_ERROR)
    
    def method_matches_input_values_TYPE_CHECK(self, method, input_values):
        # checks to see if the method to be called matches the argument types of the input_values provided
        num_inputs = len(input_values)
        num_expected_params = len(method.param_map_name_to_type.keys())
        if num_inputs != num_expected_params:
            print("Wrong number of args provided to fxn call")
            return False
        param_type_list = list(method.param_map_name_to_type.values())
        for i in range(num_inputs):
            cur_input = input_values[i]
            cur_expected_type = param_type_list[i]
            if not basic_type_check(cur_input, cur_expected_type):
                return False
        return True
    
    def run_method_helper(self, method, param_values, interpreter):
        # actually runs the method
        method.set_method_values(param_values)
            #print("method_map from run_method: ", method.param_map_name_to_value, method.param_map_name_to_type)
        result = self.__run_statement(method.statement, 
                                    method.param_map_name_to_value, 
                                    method.param_map_name_to_type,
                                    interpreter)
            #print("Before default typing", result, method.return_type.base_data_type)

            # add in default typing for no return statement or (return) statement
        if (result is None or (isinstance(result, NullType) and result.is_null == False)) \
                and method.return_type.base_data_type != BaseDataType.VOID:
            result = BaseDataType.get_default_value(method.return_type.base_data_type)
                #print("After default typing", result, method.return_type.base_data_type)

                # return type checking
        if basic_type_check(result, method.return_type):
            return result 
        else: 
            print(f"ERROR: After method of name {method.name} was run, the return value of {result} was not of type {method.return_type.base_data_type}")
            interpreter.error(ErrorType.TYPE_ERROR)
        

    def run_method(self, method_name, param_values, interpreter): # wrapper for find_method which actually runs the method on the object that the method came from
        res = self.__find_method(method_name, param_values, interpreter)
        return res
         
    
    def __execute_inputs(self, statement, params, params_to_type,interpreter): #get string input and set to a field or parameter w/ matching name
        temp = interpreter.get_input()
        if not is_string(temp):
            print("Not instance of a string inputed to inputs")
        
        input_var_name = statement.args[0]

        if input_var_name in params:
            params[input_var_name] = temp
        elif input_var_name in self.fields: # if the field name exists then set the field to that value
            self.fields[input_var_name] = temp 

    def __execute_inputi(self, statement, params, params_to_type, interpreter): #get integer input and set to a field or parameter w/ matching name
        temp = interpreter.get_input()
        if not is_number(temp):
            print("Not instance of an int inputed to inputi")
        
        input_var_name = statement.args[0]

        if input_var_name in params:
            params[input_var_name] = temp
        elif input_var_name in self.fields: # if the field name exists then set the field to that value
            self.fields[input_var_name] = temp 
    
    def is_expression(self, cur):
        exp_starts = {'+', '-', '*', '/', 
                      '>','<','==','!=', 
                      '>=', '<=', '&', '|'
                      ,'!', '%', InterpreterBase.CALL_DEF, InterpreterBase.NEW_DEF}
        return (isinstance(cur, list) and cur[0] in exp_starts)

    def __handle_expression(self, expression, params, params_to_type, interpreter):
        # handling the call expression
        if expression[0] == InterpreterBase.CALL_DEF:
            # Ex: (print (call me echo 5)) -> the call statement
            call_statement = StatementDef(expression)
            res = self.__run_statement(call_statement, params, params_to_type, interpreter)
            #print("res from __handle_expression: ", res)
            return res
        
        # handling the new expression
        if expression[0] == InterpreterBase.NEW_DEF:
            # instantiate the required class
            new_class_name = expression[1]
            new_class = interpreter.find_definition_for_class(new_class_name)
            new_object = new_class.instantiate_object()
            return new_object
        
        # otherwise, it is not a new or call expression and has a normal operator as the first element
        # op = operator, a = first value, b = second value
        if len(expression) < 2:
            print("Expression length is not long enough. Needs to have at least an op and a value")
        elif len(expression) == 2:
            op, a = expression[0:2]
            b = None
        else:
            op, a, b = expression[0:3]
        
        # check to see if a or b is a field or parameter or local variable
        if not isinstance(a, list):
            if self.in_local_vars(a):
                a = self.get_top_match_local_var(a)[2] # of format [TYPE, NAME, VALUE]
            elif a in params:
                a = params[a]
            elif a in self.fields:
                a = self.fields[a]
            elif not is_string(a) and \
                not is_number(a) and \
                a != None and \
                a != True and a != False and a != InterpreterBase.TRUE_DEF and a != InterpreterBase.FALSE_DEF and a != InterpreterBase.NULL_DEF:
                print("unknown variable in expression", a)
                interpreter.error(ErrorType.NAME_ERROR)
        if not isinstance(b, list):
            if self.in_local_vars(b):
                b = self.get_top_match_local_var(b)[2] # of format [TYPE, NAME, VALUE]
            if b in params:
                b = params[b]
            elif b in self.fields:
                b = self.fields[b]
            elif not is_string(b) and \
                not is_number(b) and \
                b != None and \
                b != True and b != False and b != InterpreterBase.TRUE_DEF and b != InterpreterBase.FALSE_DEF and b != InterpreterBase.NULL_DEF:
                print("unknown variable in expression", b)
                interpreter.error(ErrorType.NAME_ERROR)


        # need to verify that a or b is not another list
        if self.is_expression(a):
            a = self.__handle_expression(a, params, params_to_type,interpreter)
            if isinstance(a, str): 
                    a = '"' + a + '"' # enclose in double-quotes
        if b and self.is_expression(b):
            b = self.__handle_expression(b, params, params_to_type, interpreter)
            if isinstance(b, str): 
                    b = '"' + b + '"' # enclose in double-quotes
        
        
        # HANDLE IF A FIELD IS SPECIFIED BUT DOESN'T EXIST
        
        # if a or b is a number convert to an int
        if isinstance(a, str) and is_number(a):
            a = int(a)
        if b and isinstance(b, str) and is_number(b):
            b = int(b)

        # if a or b is a bool, convert to a bool
        if a == InterpreterBase.TRUE_DEF:
            a = True
        if a == InterpreterBase.FALSE_DEF:
            a = False
        if b == InterpreterBase.TRUE_DEF:
            b = True
        if b == InterpreterBase.FALSE_DEF:
            b = False
        if a == InterpreterBase.NULL_DEF:
            a = None
        if b == InterpreterBase.NULL_DEF:
            b = None

        # if a or b is NullType and has is_null true -> meaning it is null, convert to None
        if isinstance(a, NullType) and a.is_null == True:
            a = None
        if isinstance(b, NullType) and b.is_null == True:
            b = None

        #print("OPAB: ",op, a, b)
        #print("Params: ", params)
        # op, a and b are now all valid
        res = self.simple_calculate(a,b,op, interpreter)
        if isinstance(res, str): 
            res = '"' + res + '"' # enclose in double-quotes
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
        a_is_string = is_string(a)
        b_is_string = is_string(b)
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
                elif op == "==":
                    return a == b
                elif op == "!=":
                    return a != b
                elif op == ">":
                    return a > b
                elif op == "<":
                    return a < b
                elif op == "<=":
                    return a<=b
                elif op == ">=":
                    return a>=b
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
                    interpreter.error(ErrorType.TYPE_ERROR)
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
                    interpreter.error(ErrorType.TYPE_ERROR)
            elif a_is_obj and b_is_obj:
                if op == "!=":
                    return a != b
                elif op == "==":
                    return a == b
                else:
                    print("Unsupported operation between objects")
                    interpreter.error(ErrorType.TYPE_ERROR)
            else:
                print(a)
                print(b)
                interpreter.error(ErrorType.TYPE_ERROR)
                print("Expression: The type of a and b is not consistent")
        else:
            return "Expression ERROR, operation not supported"

    def __execute_print(self, statement, params, params_to_type, interpreter):
        to_print = ""
        
        for arg in statement.args:
            cur = arg
            #print("arg before: ", cur)
            if not isinstance(cur, list):
                cur = cur.strip('\'')
            #    print("arg after: ", cur)

            # FIRST CHECK IF THE PRINT ARG IS ACTUALLY A LOCAL VAR, THEN PARAMETER THEN FIELD, WITH THAT PRIORITY
            #   IF SO GET ITS VALUE
            from_local_var_or_param_or_field = False
            if not isinstance(cur, list) and self.in_local_vars(cur):
                data_type, name, value = self.get_top_match_local_var(cur)
                cur = value
                from_local_var_or_param_or_field = True
            if not isinstance(cur, list) and cur in params:
                #print("Param_map: ", params)
                cur = params[cur]
                from_local_var_or_param_or_field = True
                #print("q: ", cur)
            elif not isinstance(cur, list) and cur in self.fields:
                #print("DEBUG:Field: ", cur, self.fields[cur])
                cur = self.fields[cur]
                from_local_var_or_param_or_field = True

            # second check if the current print argument is actually an expression
            #   if so evaluate it!
            elif self.is_expression(cur):
                cur = self.__handle_expression(cur, params, params_to_type, interpreter)
                if isinstance(cur, bool):
                    if cur:
                        cur = InterpreterBase.TRUE_DEF
                    else:
                        cur = InterpreterBase.FALSE_DEF
                elif isinstance(cur, str): # may need to account for other data types here! 
                    cur = '"' + cur + '"' # enclose in double-quotes
                #to_print += res
            
            #print("arg before: ", cur)
            #if not isinstance(arg, list):
            #    cur = arg.strip('\'')
            #    print("arg after: ", cur)
            
            if isinstance(cur, ObjectDef) :
                to_print += str(cur)
            elif cur == None: #and from_param_or_field:
                to_print += str(cur)
            elif cur == InterpreterBase.NULL_DEF or isinstance(cur, NullType):
                to_print += str(None)
            elif is_number(cur): # if cur is an integer (positive or negative)
                #print("DEBUG:Is a number!")
                to_print += str(cur)
            elif cur == InterpreterBase.TRUE_DEF or cur == InterpreterBase.FALSE_DEF:
                #print("DEBUG:Is a bool")
                to_print += cur
            elif is_string(cur) or (from_local_var_or_param_or_field and isinstance(cur, str)):
                #print("DEBUG:IS A STRING")
                res = cur.strip('"')
                #print("Arg after strip \": ", res)
                to_print += res
            else:  
                print(f"ERROR: Unknown arg to print: {cur}", type(cur))
                interpreter.error(ErrorType.NAME_ERROR)
        interpreter.output(to_print)
        #print(to_print)
    
    def __execute_begin(self, statement, params, params_to_type, interpreter):
        sub_statements = statement.args
        if len(sub_statements) == 0:
            print("ERROR: Cannot have an empty begin statement.")
        res = None
        for statement in sub_statements:
            res = self.__run_statement(statement, params, params_to_type, interpreter)
            #print("res1: ", res, statement.type, statement.args)
            if res != None and statement.type != StatementType.CALL: # if in a call statement do not return the value unless in a return statement itself
                return res
        #print("res2: ", res)
        #return res # if there is nothing to return return none
    
    def __execute_set(self, statement, params, params_to_type, interpreter):
        var_name, value_to_set = statement.args[0], statement.args[1]
        #print("NAME and VALUE:",var_name, value_to_set)
        #print(self.local_var_stack)
        # if value_to_set is null then set it to None
        if value_to_set == InterpreterBase.NULL_DEF:
            value_to_set = NullType(True) # True to set the is_null field in NullType to True
        # if value_to_set is an expression evaluate it!
        elif self.is_expression(value_to_set):
            value_to_set = self.__handle_expression(value_to_set, params, params_to_type, interpreter)
            if isinstance(value_to_set, bool):
                if value_to_set:
                    value_to_set = InterpreterBase.TRUE_DEF
                else:
                    value_to_set = InterpreterBase.FALSE_DEF
        # the value could refer to a field or parameter or local var
        elif self.in_local_vars(value_to_set):
            #print("in here 3")
            value_to_set = self.get_top_match_local_var(value_to_set)[2] # of format [TYPE, NAME, VALUE]
        elif value_to_set in params:
            #print("in here")
            value_to_set = params[value_to_set]
        elif value_to_set in self.fields:
            #print("in here2")
            value_to_set = self.fields[value_to_set]

        # the variable to set could be in either self.fields or a parameter or a local var
        # if a local var
        if self.in_local_vars(var_name):
            self.set_top_match_local_var(var_name ,value_to_set, interpreter)
        # if a parameter
        elif var_name in params:
            required_type = params_to_type[var_name]
            if basic_type_check(value_to_set, required_type):
                params[var_name] = value_to_set
            else:
                print("ERROR: Incompatible type when setting a parameter value")
                interpreter.error(ErrorType.TYPE_ERROR)

        # if a field
        elif var_name in self.fields:
            
            #print("CURRENT STATE OF FIELDS: ",self.fields, [(name, type_.base_data_type, type_.class_name) for name, type_ in self.fields_to_type.items()])
            required_type = self.fields_to_type[var_name]
            if basic_type_check(value_to_set, required_type):
                self.fields[var_name] = value_to_set #ValueDef(type(value_to_set), value_to_set)
            else:
                print("ERROR: Incompatible type when setting a field value")
                interpreter.error(ErrorType.TYPE_ERROR)
        else:
            print("Setting an unknown variable")
            interpreter.error(ErrorType.NAME_ERROR)
    
    def __execute_if(self, statement, params, params_to_type, interpreter):
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
        expression_val = self.__execute_expession(expression, params, params_to_type, interpreter)
        #print("Expression val:",expression_val)
        # return the statement specified by the result of the expression
        if expression_val == True and isinstance(expression_val, bool): 
            if_clause = StatementDef(if_clause)
            return self.__run_statement(if_clause, params, params_to_type, interpreter) # execute if_clause
        elif expression_val == False and isinstance(expression_val, bool):
            if else_clause != None:
                else_clause = StatementDef(else_clause)
                return self.__run_statement(else_clause, params, params_to_type, interpreter) # execute else_clause
        else:
            interpreter.error(ErrorType.TYPE_ERROR)
            print("ERROR: If Expression did not result in a Boolean")
    
    def __execute_while(self, statement, params, params_to_type, interpreter):
        # Syntax
        # (while expression statement_to_run_while_expression_is_true)
        # ['while', [expression], [statement_to_run_while_expression_is_true]]
        
        condition = statement.args[0]
        statement_to_run = StatementDef(statement.args[1])

        while True: # NEED TO DEAL WITH RETURNS IN THE WHILE STATEMENT
            res = self.__execute_expession(condition, params, params_to_type, interpreter) #execute the condition
            #print("Cond res: ", res)
            #print("Fields: ", [(key,val) for key,val in self.fields.items()])
            if res == True and isinstance(res, bool):
                # run the statement
                return_res = self.__run_statement(statement_to_run, params, params_to_type, interpreter) # execute if_clause
                #print("Return res: ", return_res)
                if return_res != None:
                    return return_res
            elif res == False and isinstance(res, bool):
                break # exit the while loop
            else:
                interpreter.error(ErrorType.TYPE_ERROR)
                print("ERROR: Expression in while loop did not result in a Boolean")
    
    def __execute_expession(self, expression, params, params_to_type, interpreter):
        expression_val = expression
        # if the expression is a local var (the name of a)
        if not isinstance(expression, list) and self.in_local_vars(expression):
            return self.get_top_match_local_var(expression)[2] # of format [TYPE, NAME, VALUE]
        # if the expression is a param
        if not isinstance(expression, list) and expression in params:
            return params[expression]
        # if the expression is a field
        if not isinstance(expression, list) and expression in self.fields:
            #print("REturning: ", self.fields[expression])
            return self.fields[expression]
        # if the expression is not a constant and needs to be further evaluated
        if self.is_expression(expression):
            expression_val = self.__handle_expression(expression, params, params_to_type, interpreter)
        
        # if the expression is a bool convert to python bool
        if expression_val == InterpreterBase.TRUE_DEF:
            expression_val = True
        elif expression_val == InterpreterBase.FALSE_DEF:
            expression_val = False
        elif expression_val == InterpreterBase.NULL_DEF:
            expression_val = NullType(True)
        elif isinstance(expression_val, NullType):
            return expression_val
        elif isinstance(expression_val, str) and is_number(expression_val):
            expression_val = int(expression_val)
        elif isinstance(expression_val, int) \
                or isinstance(expression_val, bool) \
                or is_string(expression_val) \
                or isinstance(expression_val, ObjectDef):
            #print("Alt:", expression_val)
            return expression_val
        else:
            print("Expression: ", expression)
            print("Params:", params)
            print("error with expression value: ", expression_val)  
            interpreter.error(ErrorType.NAME_ERROR)
        return expression_val
    
    def __execute_call(self, statement, old_params, old_params_to_type, interpreter):
        #print("Parsing a call statement")
        # Syntax
        # (call target_object method_name param1 ... paramn)
        # Ex: (call me bar 5)
        obj_to_call_name = statement.args[0]
        
        params = []
        if len(statement.args) > 2:
            params = statement.args[2:]
        params_types = [0 for x in params] # filled with 0s for default
        #print("Printing from __execute_call", params, params_types, old_params, old_params_to_type)
        
        # params could be from a local var or field or the old parameters or could be an expression
        for i in range(len(params)):
            if self.is_expression(params[i]):
                params[i] = self.__execute_expession(params[i], old_params, old_params_to_type, interpreter) 
            elif self.in_local_vars(params[i]):
                params[i] = self.get_top_match_local_var(params[i])[2] # of form [TYPE, NAME, VALUE]
            elif params[i] in old_params: # handle param
                params[i] = old_params[params[i]]
            elif params[i] in self.fields: # handle field
                params[i] = self.fields[params[i]]
                #params_types[i] = self.fields_to_type[params[i]]
            
                #params_types[i] = old_params_to_type[params[i]]
        #print("Params before running the method to call: ", params, params_types, old_params, old_params_to_type)

        # call me
        if obj_to_call_name == InterpreterBase.ME_DEF:
            func_to_call = statement.args[1]
            res = self.run_method(func_to_call, params, interpreter)
            #print("From exec call: ", res)
            return res
        elif obj_to_call_name == InterpreterBase.SUPER_DEF:
            func_to_call = statement.args[1]
            res = self.inherits_from.run_method(func_to_call, params, interpreter)
            return res
        # obj_to_call_name could be an expression. Handle that
        elif self.is_expression(obj_to_call_name):
            expression = obj_to_call_name
            obj_to_call = self.__handle_expression(expression, params, params_types, interpreter)
            if obj_to_call == None or not isinstance(obj_to_call, ObjectDef):
                print("Cannot call function on null object!")
                interpreter.error(ErrorType.FAULT_ERROR)
            func_to_call = statement.args[1]
            return obj_to_call.run_method(func_to_call, params, interpreter)
        
        # otherwise look in the local variables
        if self.in_local_vars(obj_to_call_name):
            obj_to_call = self.get_top_match_local_var(obj_to_call_name)[2] # of form [TYPE, NAME, VALUE]
            if obj_to_call == None or isinstance(obj_to_call, NullType):
                print("Cannot call function on null object!")
                interpreter.error(ErrorType.FAULT_ERROR) 
            func_to_call = statement.args[1]
            return obj_to_call.run_method(func_to_call, params, interpreter)
        
        # otherwise look in the parameters (the old ones not the new ones provided to this call!)
        #print("old_params: ", old_params)
        for name, obj in old_params.items():
            if name == obj_to_call_name:
                obj_to_call = obj
                if obj_to_call == None or isinstance(obj_to_call, NullType):
                    print("Cannot call function on null object!")
                    interpreter.error(ErrorType.FAULT_ERROR) 
                func_to_call = statement.args[1]
                return obj_to_call.run_method(func_to_call, params, interpreter)
        
        # otherwise look in the fields (where the value of the field is set to the class)
        for name, obj in self.fields.items():
            #print(name, obj_to_call_name)
            if name == obj_to_call_name:
                obj_to_call = obj 
                if obj_to_call == None or isinstance(obj_to_call, NullType):
                    print("Cannot call function on null object!")
                    interpreter.error(ErrorType.FAULT_ERROR) 
                func_to_call = statement.args[1]
                return obj_to_call.run_method(func_to_call, params, interpreter)
            
        # if the object is not found in a field or is itself
        print("Object to call function on not found or the object is null!")
        interpreter.error(ErrorType.FAULT_ERROR) 
    
    def __execute_return(self, statement, params, params_to_type, interpreter):
        #print("args: ", statement.args)
        if len(statement.args) == 0: # for the (return) statement
            #print("NullType false")
            return NullType(False) # False to indicate that the is_null field is false
        expression_to_return = statement.args[0]
        #print("expression_to_return", expression_to_return, params)
        res = self.__execute_expession(expression_to_return, params, params_to_type, interpreter) #execute the condition
        print("From __execute_return returning: ", res)
        return res
    
    def in_local_vars(self, cur):
        # go through the local var stack and return true if there is a match
        # cur is the name that we are searching for
        # has format [[[TYPE, 'x', 'true'], [TYPE, 'y', '5']], [[TYPE, 'z', 6]]]
        #print(self.local_var_stack)
        for stack_frame in self.local_var_stack: # each let statement pushes one stack_frame containing local vars
            for local_var in stack_frame:
                name = local_var[1] # local_var is of format [TYPE, NAME, VALUE]
                if name == cur:
                    return True
        return False
    
    def get_top_match_local_var(self, cur): # returns the variable searched for in format [TYPE, NAME, VALUE]
                                            # searches the stack backwards from the latest pushed stack frame to the first pushed
        #print(f"Attempting to match local var {cur}") 
        for i in range(len(self.local_var_stack) - 1, -1, -1): # search backwards through stack frames
            stack_frame = self.local_var_stack[i] # each let statement pushes one stack_frame containing local vars
            for local_var in stack_frame:
                name = local_var[1] # local_var is of format [TYPE, NAME, VALUE]
                if name == cur:
                    #print(f"Var matched with {cur}. Returning {local_var}")
                    return local_var
        print("ERROR: No matching local_var found. get_top_match_local_var should be called when the input is known to be in the local_var stack")
        return None
    
    def set_top_match_local_var(self, cur, value_to_set, interpreter):
        for i in range(len(self.local_var_stack) - 1, -1, -1): # search backwards through stack frames
            stack_frame = self.local_var_stack[i] # each let statement pushes one stack_frame containing local vars
            for local_var in stack_frame:
                required_type, name, old_value = local_var # local_var is of format [TYPE, NAME, VALUE]
    
                if name == cur: # a match is found (cur is the variable to set's name)
                    #print(value_to_set, required_type.base_data_type, required_type.class_name)
                    if basic_type_check(value_to_set, required_type):
                        local_var[2] = value_to_set # set the local variable
                        return
                    else:
                        print("ERROR: Incompatible type when setting a local variable value")
                        interpreter.error(ErrorType.TYPE_ERROR)
        print("ERROR: No matching local_var found. set_top_match_local_var should be called when the input is known to be in the local_var stack")
        
    def __execute_let(self, statement, params, params_to_type, interpreter):
        #print("executing a let statement")
        # Example syntax:
        # (let ((bool x true) (int y 5))
        #       (print x) # Line #2: prints true
        #        (print y) # Line #3: prints 5
        #    )
        #  [
        # 'let', # the let 
        # [['bool', 'x', 'true'], ['int', 'y', '5']], # the local var defs
        # ['print', 'x'], # and each statement
        # ['print', 'y']
        # ]
        local_var_defs = statement.args[0] # NEED TO GO THROUGH AND DEFINE THESE
        cur_local_vars = []
        already_used_names = set()
        for var_def in local_var_defs:
            type_name, name, value = var_def[0:3]
            if name in already_used_names:
                print(f"Duplicate local variable added! Of name {name}")
                interpreter.error(ErrorType.NAME_ERROR)
            else:
                already_used_names.add(name)
            base_data_type = BaseDataType.str_to_data_type(type_name)
            data_type = DataType(base_data_type, type_name)
            cur_local_vars.append([data_type, name, value]) # formating is TYPE, NAME, VALUE
        
        # add cur_local_vars to the top of the local var stack
        self.local_var_stack.append(cur_local_vars)
        #print(self.local_var_stack)
        sub_statements = statement.args[1:]
        #print(sub_statements)
        if len(sub_statements) == 0:
            print("ERROR: Cannot have an empty let statement.")
        res = None
        for statement in sub_statements:
            statement = StatementDef(statement) # turn into an actual statement
            res = self.__run_statement(statement, params, params_to_type, interpreter)
            #print("res1: ", res, statement.type, statement.args)
            if res != None and statement.type != StatementType.CALL: # if in a call statement do not return the value unless in a return statement itself
                self.local_var_stack.pop() # POP THE STACK so local vars go out of scope
                return res
        self.local_var_stack.pop() # POP THE STACK so local vars go out of scope
        

    # runs/interprets the passed-in statement until completion and gets the result, if any
    def __run_statement(self, statement, params, params_to_type, interpreter):
        if statement.type == StatementType.PRINT:
            #print("exec print")
            return self.__execute_print(statement, params, params_to_type, interpreter)
        elif statement.type == StatementType.BEGIN:
            res =  self.__execute_begin(statement, params, params_to_type, interpreter)
            #print("res from __run_statement: ", res)
            return res
        elif statement.type == StatementType.CALL:
            return self.__execute_call(statement, params, params_to_type,interpreter)
        elif statement.type == StatementType.WHILE:
            return self.__execute_while(statement, params, params_to_type, interpreter)
        elif statement.type == StatementType.RETURN:
            res = self.__execute_return(statement, params, params_to_type,interpreter)
            #print("q: ", res)
            return res
        elif statement.type == StatementType.INPUTI:
            return self.__execute_inputi(statement, params, params_to_type,interpreter)
        elif statement.type == StatementType.INPUTS:
            return self.__execute_inputs(statement, params, params_to_type,interpreter)
        elif statement.type == StatementType.IF:
            return self.__execute_if(statement, params, params_to_type, interpreter)
        elif statement.type == StatementType.SET:
            return self.__execute_set(statement, params, params_to_type, interpreter)
        elif statement.type == StatementType.LET:
            return self.__execute_let(statement, params, params_to_type, interpreter)
        print("Statement type error!")
        return None