# this is the main interpreter file!
# TURNING IT IN: Turn in this file and others used to support it that you create
#                Do not turn in bparser.py or intbase.py
from bparser import *
from intbase import *
from fundamental_defs import *
from class_ import ClassDef
from object_ import *

# This is the needed Interpreter class that is derived from InterpreterBase
class Interpreter(InterpreterBase):
    def __init__(self, console_output = True, inp=None, trace_output=False):
        #define stuff here!
        super().__init__(console_output,inp)
        self.classes = {} # name to classes
    
    def run(self, program):
        # parse the program into a more easily processed form
        #print(program_source)
        result, parsed_program = BParser.parse(program)

        if result == False:
            print("Parsing error. Most likely mismatched parenthesis.")
            return # error
        
        # now that the program is correctly parsed
        # INTERPRET THE PROGRAM 
        print(f'HERE IS THE PARSED PROGRAM: \n{parsed_program}')
        self.define_fundamentals(parsed_program)
            #print(self.classes)
        main_class = self.find_definition_for_class("main")

        obj = main_class.instantiate_object()

        #for method in obj.methods:
        #    print(method)

        interpreter = self
        obj.run_method("main", [], interpreter) # run main with no args

    def define_fundamentals(self, parsed_program):
        # for each class in the program ... parse the class and add it to the interpreter classes
        
        for class_def in parsed_program:
            # class_def should have format ['class', 'main', [method ...]]
            if class_def[0] != InterpreterBase.CLASS_DEF:
                print("Error! Not in a class: ", class_def[0])

            class_name = class_def[1]

            # handle duplicate classes when the name is already set
            if class_name in self.classes: 
                print("duplicate class: ", class_name, self.classes)
                self.error(ErrorType.TYPE_ERROR)

            cur_class = ClassDef(class_name)
            for i in range(2,len(class_def)):
                if type(class_def[i]) == list:
                    # it is a field (the first element is field)
                    if class_def[i][0] == InterpreterBase.FIELD_DEF:
                        # handle a field
                        # Ex: ['field', 'int', 'q', '5']
                        type_, name, value = class_def[i][1:4]
                        type_ = DataType(BaseDataType.str_to_data_type(type_), type_) # makes type_ an object of DataType with a base_type and class_name

                        # handle a duplicate field
                        if name in cur_class.fields:
                            print("duplicate field: ", name)
                            self.error(ErrorType.NAME_ERROR)

                        if value == InterpreterBase.NULL_DEF:
                            value = NullType() #None
                        
                        if basic_type_check(value, type_):
                            cur_field = VariableDef(name, value, type_)
                            cur_class.add_field(cur_field)
                        else:
                            print("Field input value does not match the type.")
                            self.error(ErrorType.TYPE_ERROR)

                    # if it is a method (first element is method)
                    elif class_def[i][0] == InterpreterBase.METHOD_DEF:
                        # handle a method
                        cur_method = class_def[i]
                        return_type_str, name, params, statement_data = cur_method[1:5]
                        return_type = DataType(BaseDataType.str_to_data_type(return_type_str), return_type_str)

                        # handle a duplicate method
                        if name in cur_class.methods:
                            print("duplicate method: ", name)
                            self.error(ErrorType.NAME_ERROR)

                        param_map_name_to_value = dict()
                        param_map_name_to_type = dict()
                        for type_, param_name in params:
                            type_ = DataType(BaseDataType.str_to_data_type(type_), type_)
                            default_value = BaseDataType.get_default_value(type_.base_data_type)
                            param_map_name_to_type[param_name] = type_
                            param_map_name_to_value[param_name] = default_value

                        # params: [['int', 'a'], ['int', 'b']]
                        #['method', 'int', 'add', [['int', 'a'], ['int', 'b']], ['return', ['+', 'a', 'b']]]
                        
                        statement = StatementDef(statement_data) # statement data holds the type of statement and the args
                        cur_method = MethodDef(name, 
                                               param_map_name_to_value, 
                                               param_map_name_to_type,
                                               statement, 
                                               return_type)
                        
                        #print("Adding a method")
                        print(f'Name: {name}, Params: {param_map_name_to_type, param_map_name_to_value}, Statement: {statement.type, statement.args}')
                        cur_class.add_method(cur_method)
                    else:
                        print("Error: Unknown list start within class")
                        print(class_def[i][0])
                        #exit(1)
            
            # add the current class to the list
                #print("Adding a class")
            self.classes[cur_class.name] = cur_class
        #for class_name, class_ in self.classes.items():
        #    print(class_name, class_)
    # print all of the line numbers for all tokens in parsed program
    def print_line_nums(self, parsed_program):
        for item in parsed_program:
            if type(item) is not list:
                print(f'{item} was found on line {item.line_num}')
            else:
                self.print_line_nums(item)

    def find_definition_for_class(self, name):
        if name not in self.classes:
            print(f"The class {name} could not be found in interpreter!")
            self.error(ErrorType.TYPE_ERROR)
        return self.classes[name]
        