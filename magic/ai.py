from magic.elements import *
from magic.utils import *
from magic.state import *
from enum import Enum, auto
from functools import partial
from typing import *
import secrets # Needed for __hash__'ing things
import random

class ThreadScope(Enum):
    main = auto()
    fn1  = auto()
    fn2  = auto()

class Problem:
    @print_debugger
    def __init__(self, game_state: State, player_actions: List[Tuple[ThreadScope, WizAction]] = []):
        self.game_state = game_state
        self.player_actions = player_actions
        for (scope_kind, wiz_action) in player_actions:
            match scope_kind:
                case ThreadScope.main:
                    self.game_state.program.main.append(wiz_action)
                case ThreadScope.fn1:
                    self.game_state.program.fn1.append(wiz_action)
                case ThreadScope.fn2:
                    self.game_state.program.fn2.append(wiz_action)
        
        # This is undesirable since it limits
        # any sort of semantically equivalence checking.
        # ToDo: Find a better way
        self._hash = secrets.token_bytes(32)

    @print_debugger
    def main_capacity_full(self):
        return not len(self.game_state.program.main.actions) < self.game_state.program.main._max_size

    @print_debugger
    def fn1_capacity_full(self):
        return not len(self.game_state.program.fn1.actions) < self.game_state.program.fn1._max_size
    
    @print_debugger
    def fn2_capacity_full(self):
        return not len(self.game_state.program.fn2.actions) < self.game_state.program.fn2._max_size

    @print_debugger
    def main_empty(self):
        return not self.game_state.program.main.actions

    @print_debugger
    def fn1_empty(self):
        return not self.game_state.program.fn1.actions
    
    @print_debugger
    def fn2_empty(self):
        return not self.game_state.program.fn2.actions

    @print_debugger
    def actions(self):
        actions = []
        if not self.main_capacity_full():
            for wiz_action in list(filter(lambda wa: wa !=WizAction.none, WizAction)):
                actions.append((ThreadScope.main, wiz_action))
        if not self.fn1_capacity_full():
            for wiz_action in WizAction:
                actions.append((ThreadScope.fn1, wiz_action))
        if not self.fn2_capacity_full():
            for wiz_action in WizAction:
                actions.append((ThreadScope.fn2, wiz_action))
        return actions        

    @print_debugger
    def result(self, player_action):
        thread_scope, wiz_action = player_action
        main, main_max_size = self.game_state.program.main.actions, self.game_state.program.main._max_size
        fn1, fn1_max_size = self.game_state.program.fn1.actions, self.game_state.program.fn1._max_size
        fn2, fn2_max_size = self.game_state.program.fn2.actions, self.game_state.program.fn2._max_size
        match thread_scope:
            case ThreadScope.main:
                main.append(wiz_action)
            case ThreadScope.fn1:
                fn1.append(wiz_action)
            case ThreadScope.fn2:
                fn2.append(wiz_action)
        new_program = Program(
                Thread.main(main, available_slots=main_max_size),
                Thread.function_1(fn1,  available_slots=fn1_max_size),
                Thread.function_2(fn2,  available_slots=fn2_max_size),
                self.game_state.program.matrix,
                self.game_state.program.wizard,
        )
        new_program.collect()
        new_state = State(new_program)
        for entry in new_state.program.instructions:
            new_state.apply_action(entry)
        return Problem(game_state=new_state, player_actions=self.player_actions + [player_action])
        
    @print_debugger
    def goal_test(self):
        return self.game_state.level_complete()

    @print_debugger
    def unable_to_continue(self):
        return not self.actions()
    


