from magic.utils import print_debugger
from enum import (auto, Enum)
from collections import deque
from itertools import chain
from collections import namedtuple
import functools
Wizard = namedtuple('Wizard', ['x', 'y', 'orientation'])

class WizAction(Enum):
    none = auto()
    walk = auto()
    rotate_left = auto()
    rotate_right = auto()
    jump = auto()
    power = auto()
    fn1_call = auto()
    fn2_call = auto()
    halt = auto()

    blue_walk = auto()
    blue_rotate_left = auto()
    blue_rotate_right = auto()
    blue_jump = auto()
    blue_power = auto()
    blue_fn1_call = auto()
    blue_fn2_call = auto()
    blue_halt = auto()

    red_walk = auto()
    red_rotate_left = auto()
    red_rotate_right = auto()
    red_jump = auto()
    red_power = auto()
    red_fn1_call = auto()
    red_fn2_call = auto()
    red_halt = auto()

    yellow_walk = auto()
    yellow_rotate_left = auto()
    yellow_rotate_right = auto()
    yellow_jump = auto()
    yellow_power = auto()
    yellow_fn1_call = auto()
    yellow_fn2_call = auto()
    yellow_halt = auto()

class WizOrient(Enum):
    north = ( 0,  1)
    east  = ( 1,  0)
    south = ( 0, -1)
    west  = (-1,  0)


class Terrain(Enum):
    Unreachable = auto()
    Normal = auto()
    
    BlueDisk = auto()
    Disk = auto()
    RedDisk = auto()
    YellowDisk = auto()

    Elevator_Down = auto()
    Elevator_Up   = auto()

    Cliff_1 = auto()
    Cliff_1_BlueDisk = auto()
    Cliff_1_Disk = auto()
    Cliff_1_RedDisk = auto()
    Cliff_1_YellowDisk = auto()
    Cliff_1_Elevator_Down = auto()
    Cliff_1_Elevator_Up = auto

    Cliff_2 = auto()
    Cliff_2_BlueDisk = auto()
    Cliff_2_Disk = auto()
    Cliff_2_RedDisk = auto()
    Cliff_2_YellowDisk = auto()
    Cliff_2_Elevator_Down = auto()
    Cliff_2_Elevator_Up   = auto()

    Cliff_3 = auto()
    Cliff_3_BlueDisk = auto()
    Cliff_3_Disk = auto()
    Cliff_3_RedDisk = auto()
    Cliff_3_YellowDisk = auto()

class Thread:
    @print_debugger
    def __init__(self, actions, available_slots=12, name='Thread'):
        assert len(actions) <= available_slots, "Too many instructions"
        self._max_size = available_slots
        self.actions = actions

    @classmethod
    def main(cls, actions, available_slots, name='MainThread'):
        return cls(actions, available_slots, name)

    @classmethod
    def function_1(cls, actions, available_slots=8, name='Function_1'):
        return cls(actions, available_slots, name)

    @classmethod
    def function_2(cls, actions, available_slots=8, name='Function_2'):
        return cls(actions, available_slots, name)

class Program:
    @print_debugger
    def __init__(self, main, fn1, fn2, matrix, wizard):
        self.main = main
        self.fn1 = fn1
        self.fn2 = fn2
        self.matrix = matrix
        self.wizard = wizard
        self.instructions = deque([])
    
    @print_debugger
    def validate_next_action(self, some_action):
        return True
    @print_debugger
    def apply_action(self, some_action):
        permitted = validate_next_action(some_action)
        if not permitted:
            raise ValueError("Cannot do that, sorry")
        return some_action
    @print_debugger
    def collect(self):
        """Since recursion is frequently used
        `collect` performs a syntactic macro-expansion sort
        of vectorization, and saves the collection to `self.instructions`
        """
        instructions = deque([action for action in self.main.actions]) 
        saved = []
        trim_needed = False
        too_large = lambda some_list: len(some_list) > 256

        @print_debugger
        def sanitize(some_instructions, some_new_left):
            for instruction in some_instructions:
                some_new_left.append(instruction)
            return deque(some_new_left)

        while True:
            # Keep doing this until 
            # (a) the recursion limit has been exhauseted,
            # (b) all function calls have been replaced with non-function calls, or
            # (c) there are no more remaining instructions to collect 
            try:
                action = instructions.popleft()
                match (dispatch := action):
                    case WizAction.fn1_call | WizAction.blue_fn1_call | WizAction.red_fn1_call | WizAction.yellow_fn1_call:
                        new_left = [action for action in self.fn1.actions]
                        instructions = sanitize(instructions, new_left)
                    case WizAction.fn2_call | WizAction.blue_fn2_call | WizAction.red_fn2_call | WizAction.yellow_fn2_call:
                        new_left = [action for action in self.fn2.actions] 
                        instructions = sanitize(instructions, new_left)
                    case WizAction.blue_halt | WizAction.red_halt | WizAction.yellow_halt | WizAction.halt:
                        continue
                    case _:
                        if too_large(saved):
                            break
                        saved.append(dispatch)
            except IndexError:
                break

        if trim_needed:
            saved = [_ for _ in saved[0:recursion_limit]]
        self.instructions = saved

                    
class Matrix:
    @print_debugger
    def __init__(self, new_map):
        self.map = new_map

    @classmethod
    def from_dimensions(cls, width, height):
        template = [
            [ Terrain.Unreachable for _ in range(height) ]
            for __ in range(width) 
        ]
        return cls(template)

    @print_debugger
    def put(self, coordinate, terrain):
        mutation = self.map
        x, y = coordinate
        mutation[x][y] = terrain
        return Matrix(mutation)

    @print_debugger
    def get(self, coordinate):
        x, y = coordinate
        return self.map[x][y]


