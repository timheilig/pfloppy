OPERAND_SID = 'SID'
OPERAND_BOOLEAN = 'boolean'
OPERAND_NUMBER = 'number'
OPERAND_ARRAY = 'array'
OPERAND_DELTA = 'delta'
OPERAND_OPERATION = 'operation'


class Operation(object):
    def __init__(self, key, types, default_value=None):
        self.key = key
        self.types = types
        self.default_value = default_value


class Command(Operation):
    def __init__(self, key):
        super(Command, self).__init__(key, ())
