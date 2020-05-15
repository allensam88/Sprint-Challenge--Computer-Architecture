import sys
from cpu import *

if len(sys.argv) == 2:
    program_filename = sys.argv[1]
else:
    print('Invalid entry --> please enter the program name.')
    exit()

cpu = CPU()

cpu.load(program_filename)
cpu.run()
