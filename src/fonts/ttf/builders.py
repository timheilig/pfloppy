import datetime
from pdfbox.fonts.walkable import WalkableString as WalkableString


class CmapFormat(object):
    def __init__(self, sub_table_format, content):
        self.sub_table_format = sub_table_format
        self.content = content
        self.language = self.content.read_integer(2)
        self.char_to_glyph_id_map = {}
        self.segment_count = 0
        self.end_code = []
        self.start_code = []
        self.id_delta = []
        self.id_range_offset = []
        self.glyph_index_array = []

        if sub_table_format == 0:
            self.handle_format_zero()
        elif sub_table_format == 4:
            self.handle_format_four()
        elif sub_table_format == 6:
            self.handle_format_six()
        else:
            raise ValueError("Unhandled cmap subtable format")

    def handle_format_zero(self):
        for i in range(256):
            self.char_to_glyph_id_map[i] = self.content.read_integer(1)

    def handle_format_four(self):
        segment_count_times_two = self.content.read_integer(2)
        self.segment_count = segment_count_times_two / 2
        search_range = self.content.read_integer(2)
        entry_selector = self.content.read_integer(2)
        range_shift = self.content.read_integer(2)
        for i in range(self.segment_count):
            self.end_code.append(self.content.read_integer(2))
        reserved_pad = self.content.read_integer(2)
        for i in range(self.segment_count):
            self.start_code.append(self.content.read_integer(2))
        for i in range(self.segment_count):
            self.id_delta.append(self.content.read_integer(2))
        for i in range(self.segment_count):
            self.id_range_offset.append(self.content.read_integer(2))
        while not self.content.is_exhausted():
            self.glyph_index_array.append(self.content.read_integer(2))

    def handle_format_six(self):
        first_code = self.content.read_integer(2)
        entry_count = self.content.read_integer(2)
        for i in range(first_code, first_code + entry_count):
            self.char_to_glyph_id_map[i] = self.content.read_integer(2)
        assert(self.content.is_exhausted())

    def character_to_glyph_id(self, character_code):
        if character_code in self.char_to_glyph_id_map:
            return self.char_to_glyph_id_map[character_code]
        glyph_id = 0
        for i in range(self.segment_count):
            if character_code <= self.end_code[i]:
                if character_code < self.start_code[i]:
                    glyph_id = 0
                elif self.id_range_offset[i] == 0:
                    glyph_id = character_code + self.id_delta[i]
                else:
                    # id range offset is a byte value, (so we divide by 2 to get an index)
                    # id_range_offset is relative to it's actual location, so we need to add the current
                    # index back in. for example if you had {1 => 2, 2 => 6, 15 => 19, 16 => 35)
                    # start_code would be [1, 15], end_code would be [2, 16], id_range_offset would be [4 6]
                    # [4 6] [2 6 19 35]
                    index = self.id_range_offset[i] / 2 + i - self.segment_count + character_code - self.start_code[i]
                    glyph_id = self.glyph_index_array[index]
                glyph_id %= 65536
        self.char_to_glyph_id_map[character_code] = glyph_id
        return glyph_id


class TtfTable(object):
    def __init__(self, content):
        """
        :param WalkableString content:
        :return:
        """
        self.content = content

    def parse(self):
        pass

    def serialize(self):
        return self.content


class TtfHeadTable(TtfTable):
    def __init__(self, content):
        super(TtfHeadTable, self).__init__(content)
        self.sfnt_revision = None
        self.optimized_for_cleartype = False
        self.apply_lsb = False
        self.emsize = 0
        self.ascent = 0
        self.descent = 0
        self.font_bounding_box = [0, 0, 0, 0]
        self.macstyle = 0
        self.index_to_loc_is_long = False
        self.created_time = datetime.datetime.now()
        self.modified_time = self.created_time

    def parse(self):
        self.content.set_position(4, WalkableString.RELATIVE_TO_START)  # skip over version
        self.sfnt_revision = self.content.read_integer(4)
        self.content.set_position(8, WalkableString.RELATIVE_TO_CURRENT)  # skipping checksum and magic number
        flags = self.content.read_integer(2)
        if flags & (1 << 13) > 0:
            self.optimized_for_cleartype = True
        if flags & (1 << 1) > 0:
            self.apply_lsb = True
        self.emsize = self.content.read_integer(2)
        self.ascent = self.emsize * .8
        self.descent = self.emsize - self.ascent
        self.created_time = self.content.read_font_epoch_time()
        self.modified_time = self.content.read_font_epoch_time()
        for i in range(4):
            self.font_bounding_box[i] = self.content.read_integer(2, True)
        self.macstyle = self.content.read_integer(2)
        self.content.set_position(4, WalkableString.RELATIVE_TO_CURRENT)  # skipping 2 shorts
        self.index_to_loc_is_long = self.content.read_integer(2) > 0
        assert(self.content.read_integer(2) == 0)
        assert(self.content.is_exhausted())