class ProblemSolver:

    @print_debugger
    def __init__(self):
        self.problems = deque([])
        self.dead_problems = tuple()
    
    @print_debugger
    def solve(self, *problems) -> List[Tuple[ThreadScope, WizAction]]:
        print(*problems)
        for problem in problems:
            self.problems.append(problem)
        while 1: 
            problem = self.problems.pop() #frontier.pop()
            possible_actions = problem.actions()
            player_actions = []
            for player_action in possible_actions:
                resulting_problem = problem.result(player_action)
            if problem.goal_test():
                print("Success!")
                return problem.player_actions
            if problem in self.dead_problems:
                next_problem: Problem = self.problems.pop()
                return self.solve(next_problem)               
                new_problem: Problem = self.mutate_problem(problem)
                self.problems.append(new_problem)
                next_problem: Problem = self.get_next_problem()
                return self.solve(next_problem)
            if problem.unable_to_continue:
                self.dead_problems += (problem,)
                continue # ironic?
            self.problems.append(problem)
                          
    @classmethod
    def build(cls, initial_problem):
        ps = cls()
        ps.problems.append(initial_problem)
        return ps
    @print_debugger
    def mutate_problem(self, problem) -> Problem:
        # Just before death, we offer redemption
        # mutate yourself for a second chance.
        # Change any `Tuple[ThreadScope, WizAction]`
        # in the `problem.player_actions` to something
        # different and re-add it to `self.problems`
        @print_debugger
        def space_available_in_main():
            return not problem.main_capacity_full()

        @print_debugger
        def space_available_in_fn1():
            return not problem.fn1_capacity_full()
       
        @print_debugger
        def space_available_in_fn2():
            return not problem.fn2_capacity_full()

        class Mutation(Enum):
            delete_at_main = auto()
            delete_at_fn1  = auto()
            delete_at_fn2  = auto()
            insert_at_main = auto()
            insert_at_fn1  = auto()
            insert_at_fn2  = auto()
            mutate_at_main = auto()
            mutate_at_fn1  = auto()
            mutate_at_fn2  = auto()

        @print_debugger
        def delete(at: int, scope_kind: ThreadScope) -> List[Tuple[ThreadScope, WizAction]]:
            slot = {
                "main": -1,
                "fn1":  -1,
                "fn2":  -1,
            }
            # Explicit opt-in for a shallow copy
            player_actions = [_ for _ in problem.player_actions]
            
            for (idx, (thread, _wiz_action)) in enumerate(player_actions):
                # Opting for lower cognitive load and simpler statements
                # at the expense of runtime performance. 
                match thread:
                    case ThreadScope.main:
                        slot["main"] += 1
                    case ThreadScope.fn1:
                        slot["fn1"] += 1
                    case ThreadScope.fn2:
                        slot["fn2"] += 1
                # Not sure if `del some_list[index]` still leaves a `None` behind,
                # or if it resizes the list, but filtering out potential residue just in case
                match thread:
                    case ThreadScope.main:
                        if not slot["main"] == at:
                            continue
                        del player_actions[idx]
                        player_actions = list(filter(None, player_actions))
                    case ThreadScope.fn1:
                        if not slot["fn1"] == at:
                            continue
                        del player_actions[idx]
                        player_actions = list(filter(None, player_actions))
                    case ThreadScope.fn2:
                        if not slot["fn2"] == at:
                            continue
                        del player_actions[idx]
                        player_actions = list(filter(None, player_actions))
            return player_actions
        @print_debugger
        def insert(at: int, 
                   scope_kind: ThreadScope, 
                   wiz_action: WizAction) -> List[Tuple[ThreadScope, WizAction]]:
            slot = {
                "main": -1,
                "fn1":  -1,
                "fn2":  -1,
            }
            
            buffer = []
            
            for (idx, (thread, _wiz_action)) in enumerate(problem.player_actions):
                match thread:
                    case ThreadScope.main:
                        slot["main"] += 1
                    case ThreadScope.fn1:
                        slot["fn1"] += 1
                    case ThreadScope.fn2:
                        slot["fn2"] += 1

                match thread:
                    case ThreadScope.main:
                        if not slot["main"] == at:
                            buffer.append((thread, _wiz_action))
                            continue
                        buffer.append((thread, wiz_action))        
                    case ThreadScope.fn1:
                        if not slot["fn1"] == at:
                            buffer.append((thread, _wiz_action))
                            continue
                        buffer.append((thread, wiz_action))
                    case ThreadScope.fn2:
                        if not slot["fn2"] == at:
                            buffer.append((thread, _wiz_action))
                            continue
                        buffer.append((thread, wiz_action))
            return buffer

        @print_debugger
        def mutate(at: int, scope_kind: ThreadScope, wiz_action: WizAction) -> List[Tuple[ThreadScope, WizAction]]:
            slot = {
                "main": -1,
                "fn1":  -1,
                "fn2":  -1,
            }
            
            @print_debugger
            def point_mut(wa):
                """converts deleted `None` values into
                the desired `wiz_action` mutation
                """
                if not wa:
                    return (scope_kind, wiz_action)
                return (scope_kind, wa)

            player_actions = [_ for _ in problem.player_actions]
            
            for (idx, (thread, _wiz_action)) in enumerate(player_actions):
                match thread:
                    case ThreadScope.main:
                        slot["main"] += 1
                    case ThreadScope.fn1:
                        slot["fn1"] += 1
                    case ThreadScope.fn2:
                        slot["fn2"] += 1
                
                match thread:
                    case ThreadScope.main:
                        if not slot["main"] == at:
                            continue
                        del player_actions[idx]
                        player_actions = list(map(point_mut, player_actions))
                        break
                    case ThreadScope.fn1:
                        if not slot["fn1"] == at:
                            continue
                        del player_actions[idx]
                        player_actions = list(map(point_mut, player_actions))
                        break
                    case ThreadScope.fn2:
                        if not slot["fn2"] == at:
                            continue
                        del player_actions[idx]
                        player_actions = list(map(point_mut, player_actions))
                        break
            return player_actions

        @print_debugger
        def mutation_policy():
            constraints = ()
            options_main = [(ThreadScope.main, wa) for wa in list(filter(lambda wa: wa != WizAction.none, WizAction))]
            options_fn1  = [(ThreadScope.fn1, wa)  for wa in list(filter(lambda wa: wa != WizAction.none, WizAction))]
            options_fn2  = [(ThreadScope.fn2, wa)  for wa in list(filter(lambda wa: wa != WizAction.none, WizAction))]
            if not space_available_in_main():
                constraints += (Mutation.insert_at_main,)
            if not space_available_in_fn1():
                constraints += (Mutation.insert_at_fn1,)
            if not space_available_in_fn2():
                constraints += (Mutation.insert_at_fn2,)
            if problem.main_empty():
                constraints += (Mutation.delete_at_main, Mutation.mutate_at_main)
            if problem.fn1_empty():
                constraints += (Mutation.delete_at_fn1, Mutation.mutate_at_fn1)
            if problem.fn2_empty():
                constraints += (Mutation.delete_at_fn2, Mutation.mutate_at_fn2)
            
            while 1:
                mut = random.choice(list(Mutation))
                
                if mut in constraints:
                    continue
                
                # The subtlety here is that this must copy `problem.player_actions`,
                # not `problem.game_state`. From there `problem` needs to reconstruct
                # its `self.game_state` using the second-order instructions.
                # 
                # The reasoning here is that we're not modifying the game state
                # at all, but rather modifying the player's behaviors which macro-expand
                # to `problem.game_state.program.instructions`
                match mut:
                    case Mutation.delete_at_main:
                        try:
                            at = random.randint(0, problem.game_state.program.main._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = delete(index=at, scope_kind=ThreadScope.main)
                            return player_actions
                        except:
                            continue
                    case Mutation.delete_at_fn1:
                        try:
                            at = random.randint(0, problem.game_state.program.fn1._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = delete(index=at, scope_kind=ThreadScope.fn1)
                            return player_actions
                        except:
                            continue
                    case Mutation.delete_at_fn2:
                        try:
                            at = random.randint(0, problem.game_state.program.fn2._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = delete(index=at, scope_kind=ThreadScope.fn2)
                            return player_actions
                        except:
                            continue
                    case Mutation.insert_at_main:
                        try:
                            at = random.randint(0, problem.game_state.program.main._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = insert(index=at, scope_kind=ThreadScope.main)
                            return player_actions
                        except:
                            continue
                    case Mutation.insert_at_fn1:
                        try:
                            at = random.randint(0, problem.game_state.program.fn1._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = insert(index=at, scope_kind=ThreadScope.fn1)
                            return player_actions
                        except:
                            continue
                    case Mutation.insert_at_fn2:
                        try:
                            at = random.randint(0, problem.game_state.program.fn2._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = insert(index=at, scope_kind=ThreadScope.fn2)
                            return player_actions
                        except:
                            continue
                    case Mutation.mutate_at_main:
                        try:
                            at = random.randint(0, problem.game_state.program.main._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = mutate(index=at, scope_kind=ThreadScope.main)
                            return player_actions
                        except:
                            continue
                    case Mutation.mutate_at_fn1:
                        try:
                            at = random.randint(0, problem.game_state.program.fn1._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = mutate(index=at, scope_kind=ThreadScope.fn1)
                            return player_actions 
                        except:
                            continue
                    case Mutation.mutate_at_fn2:
                        try:
                            at = random.randint(0, problem.game_state.program.fn2._max_size)
                            player_actions: List[Tuple[ThreadScope, WizAction]] = mutate(index=at, scope_kind=ThreadScope.fn2)
                            return player_actions 
                        except:
                            continue
                    case _:
                        raise ValueError("This should be unreachable")
        matrix     = problem.game_state.history[0].matrix_map
        main       = problem.game_state.program.main
        function_1 = problem.game_state.program.fn1
        function_2 = problem.game_state.program.fn2
        wizard     = problem.game_state.history[0].wizard

        new_program = Program(main=main, 
                              fn1=function_1,
                              fn2=function_2, 
                              matrix=matrix, 
                              wizard=wizard)
        
        game_state  = State(new_program)
        player_actions = mutation_policy()
        new_problem = Problem(game_state=game_state, player_actions=player_actions)
        new_problem.game_state.collect()
        return new_problem

    @print_debugger
    def get_next_problem(self):
        return self.problems.pop()

    @print_debugger
    def derive_frontier(self, problem):
        frontier = []
        for action in problem.actions():
            new_problem = problem.result(action)
            frontier.append(new_problem)
        return frontier
