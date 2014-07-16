from encodings import Encoding
from charstrings import Type2CharString, Type2CharStringParser
from pdfbox.fonts.walkable import WalkableString as WalkableString
import pdfbox.fonts.cff.rawdata
import pdfbox.fonts.cff.encodings


OPERAND_SID = 'SID'
OPERAND_BOOLEAN = 'boolean'
OPERAND_NUMBER = 'number'
OPERAND_ARRAY = 'array'
OPERAND_DELTA = 'delta'
OPERAND_OPERATION = 'operation'

class CffFont(object):
    built_in_string_table = [
        '.notdef', 'space', 'exclam', 'quotedbl', 'numbersign', 'dollar', 'percent', 'ampersand', 'quoteright',  # 0-8
        'parenleft', 'parenright', 'asterisk', 'plus', 'comma', 'hyphen', 'period', 'slash', 'zero', 'one',    # 9-18
        'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'colon', 'semicolon', 'less',         # 19-29
        'equal', 'greater', 'question', 'at', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',      # 30-45
        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'bracketleft', 'backslash',      # 46-61
        'bracketright', 'asciicircum', 'underscore', 'quoteleft', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', # 62-74
        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'braceleft',      # 75-92
        'bar', 'braceright', 'asciitilde', 'exclamdown', 'cent', 'sterling', 'fraction', 'yen', 'florin',      # 93-101
        'section', 'currency', 'quotesingle', 'quotedblleft', 'guillemotleft', 'guilsinglleft',                # 102-107
        'guilsinglright', 'fi', 'fl', 'endash', 'dagger', 'daggerdbl', 'periodcentered', 'paragraph',          # 108-115
        'bullet', 'quotesinglbase', 'quotedblbase', 'quotedblright', 'guillemotright', 'ellipsis',             # 116-121
        'perthousand', 'questiondown', 'grave', 'acute', 'circumflex', 'tilde', 'macron', 'breve',             # 122-129
        'dotaccent', 'dieresis', 'ring', 'cedilla', 'hungarumlaut', 'ogonek', 'caron', 'emdash', 'AE',         # 130-138
        'ordfeminine', 'Lslash', 'Oslash', 'OE', 'ordmasculine', 'ae', 'dotlessi', 'lslash', 'oslash',         # 139-147
        'oe','germandbls','onesuperior','logicalnot', 'mu', 'trademark', 'Eth', 'onehalf', 'plusminus',        # 148-156
        'Thorn', 'onequarter', 'divide', 'brokenbar', 'degree', 'thorn', 'threequarters', 'twosuperior',       # 157-164
        'registered', 'minus', 'eth', 'multiply', 'threesuperior', 'copyright', 'Aacute', 'Acircumflex',       # 165-172
        'Adieresis', 'Agrave', 'Aring', 'Atilde', 'Ccedilla', 'Eacute', 'Ecircumflex', 'Edieresis', 'Egrave',  # 173-181
        'Iacute', 'Icircumflex', 'Idieresis', 'Igrave', 'Ntilde', 'Oacute', 'Ocircumflex', 'Odieresis',        # 182-189
        'Ograve', 'Otilde', 'Scaron', 'Uacute', 'Ucircumflex', 'Udieresis', 'Ugrave', 'Yacute', 'Ydieresis',   # 190-198
        'Zcaron', 'aacute', 'acircumflex', 'adieresis', 'agrave', 'aring', 'atilde', 'ccedilla', 'eacute',     # 199-207
        'ecircumflex', 'edieresis', 'egrave', 'iacute','icircumflex', 'idieresis', 'igrave', 'ntilde',         # 208-215
        'oacute', 'ocircumflex', 'odieresis', 'ograve', 'otilde', 'scaron', 'uacute', 'ucircumflex',           # 216-223
        'udieresis', 'ugrave', 'yacute', 'ydieresis', 'zcaron', 'exclamsmall', 'Hungarumlautsmall',            # 224-230
        'dollaroldstyle', 'dollarsuperior', 'ampersandsmall', 'Acutesmall', 'parenleftsuperior',               # 231-235
        'parenrightsuperior4', 'twodotenleader', 'onedotenleader', 'zerooldstyle', 'oneoldstyle',              # 236-240
        'twooldstyle', 'threeoldstyle', 'fouroldstyle', 'fiveoldstyle', 'sixoldstyle', 'sevenoldstyle',        # 241-246
        'eightoldstyle', 'nineoldstyle', 'commasuperior', 'threequartersemdash', 'periodsuperior',             # 247-251
        'questionsmall', 'asuperior', 'bsuperior', 'centsuperior', 'dsuperior', 'esuperior', 'isuperior',      # 252-258
        'lsuperior', 'msuperior', 'nsuperior', 'osuperior', 'rsuperior', 'ssuperior', 'tsuperior', 'ff',       # 259-266
        'ffi', 'ffl', 'parenleftinferior', 'parenrightinferior', 'Circumflexsmall', 'hyphensuperior',          # 267-272
        'Gravesmall', 'Asmall', 'Bsmall', 'Csmall', 'Dsmall', 'Esmall', 'Fsmall', 'Gsmall', 'Hsmall',          # 273-281
        'Ismall', 'Jsmall', 'Ksmall', 'Lsmall', 'Msmall', 'Nsmall', 'Osmall', 'Psmall', 'Qsmall', 'Rsmall',    # 282-291
        'Ssmall', 'Tsmall', 'Usmall', 'Vsmall', 'Wsmall', 'Xsmall', 'Ysmall', 'Zsmall', 'colonmonetary',       # 292-300
        'onefitted', 'rupiah', 'Tildesmall', 'exclamdownsmall', 'centoldstyle', 'Lslashsmall',                 # 301-306
        'Scaronsmall', 'Zcaronsmall', 'Dieresissmall', 'Brevesmall', 'Caronsmall', 'Dotaccentsmall',           # 307-312
        'Macronsmall', 'figuredash', 'hypheninferior', 'Ogoneksmall', 'Ringsmall', 'Cedillasmall',             # 313-318
        'questiondownsmall', 'oneeighth', 'threeeighths', 'fiveeighths', 'seveneigths', 'onethird',            # 319-324
        'twothirds', 'zerosuperior', 'foursuperior', 'fivesuperior', 'sixsuperior', 'sevensuperior',           # 325-330
        'eightsuperior', 'ninesuperior', 'zeroinferior', 'oneinferior', 'twoinferior', 'threeinferior',        # 331-336
        'fourinferior', 'fiveinferior', 'sixinferior', 'seveninferior', 'eightinferior', 'nineinferior',       # 337-342
        'centinferior', 'dollarinferior', 'periodinferior', 'commainferior', 'Agravesmall', 'Aacutesmall',     # 343-348
        'Acircumflexsmall', 'Atildesmall', 'Adieresissmall', 'Aringsmall', 'AEsmall', 'Ccedillasmall',         # 349-354
        'Egravesmall', 'Eacutesmall', 'Ecircumflexsmall', 'Edieresissmall', 'Igravesmall', 'Iacutesmall',      # 355-360
        'Icircumflexsmall', 'Idieresissmall', 'Ethsmall', 'Ntildesmall', 'Ogravesmall', 'Oacutesmall',         # 361-366
        'Ocircumflexsmall', 'Otildesmall', 'Odieresissmall', 'OEsmall', 'Oslashsmall', 'Ugravesmall',          # 367-372
        'Uacutesmall', 'Ucircumflexsmall', 'Udieresissmall', 'Yacutesmall', 'Thornsmall', 'Ydieresissmall',    # 373-378
        '001.000', '001.001', '001.002', '001.003', 'Black', 'Bold', 'Book', 'Light', 'Medium', 'Regular',     # 379-388
        'Roman', 'Semibold'                                                                                    # 389-390
    ]

    top_dict_operation_map = {
                (0,): ('version', (OPERAND_SID,), None),
                (1,): ('Notice', (OPERAND_SID,), None),
                (2,): ('FullName', (OPERAND_SID,), None),
                (3,): ('FamilyName', (OPERAND_SID,), None),
                (4,): ('Weight', (OPERAND_SID,), None),
                (5,): ('FontBBox', (OPERAND_ARRAY,), [0, 0, 0, 0]),
                (12, 0): ('Copyright', (OPERAND_SID,), None),
                (12, 1): ('isFixedPitch', (OPERAND_BOOLEAN,), False),
                (12, 2): ('ItalicAngle', (OPERAND_NUMBER,), 0),
                (12, 3): ('UnderlinePosition', (OPERAND_NUMBER,), -100),
                (12, 4): ('UnderlineThickness', (OPERAND_NUMBER,), 50),
                (12, 5): ('PaintType', (OPERAND_NUMBER,), 0),
                (12, 6): ('CharstringType', (OPERAND_NUMBER,), 2),
                (12, 7): ('FontMatrix', (OPERAND_ARRAY,), [.001, 0, 0, .001, 0, 0]),
                (12, 8): ('StrokeWidth', (OPERAND_NUMBER,), 0),
                (12, 20): ('SyntheticBase', (OPERAND_NUMBER,), None),
                (12, 21): ('PostScript', (OPERAND_SID,), None),
                (12, 22): ('BaseFontName', (OPERAND_SID,), None),
                (12, 23): ('BaseFontBlend', (OPERAND_DELTA,), None),
                (12, 30): ('ROS', (OPERAND_SID, OPERAND_SID, OPERAND_NUMBER), None),
                (12, 31): ('CIDFontVersion', (OPERAND_NUMBER,), 0),
                (12, 32): ('CIDFontRevision', (OPERAND_NUMBER,), 0),
                (12, 33): ('CIDFontType', (OPERAND_NUMBER,), 0),
                (12, 34): ('CIDCount', (OPERAND_NUMBER,), 8720),
                (12, 35): ('UIDBase', (OPERAND_NUMBER,), None),
                (12, 36): ('FDArray', (OPERAND_NUMBER,), None),
                (12, 37): ('FDSelect', (OPERAND_NUMBER,), None),
                (12, 38): ('FontName', (OPERAND_SID,), None),
                (13,): ('UniqueID', (OPERAND_NUMBER,), None),
                (14,): ('XUID', (OPERAND_ARRAY,), None),
                (15,): ('charset', (OPERAND_NUMBER,), 0),
                (16,): ('Encoding', (OPERAND_NUMBER,), None),
                (17,): ('CharStrings', (OPERAND_NUMBER,), None),
                (18,): ('Private', (OPERAND_NUMBER, OPERAND_NUMBER), None),
            }

    private_dict_operation_map = {
                (6,): ('BlueValues', (OPERAND_DELTA,), None),
                (7,): ('OtherBlues', (OPERAND_DELTA,), None),
                (8,): ('FamilyBlues', (OPERAND_DELTA,), None),
                (9,): ('FamilyOtherBlues', (OPERAND_DELTA,), None),
                (10,): ('StdHW', (OPERAND_NUMBER,), None),
                (11,): ('StdVW', (OPERAND_NUMBER,), None),
                (12, 9): ('BlueScale', (OPERAND_NUMBER,), .039625),
                (12, 10): ('BlueShift', (OPERAND_NUMBER,), 7),
                (12, 11): ('BlueFuzz', (OPERAND_NUMBER,), 1),
                (12, 12): ('StemSnapH', (OPERAND_DELTA,), None),
                (12, 13): ('StemSnapV', (OPERAND_DELTA,), None),
                (12, 14): ('ForceBold', (OPERAND_BOOLEAN,), False),
                (12, 17): ('LanguageGroup', (OPERAND_NUMBER,), 0),
                (12, 18): ('ExpansionFactor', (OPERAND_NUMBER,), .06),
                (12, 19): ('initialRandomSeed', (OPERAND_NUMBER,), 0),
                (19,): ('Subrs', (OPERAND_NUMBER,), None),
                (20,): ('defaultWidthX', (OPERAND_NUMBER,), 0),
                (21,): ('nominalWidthX', (OPERAND_NUMBER,), 0),
            }

    def __init__(self):
        self._glyphs = []
        self.custom_string_table = None
        self.top_dicts = None
        self.global_subroutine_table = None
        self._local_subr_table = None
        self.encodings = []
        self.char_sets = []
        self.char_strings = []
        self.name = ''
        self.private_data = None
        self.data = WalkableString('')

    def read_from_content(self, encoded_data):
        self.data = WalkableString(encoded_data)
        self.move_to_end_of_header()
        font_name_table = self.read_index_table()
        top_dict_table = self.read_index_table()
        self.custom_string_table = self.read_index_table()
        self.top_dicts = self.build_tables(top_dict_table, self.top_dict_operation_map)
        self.global_subroutine_table = self.read_index_table()
        for i in range(len(font_name_table)):
            top_dict = self.top_dicts[i]
            if 'CharStrings' in top_dict:
                self.data.set_position(top_dict['CharStrings'])
                char_string_table = self.read_index_table()
                self.char_strings.append(char_string_table)
            else:
                self.char_strings.append([])
                char_string_table = []

            if 'Encoding' in top_dict and top_dict['Encoding']:
                self.encodings.append(self.parse_encoding(self.data, top_dict['Encoding']))
            else:
                self.encodings.append([])

            if 'charset' in top_dict:
                self.char_sets.append(self.parse_char_set(self.data, top_dict['charset'], len(char_string_table)))
            else:
                self.char_sets.append([])

            if 'Private' in top_dict and top_dict['Private']:
                private_operands = top_dict['Private']
                self.private_data = self.parse_private_data(self.data, private_operands[1], private_operands[0])
                if 'Subrs' in self.private_data:
                    self.data.set_position(self.private_data['Subrs'])
                    self._local_subr_table = self.read_index_table()
            parser = Type2CharStringParser()
            for j in range(len(char_string_table)):
                if j == 0:
                    char = '.notdef'
                else:
                    char = self.char_sets[i][j - 1]

                self._glyphs.append(Type2CharString(
                    font_name_table[i].data, char,
                    parser.parse(char_string_table[j], self.global_subroutine_table, self._local_subr_table),
                    self.private_data[i]['defaultWidthX'], self.private_data[i]['nominalWidthX']))
        self.name = font_name_table[0].data

    def move_to_end_of_header(self):
        self.data.set_position(2)  # This is the location of the header size
        self.data.set_position(self.data.read_integer(1))  # reposition to the first byte after the header

    def lookup_string_by_index(self, index):
        if index < len(self.built_in_string_table):
            return self.built_in_string_table[index]
        elif index - len(self.built_in_string_table) < len(self.custom_string_table):
            return self.custom_string_table[index - len(self.built_in_string_table)].get_data()
        else:
            return None

    def get_values(self, operand_types, stack):
        values = []
        for operand_type in operand_types:
            if operand_type == OPERAND_ARRAY:
                values.append([value[1] for value in stack])
                del stack[:]
            elif operand_type == OPERAND_DELTA:
                current_value = 0
                for value in stack:
                    current_value += value[1]
                    values.append(current_value)
                del stack[:]
            else:
                (type, value) = stack.pop(0)
                if operand_type == OPERAND_SID:
                    if type != OPERAND_NUMBER:
                        raise ValueError('Type of argument does not match expected type')
                    else:
                        value = self.lookup_string_by_index(value)
                elif operand_type != operand_type:
                    raise ValueError('Type of argument does not match expected type')
                values.append(value)
        return values

    def build_tables(self, table_data_list, operation_map):
        tables = []
        stack = []

        for table_data in table_data_list:
            table = {}
            for value in operation_map.values():
                # initialize defaults
                table[value[0]] = value[2]
            while not table_data.is_exhausted():
                (type, value) = pdfbox.fonts.cff.rawdata.read_unknown_thing(table_data)
                if type == OPERAND_OPERATION:
                    operation = operation_map[value]
                    (key, operand_types, default_value) = operation
                    values = self.get_values(operand_types, stack)
                    if len(values) == 1:
                        table[key] = values[0]
                    else:
                        table[key] = values
                else:
                    stack.append((type, value))
            tables.append(table)
        return tables


    @staticmethod
    def get_header_size(bytes):
        header_size = bytes[2]
        return header_size

    def read_index_table(self):
        count = self.data.read_integer(2)
        if count == 0:
            return []
        offset_size = self.data.read_integer(1)
        offsets = []
        for i in range(count+1):
            offsets.append(self.data.read_integer(offset_size))
        byte_chunks = []
        for i in range(count):
            size = offsets[i + 1] - offsets[i]
            byte_chunks.append(self.data.read_chunk(size))
        return byte_chunks

    def parse_encoding(self, data, offset):
        data.set_position(offset)
        if offset == 0:
            return pdfbox.fonts.cff.encodings.StandardEncoding()
        elif offset == 1:
            return pdfbox.fonts.cff.encodings.ExpertEncoding()

        encoding = pdfbox.fonts.cff.encodings.Encoding()

        encoding_format = data.read_integer(1)
        if encoding_format > 127:
            supplemental_encodings = True
            encoding_format -= 128
        else:
            supplemental_encodings = False
        if encoding_format == 0:
            number_of_codes = data.read_integer(1)
            for i in range(1, number_of_codes + 1):
                code = data.read_integer(1)
                encoding.register(code, i)
        else:
            number_of_code_ranges = data.read_integer(1)
            glyph_id = 0
            for i in range(number_of_code_ranges):
                first_code = data.read_integer(1)
                subsequent_codes = data.read_integer(1)
                for j in range(subsequent_codes + 1):
                    code = first_code + j
                    encoding.register(code, glyph_id)
                    glyph_id += 1

        if supplemental_encodings:
            number_of_supplements = data.read_integer(1)
            for i in range(number_of_supplements):
                code = data.read_integer(1)
                sid = data.read_integer(2)
                encoding.register(code, sid)
        return encoding

    def parse_char_set(self, data, offset, num_glyphs):
        if offset <= 2:
            return self.stock_char_set(offset, num_glyphs)
        data.set_position(offset)
        char_set_format = data.read_integer(1)
        char_set = []
        if char_set_format == 0:
            for i in range(num_glyphs):
                sid = data.read_integer(2)
                char_set.append(self.lookup_string_by_index(sid))
        else:
            range_count_size = char_set_format  # format 1 means 1-byte count, format 2 means a 2-byte count
            glyphs_left = num_glyphs - 1   # .notdef glyph isn't assigned an encoding, even though it's counted in total
            while glyphs_left:
                first_sid = data.read_integer(2)
                char_set.append(self.lookup_string_by_index(first_sid))
                range_count = data.read_integer(range_count_size)
                offset += range_count_size
                for i in range(range_count):
                    char_set.append(self.lookup_string_by_index(first_sid + i + 1))
                glyphs_left -= range_count + 1
        return char_set


    def stock_char_set(self, offset, num_glyphs):
        expert_sids = [1, 13, 14, 15, 27, 28, 99, 109, 110, 150, 155, 158, 163, 164, 169]
        if offset == 0:
            # ISO/Adobe is just 1-228 inclusive
            sids_to_include = range(1, 229)
        else:
            sids_to_include = expert_sids
            if offset == 1:
                # Full expert add all ids from 229 to 378
                sids_to_include.extend(range(229, 379))
            else:
                # Expert subset, which has a bunch of small ranges and random SIDs
                sids_to_include.extend([231, 232, 272, 300, 301, 302, 305, 314, 315])
                sids_to_include.extend(range(235, 252))   # 252 is skipped
                sids_to_include.extend(range(253, 271))   # 271 is skipped
                sids_to_include.extend(range(320, 347))   # 271 is skipped

        char_set = []
        for sid in sids_to_include:
            if len(char_set) == num_glyphs:
                # This was a request for only the first part of the stock set
                return char_set
            char_set.append(self.lookup_string_by_index(sid))
        return char_set

    def parse_private_data(self, data, offset, length):
        data.set_position(offset)
        return self.build_tables([data.read_chunk(length)], self.private_dict_operation_map)