class TtfHheaTable(TtfTable):
    def __init__(self, content):
        super(TtfHheaTable, self).__init__(content)
        self.ascent = 0
        self.descent = 0
        self.ascent_add = False
        self.descent_add = False
        self.linegap = 0
        self.advance_width_max = 0
        self.width_count = 0

    def parse(self):
        self.content.set_position(4, WalkableString.RELATIVE_TO_START)  # skip over version
        self.ascent = self.content.read_integer(2, True)
        self.descent = self.content.read_integer(2, True)
        self.linegap = self.content.read_integer(2, True)
        self.advance_width_max = self.content.read_integer(2)
        self.content.set_position(22, WalkableString.RELATIVE_TO_CURRENT)  # skipping 11 shorts
        self.width_count = self.content.read_integer(2)
        assert(self.content.is_exhausted())


class TtfMaxpTable(TtfTable):
    def __init__(self, content):
        super(TtfMaxpTable, self).__init__(content)
        self.glyph_count = 0

    def parse(self):
        self.content.set_position(4, WalkableString.RELATIVE_TO_START)  # skip over version
        self.glyph_count = self.content.read_integer(2)
        self.content.set_position(26, WalkableString.RELATIVE_TO_CURRENT)  # skipping 13 shorts
        assert(self.content.is_exhausted())


class TtfCmapTable(TtfTable):
    def __init__(self, content):
        super(TtfCmapTable, self).__init__(content)
        self.sub_tables = {}

    def parse(self):
        version = self.content.read_integer(2)
        number_of_sub_tables = self.content.read_integer(2)
        for i in range(number_of_sub_tables):
            platform_id = self.content.read_integer(2)
            platform_specific_id = self.content.read_integer(2)
            offset = self.content.read_integer(4)
            current_position = self.content.get_position()
            self.content.set_position(offset, WalkableString.RELATIVE_TO_START)
            sub_table_format = self.content.read_integer(2)
            if sub_table_format < 8:
                length = self.content.read_integer(2)
                sub_table_content = self.content.read_chunk(length - 4)
            else:
                self.content.set_position(2, WalkableString.RELATIVE_TO_CURRENT)  # skip the '.0' for the long formats
                length = self.content.read_integer(4)
                sub_table_content = self.content.read_chunk(length - 8)
            self.sub_tables[(platform_id, platform_specific_id)] = self.create_subtable(
                sub_table_format, sub_table_content)
            self.content.set_position(current_position)

    @staticmethod
    def create_subtable(sub_table_format, content):
        return CmapFormat(sub_table_format, content)


