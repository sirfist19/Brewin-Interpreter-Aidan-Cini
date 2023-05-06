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
    # create an interpreter object
    interpreter = Interpreter()

    test_paths = ["helloworld", 
                  "field_num",
                  "begin_test",
                  "input_num",
                  "input_str",
                  "set_test",
                  "expression_test1",
                  "expression_test2_var",
                  "if_test_spec",
                  "null_test"
                  ]
    
    # run the interpreter
    file_path_base = '../Test_Brewin_Programs/'  # Replace with your file path
    #print("Type in the file you want to run")
    print("==================")
    for path in test_paths:
        file_path = file_path_base + path
        src = to_src(file_path)
        #print("\n\n==================")
        
        print(f"Running {path}")
        interpreter.run(src)
        print("==================")

    #file_name = input()
    #file_path = file_path_base + file_name
    #src = to_src(file_path)
    #src_to_run = src # SET THIS TO WHATEVER PROGRAM YOU WANT TO RUN
    #interpreter.run(src_to_run)