class Font(object):
    def __init__(self):
        self.name = None
        self.top_dict = None
        self.private_dict = None
        self.encoding = None
        self.charset = None
        self.char_strings_dict = None
        self.global_subr_index = None
        self.local_subr_index = None
        self.char_string_cache = {}
        self._mappings = self._create_mappings()

    def get_name(self):
        return self.name

    def set_name(self, name):
        """
        :param str name:
        """
        self.name = name

    def get_property(self, name):
        if self.top_dict and name in self.top_dict:
            return self.top_dict[name]

        if self.private_dict and name in self.private_dict:
            return self.private_dict[name]

        return None

    def add_to_top_dict(self, name, value):
        """
        :param str name:
        :param object value:
        """
        if value:
            self.top_dict[name] = value

    def get_top_dict(self):
        return self.top_dict

    def add_to_private_dict(self, name, value):
        """
        :param str name:
        :param object value:
        """
        if value:
            self.private_dict[name] = value

    def add_to_mappings(self, sid, code, mapped_names, mappings):
        char_name = self.charset.get_name(sid)
        if not char_name or char_name in mapped_names:
            return False
        char_string_bytes = self.char_strings_dict[char_name]
        if not char_string_bytes:
            return False

        mappings.append(Mapping(code, sid, char_name, char_string_bytes))
        mapped_names.add(char_name)
        return True

    def _create_mappings(self):
        mappings = []
        mapped_names = set()
        for encoding_entry in self.encoding:
            self.add_to_mappings(encoding_entry.sid, encoding_entry.code, mapped_names, mappings)

        if isinstance(self.encoding, Encoding):
            for supplement in self.encoding.get_supplements():
                self.add_to_mappings(supplement.get_glyph, supplement.get_code, mapped_names, mappings)

        code = 256  # create implied codes for extended characters
        for charset_entry in self.charset.get_entries():
            if self.add_to_mappings(charset_entry.get_name, code, mapped_names, mappings):
                code += 1
        return mappings

    def get_mappings(self):
        return self._mappings

    def get_width(self, sid):
        for mapping in self._mappings:
            if mapping.sid == sid:
                char_string = mapping.get_type1_char_string()
                return char_string.get_width()
        return self._get_not_def_width(self.get_nominal_width(sid), self.get_default_width(sid))

    def _get_not_def_width(self, nominal_width, default_width):
        char_string = self._get_type_1_char_string('.notdef')
        if char_string.get_width() != 0:
            return char_string.get_width() + nominal_width
        else:
            return default_width

    def get_encoding(self):
        return self.encoding

    def set_encoding(self, encoding):
        self.encoding = encoding

    def get_charset(self):
        return self.charset

    def set_charset(self, charset):
        self.charset = charset

    def get_sid_for_name(self, name):
        for m in self._mappings:
            if m.name == name:
                return m.sid
        return 0  # .notdef

    def get_char_strings_dict(self):
        return self.char_strings_dict

    def _get_type_1_char_string(self, name, sid=None):
        if sid is None:
            sid = self.get_sid_for_name(name)
        if name in self.char_string_cache:
            return self.char_string_cache[name]
        parser = Type2CharStringParser()
        sequence = parser.parse(self.char_strings_dict[name], self.global_subr_index, self.local_subr_index)
        char_string = Type2CharString(self.name, name, sequence, self.get_default_width(sid),
                                      self.get_nominal_width(sid))
        self.char_string_cache[name] = char_string
        return char_string

    def get_default_width(self, sid):
        width = self.get_property('defaultWidthX')
        if width is None:
            return 1000
        return width

    def get_nominal_width(self, sid):
        width = self.get_property('nominalWidthX')
        if width is None:
            return 0
        return width

    def __repr__(self):
        return (self.__class__.__name__ +
                ' [name = {0}, topdict={1}, privatedict={2}, endoding={3}, charset={4} charstrings={5}'.format(
                    self.name, self.top_dict, self.private_dict, self.encoding, self.charset, self.char_strings_dict))

    def set_global_subr_index(self, global_subr_index):
        self.global_subr_index = global_subr_index

    def get_global_subr_index(self):
        return self.global_subr_index

    def set_local_subr_index(self, local_subr_index):
        self.local_subr_index = local_subr_index

    def get_local_subr_index(self):
        return self.local_subr_index


class Mapping(object):
    def __init__(self, code, sid, name, char_string_bytes):
        """
        :param int code:
        :param int sid:
        :param str name:
        :param bytearray char_string_bytes:
        """
        self.code = code
        self.sid = sid
        self.name = name
        self.bytes = char_string_bytes
