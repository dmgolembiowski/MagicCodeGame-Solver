#from game.elements import *
from magic.utils import print_debugger
from magic.elements import *
from functools import partial

class Interrupt(Exception):
    pass

class Function1(Exception):
    pass

class Function2(Exception):
    pass

class Summary:
    @print_debugger
    def __init__(self, matrix_map, wizard, action, activated, blue_activated, red_activated, yellow_activated):
        self.matrix_map = matrix_map
        self.wizard = wizard
        self.action = action
        self.activated = activated
        self.blue_activated = blue_activated
        self.red_activated = red_activated
        self.yellow_activated = yellow_activated

    @print_debugger
    def __str__(self):
        return f"""Wizard({self.action})->{self.wizard}
        Map({self.matrix_map})
        ->Activated({self.activated})|Blue({self.blue_activated}|Red({self.red_activated})|Yellow({self.yellow_activated})
        """

class State:
    @print_debugger
    def __init__(self, program: Program):
        self.program = program
        self.__wizard__ = program.wizard
        self.__matrix__ = program.matrix
        self.available_actions = []
        self.activated = []
        self.blue_activated  = []
        self.red_activated = []
        self.yellow_activated = []
        self.history = [
            Summary(matrix_map=program.matrix,
                    wizard=program.wizard,
                    action=WizAction.none,
                    activated=self.activated,
                    blue_activated=self.blue_activated,
                    red_activated=self.red_activated,
                    yellow_activated=self.yellow_activated
            )
        ]

    @staticmethod
    def trunc(integer):
        if not integer >= 0:
            return 0
        return integer

    @property
    def wizard(self):
        return self.__wizard__

    @wizard.setter
    def wizard(self, new_wizard):
        self.__wizard__ = new_wizard

    @property
    def matrix(self):
        return self.__matrix__

    def wizard_status(self):
        return (self.wizard.x, self.wizard.y, self.wizard.orientation)
    @print_debugger
    def apply_action(self, wiz_action: WizAction):
        # status = self.wizard_status()
        match wiz_action:
            case WizAction.walk:
                self.apply_walk()
            case WizAction.rotate_left:
                self.apply_left_rotate()
            case WizAction.rotate_right:
                self.apply_right_rotate()
            case WizAction.jump:
                self.apply_jump()
            case WizAction.power:
                self.call_power()
            case WizAction.fn1_call:
                self.apply_function_1()
            case WizAction.fn2_call:
                self.apply_function_2()
            case WizAction.blue_walk:
                self.apply_walk(blue=True)
            case WizAction.blue_rotate_left:
                self.apply_left_rotate(blue=True)
            case WizAction.blue_rotate_right:
                self.apply_right_rotate(blue=True)
            case WizAction.blue_jump:
                self.apply_jump(blue=True)
            case WizAction.blue_power:
                self.call_power(blue=True)
            case WizAction.blue_fn1_call:
                self.apply_function_1(blue=True)
            case WizAction.blue_fn2_call:
                self.apply_function_2(blue=True)
            case WizAction.blue_halt:
                self.apply_halt(blue=True)
            case WizAction.red_walk:
                self.apply_walk(red=True)
            case WizAction.red_rotate_left:
                self.apply_left_rotate(red=True)
            case WizAction.red_rotate_right:
                self.apply_right_rotate(red=True)
            case WizAction.red_jump:
                self.apply_jump(red=True)
            case WizAction.red_power:
                self.call_power(red=True)
            case WizAction.red_fn1_call:
                self.apply_function_1(red=True)
            case WizAction.red_fn2_call:
                self.apply_function_2(red=True)
            case WizAction.red_halt:
                self.apply_halt(red=True)
            case WizAction.yellow_walk:
                self.apply_walk(yellow=True)
            case WizAction.yellow_rotate_left:
                self.apply_left_rotate(yellow=True)
            case WizAction.yellow_rotate_right:
                self.apply_right_rotate(yellow=True)
            case WizAction.yellow_jump:
                self.apply_jump(yellow=True)
            case WizAction.yellow_power:
                self.call_power(yellow=True)
            case WizAction.yellow_fn1_call:
                self.apply_function_1(yellow=True)
            case WizAction.yellow_fn2_call:
                self.apply_function_2(yellow=True)
            case WizAction.yellow_halt:
                self.apply_halt(yellow=True)
            case _:
                raise NotImplemented("Uh oh.")

        self.history.append(Summary(
            matrix_map=self.matrix.map,
            wizard=self.wizard,
            action=wiz_action,
            activated=self.activated,
            blue_activated=self.blue_activated,
            red_activated=self.red_activated,
            yellow_activated=self.red_activated))
        
    @print_debugger
    def level_complete(self):
        if len(self.activated) == 0:
            return False
        disks_activated = len(self.activated)
        disks = []
        for idx_y, y in enumerate(self.matrix.map):
            for idx_x, x in enumerate(y):
                if x == Terrain.Disk:
                    disks.append((idx_x, idx_y))
                if x == Terrain.Cliff_1_Disk:
                    disks.append((idx_x, idx_y))
                if x == Terrain.Cliff_2_Disk:
                    disks.append((idx_x, idx_y))
                if x == Terrain.Cliff_3_Disk:
                    disks.append((idx_x, idx_y))
        if len(disks) == disks_activated:
            return True
        return False

    @print_debugger
    def call_power(self, blue=False, red=False, yellow=False):
        terrain: Terrain = self.matrix.get((self.wizard.x, self.wizard.y))
        xy = (self.wizard.x, self.wizard.y)
        x, y = xy
        match terrain:
            case ( Terrain.BlueDisk | Terrain.Cliff_1_BlueDisk | Terrain.Cliff_2_BlueDisk | Terrain.Cliff_3_BlueDisk ):        
                if not xy in set(self.blue_activated):
                    self.blue_activated.append(xy)
                else:
                    idx = self.blue_activated.index(xy)
                    del self.blue_activated[idx]
                    self.blue_activated = [pair for pair in self.blue_activated if pair is not None]
            
            case ( Terrain.RedDisk | Terrain.Cliff_1_RedDisk | Terrain.Cliff_2_RedDisk | Terrain.Cliff_3_RedDisk ):
                if not xy in set(self.red_activated):
                    self.red_activated.append(xy)
                else:
                    idx = self.red_activated.index(xy)
                    del self.red_activated[idx]
                    self.red_activated = [pair for pair in self.red_activated if pair is not None]
            
            case ( Terrain.YellowDisk | Terrain.Cliff_1_YellowDisk | Terrain.Cliff_2_YellowDisk | Terrain.Cliff_3_YellowDisk ):
                if not xy in set(self.yellow_activated):
                    self.yellow_activated.append(xy)
                else:
                    idx = self.red_activated.index(xy)
                    del self.yellow_activated[idx]
                    self.yellow_activated = [pair for pair in self.yellow_activated if pair is not None]
            
            case ( Terrain.Disk | Terrain.Cliff_1_Disk | Terrain.Cliff_2_Disk | Terrain.Cliff_3_Disk ):
                if not xy in set(self.activated):
                    self.activated.append(xy)
                else:
                    idx = self.activated.index(xy)
                    del self.activated[idx]
                    self.activated = [pair for pair in self.activated if pair is not None]
            
            case Terrain.Elevator_Down:
                self.matrix.map[x][y] = Terrain.Elevator_Up
            
            case Terrain.Elevator_Up:
                self.matrix.map[x][y] = Terrain.Elevator_Down
            
            case Terrain.Cliff_1_Elevator_Down:
                self.matrix.map[x][y] = Terrain.Cliff_1_Elevator_Up
            
            case Terrain.Cliff_1_Elevator_Up:
                self.matrix.map[x][y] = Terrain.Cliff_1_Elevator_Down
           
    @print_debugger
    def apply_right_rotate(self, blue=False, red=False, yellow=False):
        x, y, orientation = (self.wizard.x, self.wizard.y, self.wizard.orientation)
        match orientation:
            case WizOrient.north: 
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.east)
            case WizOrient.east:
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.south)
            case WizOrient.south: 
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.west)
            case WizOrient.west: 
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.north)
            case _:
                raise ValueError("This should be unreachable")

    @print_debugger
    def apply_left_rotate(self, blue=False, red=False, yellow=False):
        x, y, orientation = (self.wizard.x, self.wizard.y, self.wizard.orientation)
        match orientation:
            case WizOrient.north: 
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.west)
            case WizOrient.east:
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.north)
            case WizOrient.south: 
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.east)
            case WizOrient.west: 
                self.wizard = Wizard(x=x, y=y, orientation=WizOrient.south)
            case _:
                raise ValueError("This should be unreachable")

    @print_debugger
    def apply_halt(self, blue=False, red=False, yellow=False):
        # When `blue`, `red`, or `yellow` are `True`, must see
        # if the current activated disks permit this to be used
        is_legal_0 = lambda colors: True
        if not is_legal_0((blue, red, yellow)):
            return
        # Otherwise, assuming we are allowed to use this halt,
        # the state must inform either statically or with dynamic
        # dispatch
        raise Interrupt(f"blue={blue}|red={red}|yellow={yellow}")

    @print_debugger
    def apply_function_1(self, blue=False, red=False, yellow=False):
        is_legal_1 = lambda colors: True
        if not is_legal_1((blue, red, yellow)):
            return 
        raise Function1(f"blue={blue}|red={red}|yellow={yellow}")

    @print_debugger
    def apply_function_2(self, blue=False, red=False, yellow=False):
        is_legal_2 = lambda colors: True
        if not is_legal_2((blue, red, yellow)):
            return 
        raise Function2(f"blue={blue}|red={red}|yellow={yellow}")

    @print_debugger
    def apply_walk(self, blue=False, red=False, yellow=False):
        x, y, orientation = (self.wizard.x, self.wizard.y, self.wizard.orientation)
        match orientation:
            case WizOrient.north:
                new_coords = (x + WizOrient.north.value[0], y + WizOrient.north.value[1])
                new_x, new_y = new_coords
                if not self.walk_possible((x, y), new_coords):
                    return
                new_x = State.trunc(new_x)
                new_y = State.trunc(new_y)
                self.wizard = Wizard(x=new_x, y=new_y, orientation=WizOrient.north)

            case WizOrient.east:
                new_coords = (x + WizOrient.east.value[0], y + WizOrient.east.value[1])
                new_x, new_y = new_coords
                if not self.walk_possible((x, y), new_coords):
                    return
                new_x = State.trunc(new_x)
                new_y = State.trunc(new_y)
                self.wizard = Wizard(x=new_x, y=new_y, orientation=WizOrient.east)
            
            case WizOrient.south:
                new_coords = (x + WizOrient.south.value[0], y + WizOrient.south.value[1])
                new_x, new_y = new_coords
                if not self.walk_possible((x, y), new_coords):
                    return
                self.wizard = Wizard(x=new_x, y=new_y, orientation=WizOrient.south)
            
            case WizOrient.west:
                new_coords = (x + WizOrient.west.value[0], y + WizOrient.west.value[1])
                new_x, new_y = new_coords
                if not self.walk_possible((x, y), new_coords):
                    return
                new_x = State.trunc(new_x)
                new_y = State.trunc(new_y)
                self.wizard = Wizard(x=new_x, y=new_y, orientation=WizOrient.east)
            case _:
                raise ValueError("This should be unreachable")
        return 

    @print_debugger
    def walk_possible(self, init_coord, final_coord):
        if not self.coordinate_exists(final_coord):
            return False
        if any([self.jump_up_possible(init_coord, final_coord),
                self.jump_down_possible(init_coord, final_coord)]):
            return False
        if not self.same_elevation(init_coord, final_coord):
            return False
        return True         

    @print_debugger
    def coordinate_exists(self, coordinate_pair):
        x, y = coordinate_pair
        result = True
        try:
            _ = self.matrix.map[x][y]
        except:
            result = False
        finally:
            return result

    @print_debugger
    def same_elevation(self, init_coord, final_coord):
        if not all([self.coordinate_exists(init_coord),
                    self.coordinate_exists(final_coord)]):
            return False
        x0, y0 = init_coord
        x1, y1 = final_coord
        start: Terrain = self.matrix.map[x0][y0]
        end:   Terrain = self.matrix.map[x1][y1]

        h0 = set([
            Terrain.Normal,
            Terrain.BlueDisk,
            Terrain.Disk,
            Terrain.RedDisk,
            Terrain.YellowDisk,
            Terrain.Elevator_Down,
        ])
        h1 = set([
            Terrain.Cliff_1,
            Terrain.Cliff_1_BlueDisk,
            Terrain.Cliff_1_Disk,
            Terrain.Cliff_1_RedDisk,
            Terrain.Cliff_1_YellowDisk,
            Terrain.Cliff_1_Elevator_Down,
        ])
        h2 = set([
            Terrain.Cliff_2,
            Terrain.Cliff_2_BlueDisk,
            Terrain.Cliff_2_Disk,
            Terrain.Cliff_2_RedDisk,
            Terrain.Cliff_2_YellowDisk,
            Terrain.Elevator_Up,
            Terrain.Cliff_2_Elevator_Down,
        ])
        h3 = set([
            Terrain.Cliff_3,
            Terrain.Cliff_3_BlueDisk,
            Terrain.Cliff_3_Disk,
            Terrain.Cliff_3_RedDisk,
            Terrain.Cliff_3_YellowDisk,
            Terrain.Cliff_1_Elevator_Up,
        ])
        elev_0 = start in h0 and end in h0
        elev_1 = start in h1 and end in h1
        elev_2 = start in h2 and end in h2
        elev_3 = start in h3 and end in h3

        if any([elev_0,
                elev_1,
                elev_2,
                elev_3]):
            return True
        return False

    @print_debugger
    def is_power_disk(self, coord):
        pdisk = {
            Terrain.Disk,
            Terrain.BlueDisk,
            Terrain.RedDisk,
            Terrain.YellowDisk,
            Terrain.Cliff_1_Disk,
            Terrain.Cliff_1_BlueDisk,
            Terrain.Cliff_1_RedDisk,
            Terrain.Cliff_1_YellowDisk,
            Terrain.Cliff_2_Disk,
            Terrain.Cliff_2_BlueDisk,
            Terrain.Cliff_2_RedDisk,
            Terrain.Cliff_2_YellowDisk,
            Terrain.Cliff_3_Disk,
            Terrain.Cliff_3_BlueDisk,
            Terrain.Cliff_3_RedDisk,
            Terrain.Cliff_3_YellowDisk
        }
        coord_is_disk = self.matrix.get(coord) in pdisk
        return coord_is_disk

    @print_debugger
    def jump_up_possible(self, init_coord, final_coord):
        x0, y0 = init_coord
        x1, y1 = final_coord
        initial_exists = self.coordinate_exists((x0, y0))
        final_exists = self.coordinate_exists((x1, y1))
        if not final_exists and initial_exists:
            return False
        start: Terrain  = self.matrix.map[x0][y0]
        end: Terrain = self.matrix.map[x1][y1]
        match (start, end):
            case (Terrain.Normal | Terrain.BlueDisk | Terrain.Disk | Terrain.RedDisk | Terrain.YellowDisk , Terrain.Cliff_1 | Terrain.Cliff_1_BlueDisk | Terrain.Cliff_1_RedDisk | Terrain.Cliff_1_YellowDisk | Terrain.Cliff_1_Elevator_Down):
                return True
            case (Terrain.Cliff_1 | Terrain.Cliff_1_BlueDisk | Terrain.Cliff_1_Disk | Terrain.Cliff_1_RedDisk | Terrain.Cliff_1_YellowDisk , Terrain.Cliff_2 | Terrain.Cliff_2_BlueDisk | Terrain.Cliff_2_RedDisk | Terrain.Cliff_2_YellowDisk | Terrain.Cliff_2_Elevator_Down):
                return True
            case (Terrain.Cliff_2 | Terrain.Cliff_2_BlueDisk | Terrain.Cliff_2_Disk | Terrain.Cliff_2_RedDisk | Terrain.Cliff_2_YellowDisk , Terrain.Cliff_3 | Terrain.Cliff_3_BlueDisk | Terrain.Cliff_3_RedDisk | Terrain.Cliff_2_YellowDisk):
                return True
            case (_, _):
                return False

    @print_debugger
    def jump_down_possible(self, init_coord, final_coord):
        x0, y0 = init_coord
        x1, y1 = final_coord
        initial_exists = self.coordinate_exists((x0, y0))
        final_exists = self.coordinate_exists((x1, y1))
        if not final_exists and initial_exists:
            return False
        start: Terrain  = self.matrix.map[x0][y0]
        end: Terrain = self.matrix.map[x1][y1]
        match (end, start):
            case (Terrain.Normal | Terrain.BlueDisk | Terrain.Disk | Terrain.RedDisk | Terrain.YellowDisk , Terrain.Cliff_1 | Terrain.Cliff_1_BlueDisk | Terrain.Cliff_1_RedDisk | Terrain.Cliff_1_YellowDisk | Terrain.Cliff_1_Elevator_Down):
                return True
            case (Terrain.Cliff_1 | Terrain.Cliff_1_BlueDisk | Terrain.Cliff_1_Disk | Terrain.Cliff_1_RedDisk | Terrain.Cliff_1_YellowDisk , Terrain.Cliff_2 | Terrain.Cliff_2_BlueDisk | Terrain.Cliff_2_RedDisk | Terrain.Cliff_2_YellowDisk | Terrain.Cliff_2_Elevator_Down):
                return True
            case (Terrain.Cliff_2 | Terrain.Cliff_2_BlueDisk | Terrain.Cliff_2_Disk | Terrain.Cliff_2_RedDisk | Terrain.Cliff_2_YellowDisk , Terrain.Cliff_3 | Terrain.Cliff_3_BlueDisk | Terrain.Cliff_3_RedDisk | Terrain.Cliff_2_YellowDisk):
                return True
            case (_, _):
                return False
            
