class Wrapper():
    def __init__(self, surround, type_of_uploaded_object):
        self.surround = surround
        self.type_of_uploaded_object = type_of_uploaded_object
        self.surround.init_stages()

    def run(self, uploaded_data):
        return self.validate

    def validate(self):
        return self.validate_type_of_uploaded_object()

    def validate_type_of_uploaded_object(self):
        allowed_types = ['JSON', 'image']
        for type_ in allowed_types:
            if self.type_of_uploaded_object == type_:
                return True
        print("Selected type not allowed")
        return False
