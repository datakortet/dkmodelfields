class Creator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        print("OBJECT", obj)
        print("VALUE", value)
        print("TYPEOFSELFFIELD", type(self.field))
        print("TYPEOBJDICT", obj.__dict__[self.field.name])
        temp = self.field.to_python(value)
        print("TEMP", temp, type(temp))
        obj.__dict__[self.field.name] = self.field.to_python(value)
