OPERAND_SID = 'SID'
OPERAND_BOOLEAN = 'boolean'
OPERAND_NUMBER = 'number'
OPERAND_ARRAY = 'array'
OPERAND_DELTA = 'delta'
OPERAND_OPERATION = 'operation'


def read_unknown_thing(data, is_charstring=False):
    b0 = data.read_integer(1)
    if b0 == 12:
        # this is a two byte operator code
        return OPERAND_OPERATION, (b0, data.read_integer(1))
    elif b0 < 28 or (b0 < 32 and is_charstring):  # dict entries have operands in the 29-31 range, but charstring
                                                  # has operators in that range
        # this is a one byte operator code
        return OPERAND_OPERATION, (b0,)
    elif b0 == 28:
        # this is a 2 byte integer (-32768 -> +32767) in b1 and b2
        return OPERAND_NUMBER, data.read_integer(2)
    elif b0 == 29:
        # this is a 4 bit integer (-2^31 -> 2^31 - 1) in b1 -> b4
        return OPERAND_NUMBER, data.read_integer(4)
    elif b0 == 30:
        # real number (sort of a bcd encoding with extra values for '.', '-' and 'e')
        return OPERAND_NUMBER, get_real_number(data)
    elif b0 < 32 or b0 > 254:
        raise ValueError("Invalid CFF operand {0}".format(b0))
    elif b0 <= 246:
        # value between -107 and 107
        return OPERAND_NUMBER, b0 - 139
    elif b0 <= 250:
        # mid-size positive value (108 -> 1131)
        return OPERAND_NUMBER, (b0 - 247) * 256 + data.read_integer(1) + 108
    else:
        # mid-size negative value (-1131 -> -108)
        return OPERAND_NUMBER, (251 - b0) * 256 - data.read_integer(1) - 108


def get_real_number(data):
    # first decode nibbles into a string based on the character mapping
    nibble_to_char = {
        0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',
        10: '.', 11: 'e+', 12: 'e-', 14: '-'
    }
    number_as_string = ''
    done = False
    while not done:
        next_byte = data.read_integer(1)
        first_nibble = (next_byte & 0xF0) >> 4
        second_nibble = next_byte & 0xF
        for nibble in (first_nibble, second_nibble):
            if nibble < 15:
                number_as_string += nibble_to_char[nibble]
            else:
                done = True
    return float(number_as_string)
