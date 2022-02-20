#import pudb; pu.db
#from game.csp import *
import sys
from magic.elements import (
    Wizard,
    WizAction, 
    WizOrient,
    Terrain,
    Thread,
    Program,
    Matrix)
from magic.state import State
matrix = (
    Matrix.from_dimensions(4, 3)
    .put((0,1), Terrain.Normal)
    .put((1,1), Terrain.Normal)
    .put((2,1), Terrain.Normal)
    .put((3,1), Terrain.Disk)
    .put((
    .put((1,2), Terrain.Disk)
)

wizard = Wizard(x=0, y=0, orientation=WizOrient.east)

main_thread = Thread.main(
    actions=[],
    available_slots=12)

function_1 = Thread.function_1(
    actions=[],
    available_slots=12)

function_2 = Thread.function_2(
    actions=[],
    available_slots=12)

main_thread.actions.extend([ 
    WizAction.walk,
    WizAction.rotate_left,
    WizAction.walk,
    WizAction.walk,
    WizAction.power
    ])

function_1.actions.extend([
])

function_2.actions.extend([
])

def init_game(main_thread, function_1, function_2, matrix, wizard):
    exe = Program(main_thread, function_1, function_2, matrix, wizard)
    exe.collect()
    game_state = State(exe)
    return game_state

def apply_action(game_state: State, entry):
    game_state.apply_action(entry)

def goal_test(game_state: State):
    return game_state.level_complete()

game = init_game(main_thread, function_1, function_2, matrix, wizard)

for entry in game.program.instructions:
    game.apply_action(entry)
    print(game.history[-1])
    if goal_test(game):
        print("Success")
        sys.exit(0)

print(game.history)
