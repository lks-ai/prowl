class ValidationError(ValueError):
    def __init__(self, code, message, data=None):
        super().__init__(f"Error ({code}): {message}\n\t{data}")
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self):
        return {'code': self.code, 'message': self.message, 'data': self.data}