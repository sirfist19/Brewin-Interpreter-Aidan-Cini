from interpreterv1 import *

def to_src(file_path):
    """
    This function reads the file specified by the file_path parameter and returns a list of each line in the file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]  # remove newline characters from each line
    return lines

# Example usage

# the temporary start to running the interpreter
if __name__ == "__main__":

    test_paths = ["helloworld", 
                  "field_num",
                  "begin_test",
                  "input_num",
                  "input_str",
                  "set_test",
                  "expression_test1",
                  "expression_test2_var",
                  "if_test_spec",
                  "null_test",
                  "while_test",
                  "two_method_test",
                  "input_param_test", 
                  "null_test2",
                  "param_test", 
                  "two_class_test",
                  "return_test",
                  "return_test2",
                  "factorial_simple",
                  "factorial",
                  "call_complex_test",
                  "pg14_test",
                  "count_recursion",
                  "recursion1_test",
                       "null_test3",
                       
                       "while_return_test",
                       "inst_return_test1",
                       "str_op_test",
                       "nested_calls_test",
                       "while_return_test2",
                       "str_op_test2",
                       "testing",
                       "jake_test2",
                       "tree_test",
                       "linked_list_test",
                       "nested_if_return_test"
                  ]
    test_less_paths = ["two_method_test",
                       "input_param_test", 
                       "null_test2", 
                       "param_test", 
                       "two_class_test",
                       "return_test",
                       "return_test2",
                       "factorial_simple",
                       "factorial",
                       "call_complex_test",
                       "pg14_test",
                       "count_recursion",
                       "recursion1_test",
                       "null_test3",
                       "inst_return_test1",
                       "str_op_test",
                       "nested_calls_test",
                       "str_op_test2",
                       "while_return_test2",
                       "rpg_test",
                       "even_odd_rec_test",
                       "testing",
                       "jake_test2"
                       ]
    test_while = ["while_test", "while_return_test", "factorial_simple", "factorial"]
    test_str = ["str_op_test"]
    test_incorrect = ["testing"]

    # run the interpreter
    file_path_base = '../Test_Brewin_Programs/'  # Replace with your file path
    #print("Type in the file you want to run")
    print("==================")
    for path in test_paths:
        file_path = file_path_base + path
        src = to_src(file_path)
        #print("\n\n==================")
        
        print(f"Running {path}")
        # create an interpreter object
        interpreter = Interpreter()
        interpreter.run(src)
        print("==================")

    #file_name = input()
    #file_path = file_path_base + file_name
    #src = to_src(file_path)
    #src_to_run = src # SET THIS TO WHATEVER PROGRAM YOU WANT TO RUN
    #interpreter.run(src_to_run)