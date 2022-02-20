#import pudb; pu.db
#from game.csp import *
from magic.elements import (
    Wizard,
    WizAction, 
    WizOrient,
    Terrain,
    Thread,
    Program,
    Matrix)
from magic.state import State
from magic.ai import Problem, ProblemSolver

matrix = (
    Matrix.from_dimensions(4, 1)
    .put((0,0), Terrain.Normal)
    .put((1,0), Terrain.Normal)
    .put((2,0), Terrain.Normal)
    .put((3,0), Terrain.Disk)
)

wizard = Wizard(x=0, y=0, orientation=WizOrient.east)

main_thread = Thread.main(
    actions=[],
    available_slots=12)

function_1 = Thread.function_1(
    actions=[],
    available_slots=0)

function_2 = Thread.function_2(
    actions=[],
    available_slots=0)
'''
main_thread.actions.extend([
        #WizAction.rotate_right,
        WizAction.fn1_call,
        WizAction.fn1_call,
        WizAction.fn1_call,
        WizAction.power
])
'''
'''
function_1.actions.extend([
        WizAction.walk,
        #WizAction.rotate_right
])
'''
'''
function_2.actions.extend([
        WizAction.walk
])
'''
exe = Program(main_thread, function_1, function_2, matrix, wizard)
exe.collect()
game_state = State(exe)
problem = Problem(game_state=game_state)
solver = ProblemSolver.build(initial_problem=problem)
res = solver.solve(problem)
for thing in problem.game_state.history:
    print(thing)
'''
for entry in game_state.program.instructions:
    #print(entry)
    game_state.apply_action(entry)
    print(game_state.history[-1])
    if game_state.level_complete():
        print("Success! Level complete")
print("Failure..")
'''
