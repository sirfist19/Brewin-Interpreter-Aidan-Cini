# this is the main interpreter file!
# TURNING IT IN: Turn in this file and others used to support it that you create
#                Do not turn in bparser.py or intbase.py
from bparser import *
from intbase import *
from fundamental_defs import *
from class_ import ClassDef

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
        #self.__discover_all_classes_and_track_them(parsed_program)
        self.define_fundamentals(parsed_program)
            #print(self.classes)
        main_class = self.__find_definition_for_class("main")

        obj = main_class.instantiate_object()
            #print("=========== OUTPUT! =========")
        interpreter = self
        obj.run_method("main", interpreter)

    def define_fundamentals(self, parsed_program):
        for class_def in parsed_program:
            # class_def should have format ['class', 'main', [method ...]]
            if class_def[0] != InterpreterBase.CLASS_DEF:
                print("Error! Not in a class: ", class_def[0])
                #exit(1)

            class_name = class_def[1]
            cur_class = ClassDef(class_name)
            for i in range(2,len(class_def)):
                if type(class_def[i]) == list:
                    # it is a field (the first element is field)
                    if class_def[i][0] == InterpreterBase.FIELD_DEF:
                        # handle a field
                        name, value_no_type = class_def[i][1], class_def[i][2]
                        if value_no_type == "null":
                            value_no_type = None
                        value = ValueDef(type(value_no_type), value_no_type)
                        cur_field = VariableDef(name, value)
                        #print("Adding a field")
                        #print(f"Field name: {name}, Value: {value.type, value.value}\n")
                        cur_class.add_field(cur_field)

                    # if it is a method (first element is method)
                    elif class_def[i][0] == InterpreterBase.METHOD_DEF:
                        # handle a method
                        cur_method = class_def[i]
                        name, params, statement_data = cur_method[1], cur_method[2], cur_method[3]
                        statement = StatementDef(statement_data) # statement data holds the type of statement and the args
                        cur_method = MethodDef(name, params, statement)
                        
                        #print("Adding a method")
                        #print(f'Name: {name}, Params: {params}, Statement: {statement.statement_type, statement.args}')
                        cur_class.add_method(cur_method)
                    else:
                        print("Error: Unknown list start within class")
                        print(class_def[i][0])
                        #exit(1)
            
            # add the current class to the list
                #print("Adding a class")
            self.classes[cur_class.name] = cur_class

    # print all of the line numbers for all tokens in parsed program
    def print_line_nums(self, parsed_program):
        for item in parsed_program:
            if type(item) is not list:
                print(f'{item} was found on line {item.line_num}')
            else:
                self.print_line_nums(item)

    def __find_definition_for_class(self, name):
        found_class = self.classes[name]
        if not found_class:
            print("Class could not be found!")
            return None
        else:
            #print(f"Class found of name {name}")
            return self.classes[name]