import sys

class Wrapper():
    def __init__(self, surround, type_of_uploaded_object):
        self.surround = surround
        self.type_of_uploaded_object = type_of_uploaded_object
        self.surround.init_stages()

    def run(self, uploaded_data):
        if self.validate() is False:
            sys.exit()

    def validate(self):
        return self.validate_type_of_uploaded_object()

    def validate_type_of_uploaded_object(self):
        allowed_types = ['JSON', 'image']
        for type_ in allowed_types:
            if self.type_of_uploaded_object == type_:
                return True
        print("error: selected upload type not allowed")
        print("Choose from: ")
        for type_ in allowed_types:
            print(type_)
        return False

    def process(self, uploaded_data):
        Wrapper.run(self, uploaded_data)
        self.run(uploaded_data)
