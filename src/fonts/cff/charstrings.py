from commands import Command
from rawdata import *
from math import ceil

TYPE1_VOCABULARY = {
    (1,): "hstem",
    (3,): "vstem",
    (4,): "vmoveto",
    (5,): "rlineto",
    (6,): "hlineto",
    (7,): "vlineto",
    (8,): "rrcurveto",
    (9,): "closepath",
    (10,): "callsubr",
    (11,): "return",
    (12,): "escape",
    (12, 0): "dotsection",
    (12, 1): "vstem3",
    (12, 2): "hstem3",
    (12, 6): "seac",
    (12, 7): "sbw",
    (12, 12): "div",
    (12, 16): "callothersubr",
    (12, 17): "pop",
    (12, 33): "setcurrentpoint",
    (13,): "hsbw",
    (14,): "endchar",
    (21,): "rmoveto",
    (22,): "hmoveto",
    (30,): "vhcurveto",
    (31,): "hvcurveto",
}

TYPE2_VOCABULARY = {
    (1,): "hstem",
    (3,): "vstem",
    (4,): "vmoveto",
    (5,): "rlineto",
    (6,): "hlineto",
    (7,): "vlineto",
    (8,): "rrcurveto",
    (10,): "callsubr",
    (11,): "return",
    (12,): "escape",
    (12, 3): "and",
    (12, 4): "or",
    (12, 5): "not",
    (12, 9): "abs",
    (12, 10): "add",
    (12, 11): "sub",
    (12, 12): "div",
    (12, 14): "neg",
    (12, 15): "eq",
    (12, 18): "drop",
    (12, 20): "put",
    (12, 21): "get",
    (12, 22): "ifelse",
    (12, 23): "random",
    (12, 24): "mul",
    (12, 26): "sqrt",
    (12, 27): "dup",
    (12, 28): "exch",
    (12, 29): "index",
    (12, 30): "roll",
    (12, 34): "hflex",
    (12, 35): "flex",
    (12, 36): "hflex1",
    (12, 37): "flex1",
    (14,): "endchar",
    (18,): "hstemhm",
    (19,): "hintmask",
    (20,): "cntrmask",
    (21,): "rmoveto",
    (22,): "hmoveto",
    (23,): "vstemhm",
    (24,): "rcurveline",
    (25,): "rlinecurve",
    (26,): "vvcurveto",
    (27,): "hhcurveto",
    (28,): "shortint",
    (29,): "callgsubr",
    (30,): "vhcurveto",
    (31,): "hvcurveto",
}


