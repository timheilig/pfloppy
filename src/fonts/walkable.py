import datetime


class WalkableString(object):
    RELATIVE_TO_START = 0
    RELATIVE_TO_CURRENT = 1
    RELATIVE_TO_END = 2

    def __init__(self, data):
        self.data = data
        self.position = 0

    def read_integer(self, count, signed=False):
        value = 0
        negative = False
        for i in range(count):
            value <<= 8
            value += ord(self.data[self.position])
            self.position += 1
            if i == 0 and signed and value & 0x80 == 0x80:
                negative = True
        if negative:
            value -= 2 ** (count * 8)
        return value

    def read_chunk(self, chunk_size):
        chunk = WalkableString(self.data[self.position:self.position + chunk_size])
        self.position += chunk_size
        return chunk

    def set_position(self, new_position, reference_point=RELATIVE_TO_START):
        if reference_point == 0:
            self.position = new_position
        elif reference_point == 1:
            self.position += new_position
        else:
            self.position = len(self.data) - new_position

    def get_position(self):
        return self.position

    def read_font_epoch_time(self):
        seconds_adjustment = 2082844800  # seconds between 1904 and 1970
        time_read = self.read_integer(8)
        seconds_since_epoch = time_read - seconds_adjustment
        return datetime.datetime.fromtimestamp(seconds_since_epoch)

    def is_exhausted(self):
        return self.position == len(self.data)

    def get_data(self):
        return self.data

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.data == other
        else:
            return self.data == other.get_data()

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return ":".join("{:02x}".format(ord(c)) for c in self.data)