class TtfFont(object):
    """
        { CHR('a','c','n','t'), N_("accent attachment table") },
    { CHR('a','v','a','r'), N_("axis variation table") },
    { CHR('B','A','S','E'), N_("Baseline table (OT version)") },
    { CHR('b','d','a','t'), N_("bitmap data table (AAT version)") },
    { CHR('B','D','F',' '), N_("BDF bitmap properties table") },
    { CHR('b','h','e','d'), N_("bitmap font header table") },
    { CHR('b','l','o','c'), N_("bitmap location table (AAT version)") },
    { CHR('b','s','l','n'), N_("baseline table (AAT version)") },
    { CHR('C','F','F',' '), N_("PostScript font program (Compact Font Format)") },
    { CHR('C','I','D',' '), N_("Obsolete table for a type1 CID keyed font") },
    { CHR('c','m','a','p'), N_("character code mapping table") },
    { CHR('c','v','a','r'), N_("CVT variation table") },
    { CHR('c','v','t',' '), N_("control value table") },
    { CHR('D','S','I','G'), N_("digital signature table") },
    { CHR('E','B','D','T'), N_("bitmap data table (OT version)") },
    { CHR('E','B','L','C'), N_("bitmap location table (OT version)") },
    { CHR('E','B','S','C'), N_("embedded bitmap scaling control table") },
    { CHR('E','L','U','A'), N_("electronic end user license table") },
    { CHR('f','d','s','c'), N_("font descriptor table") },
    { CHR('f','e','a','t'), N_("layout feature table") },
    { CHR('F','e','a','t'), N_("SIL Graphite layout feature table") },
    { CHR('F','F','T','M'), N_("FontForge time stamp table") },
    { CHR('f','m','t','x'), N_("font metrics table") },
    { CHR('f','p','g','m'), N_("font program table") },
    { CHR('f','v','a','r'), N_("font variation table") },
    { CHR('g','a','s','p'), N_("grid-fitting and scan-conversion procedure table") },
    { CHR('G','D','E','F'), N_("glyph definition table") },
    { CHR('G','l','a','t'), N_("Graphite glyph attribute table") },
    { CHR('G','l','o','c'), N_("Graphite glyph location in Glat table") },
    { CHR('g','l','y','f'), N_("glyph outline table") },
    { CHR('G','P','O','S'), N_("glyph positioning table") },
    { CHR('g','v','a','r'), N_("glyph variation table") },
    { CHR('G','S','U','B'), N_("glyph substitution table") },
    { CHR('h','d','m','x'), N_("horizontal device metrics table") },
    { CHR('h','h','e','a'), N_("horizontal header table") },
    { CHR('h','m','t','x'), N_("horizontal metrics table") },
    { CHR('h','s','t','y'), N_("horizontal style table") },
    { CHR('j','u','s','t'), N_("justification table (AAT version)") },
    { CHR('J','S','T','F'), N_("justification table (OT version)") },
    { CHR('k','e','r','n'), N_("kerning table") },
    { CHR('l','c','a','r'), N_("ligature caret table") },
    { CHR('l','o','c','a'), N_("glyph location table") },
    { CHR('L','T','S','H'), N_("linear threshold table") },
    { CHR('M','A','T','H'), N_("math table") },
    { CHR('m','a','x','p'), N_("maximum profile table") },
    { CHR('M','M','S','D'), N_("Multi-Master table, obsolete") },
    { CHR('M','M','F','X'), N_("Multi-Master table, obsolete") },
    { CHR('m','o','r','t'), N_("metamorphosis table") },
    { CHR('m','o','r','x'), N_("extended metamorphosis table") },
    { CHR('n','a','m','e'), N_("name table") },
    { CHR('o','p','b','d'), N_("optical bounds table") },
    { CHR('O','S','/','2'), N_("OS/2 and Windows specific metrics table") },
    { CHR('P','C','L','T'), N_("PCL 5 data table") },
    { CHR('P','f','E','d'), N_("FontForge font debugging table") },
    { CHR('p','o','s','t'), N_("glyph name and PostScript compatibility table") },
    { CHR('p','r','e','p'), N_("control value program table") },
    { CHR('p','r','o','p'), N_("properties table") },
    { CHR('S','i','l','f'), N_("SIL Graphite rule table") },
    { CHR('S','i','l','l'), N_("(unspecified) SIL Graphite table") },
    { CHR('S','i','l','t'), N_("unknown SIL table") },
    { CHR('T','e','X',' '), N_("TeX table") },
    { CHR('t','r','a','k'), N_("tracking table") },
    { CHR('T','Y','P','1'), N_("Obsolete table for a type1 font") },
    { CHR('V','D','M','X'), N_("vertical device metrics table") },
    { CHR('v','h','e','a'), N_("vertical header table") },
    { CHR('v','m','t','x'), N_("vertical metrics table") },
    { CHR('V','O','R','G'), N_("vertical origin table") },
    { CHR('Z','a','p','f'), N_("glyph reference table") },
    """
    _table_parser_map = {
        'cmap': TtfCmapTable,  # character code mapping table
        'head': TtfHeadTable,  # font header table
        'hhea': TtfHheaTable,  # horizontal header table
        'maxp': TtfMaxpTable  # maximum profile table
    }

    def __init__(self):
        self.onlystrikes = False
        self.onlyonestrike = False
        self.use_typo_metrics = True
        self._tables = {}

    def glyph_count(self):
        loca_length = len(self._tables['loca'].data)
        if self._tables['head'].index_to_loc_is_long:
            glyph_count = loca_length / 4 - 1
        else:
            glyph_count = loca_length / 2 - 1

        if glyph_count > 0:
            return glyph_count
        else:
            return 0

    def check_table_conflicts(self):
        conflicts = [
            ('CFF ', 'loca', 'CID ', 'TYP1'),
            ('kern', 'GPOS'),
            ('BASE', 'bsln'),
            ('mort', 'morx', 'GSUB')
        ]
        for conflict in conflicts:
            number_tables = 0
            for table in conflict:
                if table in self._tables:
                    number_tables += 1
            if number_tables > 1:
                print 'Conflict multiple tables defined in ', conflict

    def read_from_file(self, font_file):
        content = font_file.read()
        self.read_from_content(content)

    def read_from_content(self, content):
        walkable_content = WalkableString(content)
        version = walkable_content.read_chunk(4)
        if version == 'ttcf':
            raise ValueError("Collections not supported")
        table_count = walkable_content.read_integer(2)
        # skip searchRange, entrySelector, rangeshift
        walkable_content.set_position(6, WalkableString.RELATIVE_TO_CURRENT)
        for i in range(table_count):
            tag = walkable_content.read_chunk(4).data
            checksum = walkable_content.read_integer(4)
            offset = walkable_content.read_integer(4)
            length = walkable_content.read_integer(4)
            if offset and length:
                current_position = walkable_content.get_position()
                walkable_content.set_position(offset, WalkableString.RELATIVE_TO_START)
                if tag in self._table_parser_map:
                    table_class = self._table_parser_map[tag]
                    self._tables[tag] = table_class(walkable_content.read_chunk(length))
                else:
                    self._tables[tag] = TtfTable(walkable_content.read_chunk(length))
                self._tables[tag].parse()
                walkable_content.set_position(current_position, WalkableString.RELATIVE_TO_START)
        self.check_table_conflicts()