class Type1CharString(object):
    def __init__(self, font_name, glyph_name, sequence=()):
        self._font_name = font_name
        self._glyph_name = glyph_name
        self._sequence = sequence
        self._current_position = Point()
        self._bounding_box = BoundingBox()
        self._width = 0
        self._rendered = False
        self._left_side_bearing = None
        self._is_flex = False
        self._flex_points = []

    def handle_sequence(self, sequence):
        """
        Handler for a sequence of CharStringCommands.
        :param Iterable sequence: Sequence of commands
        :rtype: list of remaining items on stack
        """
        stack = []
        for obj in sequence:
            if isinstance(obj, Command):
                results = self._handle_command(stack, obj)
                del stack[:]
                if results:
                    stack.extend(results)
            else:
                stack.append(obj)
        return stack

    def get_bounds(self):
        """
        Returns the bounds of the renderer path.
        :rtype: tuple representing rectangle bounds
        """
        if not self._rendered:
            self.render()
        return self._bounding_box

    def get_width(self):
        """
        Returns the advance width of the glyph.
        :rtype: float
        """
        if not self._rendered:
            self.render()
        return self._width

    @staticmethod
    def get_path():
        """
        Returns the path of the character.
        :rtype: GeneralPath
        """
        return None

    def get_sequence(self):
        """
        Returns the charstring sequence of commands.
        :rtype: list of commands
        """
        return self._sequence

    def render(self):
        """
        Renders the Type 1 char string sequence to a GeneralPath.
        """
        self._left_side_bearing = Point()

        self.handle_sequence(self._sequence)

    def _hsbw(self, stack):
        left_side_bearing = Point(x=stack[0])
        self._width = stack[1]
        self._current_position = left_side_bearing

    def _handle_command(self, stack, command):
        """
        Process command, returning any results that should be pushed back onto the stack
        :param list stack:
        :param Command command:
        :rtype: list
        """
        name = TYPE1_VOCABULARY[command.key]
        if name == 'rmoveto':  # since we aren't drawing, only checking bounding box, line and move can share logic
            if self._is_flex:
                self._flex_points.append(Point(stack[0], stack[1]))
            else:
                self._rline_to(stack[0], stack[1])
        elif name == 'vmoveto':
            if self._is_flex:
                # not in the Type 1 spec, but exists in some fonts
                self._flex_points.append(Point(y=stack[0]))
            else:
                self._rline_to(0, stack[0])
        elif name == 'hmoveto':
            if self._is_flex:
                # not in the Type 1 spec, but exists in some fonts
                self._flex_points.append(Point(x=stack[0]))
            else:
                self._rline_to(stack[0], 0)
        elif name == 'rlineto':
            self._rline_to(stack[0], stack[1])
        elif name == 'hlineto':
            self._rline_to(stack[0], 0)
        elif name == 'vlineto':
            self._rline_to(0, stack[0])
        elif name == 'rrcurveto':
            self._rrcurve_to(stack[0], stack[1], stack[2],
                             stack[3], stack[4], stack[5])
        elif name == 'closepath':
            pass  # we are only checking the bounding box, so nothing to do here
        elif name == 'sbw':
            left_side_bearing = Point(stack[0], stack[1])
            self._width = stack[2]
            self._current_position = left_side_bearing
        elif name == 'hsbw':
            self._hsbw(stack)
        elif name == 'vhcurveto':
            self._rrcurve_to(0, stack[0], stack[1],
                             stack[2], stack[3], 0)
        elif name == 'hvcurveto':
            self._rrcurve_to(stack[0], 0, stack[1],
                             stack[2], 0, stack[3])
        elif name == 'setcurrentpoint':
            self.set_current_point(stack[0], stack[1])
        elif name == 'callothersubr':
            self._call_other_subr(stack[0])
        elif name == 'div':
            result = float(stack[-2]) / float(stack[-1])
            del stack[-2:-1]
            return [result]
        elif (name == 'hstem' or name == 'vstem' or
              name == 'hstem3' or name == 'vstem3' or name == 'dotsection'):
            # ignore hints
            pass
        elif name == 'seac':
            # currently ignoring the drawing of standard encoding accented characters, it's non-trivial to compute
            # bbox calculations
            pass
        elif name == 'endchar':
            # end
            pass
        else:
            raise ValueError("Unknown command: " + name)
        return []

    def set_current_point(self, x, y):
        """
        Sets the current absolute point without performing a moveto.
        Used only with results from callothersubr
        :param int x:
        :param int y:
        """
        self._current_position = Point(x, y)
        self._adjust_bounding_box()

    def _call_other_subr(self, entry_number):
        """
        Turn on/off flex points
        :param int entry_number: 0 - turn flex recording off (and process flex points), 1 - turn flex recording on
        :return:
        """
        if entry_number == 0:
            self._is_flex = False

            # first point is relative to reference point, this changes it to be relative to current point
            reference = self._flex_points[0]
            first = self._flex_points[1]
            first.x += reference.x
            first.y += reference.y

            self._rrcurve_to(first.x, first.y,
                             self._flex_points[2].x, self._flex_points[2].y,
                             self._flex_points[3].x, self._flex_points[3].y)

            self._rrcurve_to(self._flex_points[4].x, self._flex_points[4].y,
                             self._flex_points[5].x, self._flex_points[5].y,
                             self._flex_points[6].x, self._flex_points[6].y)
            self._flex_points = []
        elif entry_number == 1:
            self._is_flex = True
        else:
            raise ValueError("Unexpected other subroutine: " + entry_number)

    def _adjust_bounding_box(self):
        """
        Adjust bounding box to take into account current point
        :return:
        """
        if self._current_position.x < self._bounding_box.min_x:
            self._bounding_box.min_x = self._current_position.x
        if self._current_position.x > self._bounding_box.max_x:
            self._bounding_box.max_x = self._current_position.x
        if self._current_position.y < self._bounding_box.min_y:
            self._bounding_box.min_y = self._current_position.y
        if self._current_position.y > self._bounding_box.max_y:
            self._bounding_box.max_y = self._current_position.y

    def _rline_to(self, delta_x, delta_y):
        """
        Simulate a relative straight line move and set the new current_position
        :param int delta_x:
        :param int delta_y:
        :return:
        """
        self._current_position.x += delta_x
        self._current_position.y += delta_y
        self._adjust_bounding_box()

    def _rrcurve_to(self, delta_x1, delta_y1, delta_x2, delta_y2, delta_x3, delta_y3):
        """
        Simulate a relative curve set the new current_position
        :param int delta_x1:
        :param int delta_y1:
        :param int delta_x2:
        :param int delta_y2:
        :param int delta_x3:
        :param int delta_y3:
        :return:
        """
        # TODO(theilig) Bounding box calculation might need to consider control point
        self._current_position.x += delta_x1 + delta_x2 + delta_x3
        self._current_position.y += delta_y1 + delta_y2 + delta_y3
        self._adjust_bounding_box()


