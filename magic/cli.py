import sys
import argparse
from magic.app import dispatch

parser = argparse.ArgumentParser(
    prog="magiccode",
    usage="Magic Code level solver! ",
    description="""CLI with a reverse engineered "Magic Code" game backend, \
                   for the intention of building solutions to its toughest leve\
                   ls. """
)
parser.add_argument(
    "-q",
    "--quiet",
    default=0,
    dest="quiet",
    type=int,
    help="Suppress verbose output"
)
parser.add_argument(
    "-t",
    "--template",
    default=my_magic_code_level.py,
    dest="template_target"
)
parser.add_argument(
    "-s",
    "--solve",
    default=my_magic_code_level.py,
    dest="solve_target"
)

args = parser.parse_args()
 

def main():
    global args
    return dispatch(args)

if __name__ == '__main__':
    main()
