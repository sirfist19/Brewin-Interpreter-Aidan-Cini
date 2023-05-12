from object_ import ObjectDef

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