class Type2CharString(Type1CharString):
    """
    Represents a Type 2 CharString by converting it into an equivalent Type 1 CharString.
    """
    def __init__(self, font_name, glyph_name, sequence, default_width, nominal_width):
        super(Type2CharString, self).__init__(font_name, glyph_name)
        self._default_width = default_width or 0
        self._nominal_width = nominal_width or 0
        self._path_count = 0
        self._type2sequence = sequence
        self._sequence = self._convert_type2_to_type1(sequence)

    def get_width(self):
        width = super(Type2CharString, self).get_width()
        if width == 0:
            return self._default_width
        else:
            return width

    def get_type2_sequence(self):
        return self._type2sequence

    def _get_width_from_stack(self, stack):
        # we have a width if there is an odd number on the stack
        # TODO (theilig) understand why this is true
        if len(stack) % 2 == 1:
            width = stack.pop(0) + self._nominal_width
        else:
            width = self._default_width

        return width

    def _convert_type2_to_type1(self, type2_sequence):
        """
        Converts a sequence of Type 2 commands into a sequence of Type 1 commands.
        :param Iterable type2_sequence:
        :rtype: Iterable
        """
        type1sequence = []
        stack = []
        for obj in type2_sequence:
            if isinstance(obj, Command):
                self._convert_command(stack, obj, type1sequence)
                del stack[:]
            else:
                stack.append(obj)
        return type1sequence

    @staticmethod
    def _add_command(command, stack, type1sequence):
        """
        :param Command command:
        :param list stack:
        :param list type1sequence:
        :return:
        """
        if stack:
            type1sequence.extend(stack)
        type1sequence.append(command)

    def _convert_command(self, stack, command, type1sequence):
        name = TYPE2_VOCABULARY[command.key]
        if name == 'hstem':
            stack = self._clear_stack(stack, len(stack) % 2 != 0, type1sequence)
            self._expand_stem_hints(stack, True, type1sequence)
        elif name == 'vstem':
            stack = self._clear_stack(stack, len(stack) % 2 != 0, type1sequence)
            self._expand_stem_hints(stack, True, type1sequence)
        elif name == 'vmoveto':
            stack = self._clear_stack(stack, len(stack) > 1, type1sequence)
            self._mark_path(type1sequence)
            self._add_command(command, stack, type1sequence)
        elif name == 'rlineto':
            self._add_command_list(stack, 2, command, type1sequence)
        elif name == 'hlineto':
            self._draw_alternating_line(stack, True, type1sequence)
        elif name == 'vlineto':
            self._draw_alternating_line(stack, False, type1sequence)
        elif name == 'rrcurveto':
            self._add_command_list(stack, 6, command, type1sequence)
        elif name == 'endchar':
            stack = self._clear_stack(stack, len(stack) == 5, type1sequence)
            self._close_path(type1sequence)
            if len(stack) == 4:
                stack.insert(0, 0)
                self._add_command(Command((12, 6)), stack, type1sequence)
            else:
                self._add_command(command, stack, type1sequence)
        elif name == 'rmoveto':
            stack = self._clear_stack(stack, len(stack) > 2, type1sequence)
            self._mark_path(type1sequence)
            self._add_command(command, stack, type1sequence)
        elif name == 'hmoveto':
            stack = self._clear_stack(stack, len(stack) > 1, type1sequence)
            self._mark_path(type1sequence)
            self._add_command(command, stack, type1sequence)
        elif name == 'vhcurveto':
            self._draw_alternating_curve(stack, False, type1sequence)
        elif name == 'hvcurveto':
            self._draw_alternating_curve(stack, True, type1sequence)
        elif name == 'hflex':
            stack = [stack[0], 0, stack[1], stack[2], stack[3], 0, stack[4], 0, stack[5], -stack[2], stack[6], 0]
            self._add_command_list(stack, 6, Command((8,)), type1sequence)
        elif name == 'flex':
            self._add_command_list(stack, 6, Command((8,)), type1sequence)
        elif name == 'hflex1':
            stack.insert(5, 0)
            stack.insert(7, 0)
            stack.append(0)
            self._add_command_list(stack, 6, Command((8,)), type1sequence)
        elif name == 'flex1':
            dx = 0
            dy = 0
            for i in range(start=0, stop=10, step=2):
                dx += stack[i]
                dy += stack[i + 1]
            if abs(dx) > abs(dy):
                self._add_command_list(stack[0:11].append(-dy), 6, Command((8,)), type1sequence)
            else:
                stack.insert(10, -dx)
                self._add_command_list(stack[0:12], 6, Command((8,)), type1sequence)
        elif name == 'hstemhm':
            stack = self._clear_stack(stack, len(stack) % 2 != 0, type1sequence)
            self._expand_stem_hints(stack, True, type1sequence)
        elif name == 'hintmask' or name == 'cntrmask':
            stack = self._clear_stack(stack, len(stack) % 2 != 0, type1sequence)
            if len(stack) > 0:
                self._expand_stem_hints(stack, False, type1sequence)
        elif name == 'vstemhm':
            stack = self._clear_stack(stack, len(stack) % 2 != 0, type1sequence)
            self._expand_stem_hints(stack, False, type1sequence)
        elif name == 'rcurveline':
            self._add_command_list(stack[0:-2], 6, Command((8,)), type1sequence)
            self._add_command(stack[-2:], Command((5,)), type1sequence)
        elif name == 'rlinecurve':
            self._add_command_list(stack[0:-6], 2, Command((5,)), type1sequence)
            self._add_command(Command((8,)), stack[-6:], type1sequence)
        elif name == 'vvcurveto':
            self._draw_curve(stack, False, type1sequence)
        elif name == 'hhcurveto':
            self._draw_curve(stack, True, type1sequence)
        else:
            self._add_command(command, stack, type1sequence)

    def _clear_stack(self, stack, width_present, sequence):
        if len(sequence) == 0:
            if width_present:
                width = stack.pop(0) + self._nominal_width
            else:
                width = self._default_width
            self._add_command(Command((13,)), [0, width], sequence)
        return stack

    def _expand_stem_hints(self, stack, is_horizontal, sequence):
        # TODO(theilig) this hasn't been implemented upstream
        pass

    def _mark_path(self, sequence):
        if self._path_count > 0:
            self._close_path(sequence)
        self._path_count += 1

    def _close_path(self, sequence):
        if self._path_count > 0:
            command = sequence[-1]
        else:
            command = None

        close_path_command = Command((9,))

        if command and command.key != close_path_command.key:
            self._add_command(close_path_command, [], sequence)

    def _draw_alternating_line(self, stack, is_horizontal, sequence):
        while len(stack) > 0:
            if is_horizontal:
                command = Command((6,))
            else:
                command = Command((7,))

            value = stack.pop(0)
            self._add_command(command, [value], sequence)
            is_horizontal = not is_horizontal

    def _draw_alternating_curve(self, stack, is_horizontal, sequence):
        while len(stack) > 0:
            is_last = len(stack) == 5

            if is_horizontal:
                curve_stack = [stack[0], 0, stack[1], stack[2]]
                if is_last:
                    curve_stack.append(stack[4])
                else:
                    curve_stack.append(0)
                curve_stack.append(stack[3])
            else:
                curve_stack = [0]
                curve_stack.extend(stack[0:4])
                if is_last:
                    curve_stack.append(stack[4])
                else:
                    curve_stack.append(0)
            if is_last:
                del stack[0:5]
            else:
                del stack[0:4]
            self._add_command(Command((8,)), curve_stack, sequence)
            is_horizontal = not is_horizontal

    def _draw_curve(self, stack, is_horizontal, sequence):
        while len(stack) > 0:
            is_first = len(stack) % 4 == 1
            if is_horizontal:
                if is_first:
                    curve_stack = [stack[1], stack[0], stack[2], stack[3], stack[4]]
                else:
                    curve_stack = [stack[0], 0, stack[1], stack[2], stack[3]]
            else:
                if is_first:
                    curve_stack = stack[0:5]
                else:
                    curve_stack = [0].extend(stack[0:4])
            if is_first:
                del stack[0:5]
            else:
                del stack[0:4]
            self._add_command(Command((8,)), curve_stack, sequence)

    def _add_command_list(self, stack, slice_length, command, sequence):
        while len(stack) >= slice_length:
            self._add_command(command, stack[0:slice_length], sequence)
            del stack[0:slice_length]


