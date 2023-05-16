from object_ import ObjectDef

class ClassDef:
    # constructor for a ClassDefinition
    def __init__(self, name):
        self.name = name
        self.methods = {} # a dict of MethodDefs of name to the method
        self.fields = {} # a dictionary of variables of names to values
        self.fields_to_type = {} # dict of variable names to their required types
        self.to_base = None # either None or ClassDef of the inherited class
    
    def add_method(self, method): # method should be of type MethodDef
        self.methods[method.name] = method

    def add_field(self, field): # field should be of type VariableDef 
        self.fields[field.name] = field.value
        self.fields_to_type[field.name] = field.type

    # uses the definition of a class to create and return an instance of it
    def instantiate_object(self):
        obj = ObjectDef(self.name)
        for method in self.methods.values():
            obj.add_method(method)
        for field_name, field_value in self.fields.items():
            obj.add_field(field_name, field_value)
        for field_name, field_type in self.fields_to_type.items():
            obj.add_field_type(field_name, field_type)
        if self.to_base is not None:
            base_obj = self.to_base.instantiate_object()
            base_obj.to_derived = obj
            obj.to_base = base_obj
            #base_obj.display()
        #obj.display()
        return obj