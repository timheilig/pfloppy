import cff.builders
import ttf.builders


def parse_font(encoded_data):
    if encoded_data[0:3] == "\x01\x00\x04":
        font = cff.builders.CffFont()
    elif encoded_data[0:4] in set(["\x00\x01\x00\x00", "OTTO", "true"]):
        font = ttf.builders.TtfFont()
    else:
        raise NotImplementedError
    font.read_from_content(encoded_data)

def parse_file(file_name):
    font_file = open(file_name, 'rb')
    content = font_file.read()
    return parse_font(content)