class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class BoundingBox(object):
    def __init__(self):
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0


class Type2CharStringParser(object):
    def __init__(self):
        self._hstem_count = 0
        self._vstem_count = 0
        self._sequence = []

    def parse(self, data, global_subr_index, local_subr_index, init=True):

        local_subroutine_index_provided = local_subr_index and len(local_subr_index) > 0
        global_subroutine_index_provided = global_subr_index and len(global_subr_index) > 0
        if init:
            self._hstem_count = 0
            self._vstem_count = 0
            self._sequence = []
        while not data.is_exhausted():
            (operand_type, value) = read_unknown_thing(data, True)
            if value == (10,) and local_subroutine_index_provided:
                # process local subr command
                self.parse_subroutine(local_subr_index, global_subr_index, True)
            elif value == (29,) and global_subroutine_index_provided:
                self.parse_subroutine(global_subr_index, local_subr_index, False)
            elif value == (28,):
                # special handling for shortint which is a forward looking operator
                self._sequence.append(data.read_integer(2, True))
            elif operand_type == OPERAND_OPERATION:
                command = Command(value)
                if value == (1,) or value == (18,):
                    self._hstem_count += self._stack_size() / 2
                elif value == (3,) or value == (19,) or value == (20,) or value == (23,):
                    self._vstem_count += self._stack_size() / 2
                    if value == (19,) or value == (20,):
                        mask_length = self._get_mask_length()
                        for i in range(1, mask_length + 1):
                            data.read_integer(1)  # need to clear hintmask bytes, just throwing them out for now
                self._sequence.append(command)
            else:
                self._sequence.append(value)
        return self._sequence

    def parse_subroutine(self, index, other_index, local_routine):
        operand = self._sequence.pop(-1)
        number_subroutines = len(index)
        if number_subroutines < 1240:
            bias = 107
        elif number_subroutines < 33900:
            bias = 1131
        else:
            bias = 32768
        subroutine_index = bias + operand
        if subroutine_index < len(index):
            subroutine_bytes = index[subroutine_index]
            if local_routine:
                self.parse(subroutine_bytes, other_index, index, False)
            else:
                self.parse(subroutine_bytes, index, other_index, False)
            last_item = self._sequence[-1]
            if isinstance(last_item, Command) and last_item.key == (11,):
                self._sequence.pop(-1)  # remove "return" command

    def _get_mask_length(self):
        hint_count = self._hstem_count + self._vstem_count
        if hint_count > 0:
            return int(ceil(hint_count / 8.0))
        else:
            return 1

    def _stack_size(self):
        count = 0
        index = -1
        while index > -len(self._sequence):
            if isinstance(self._sequence[index], Command):
                return count
            count += 1
            index -= 1
        return count