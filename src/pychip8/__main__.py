from cpu import *
from display import *
from memory import *
from timers import *
import pyray as rl
import sys

# get rom bytes
romname = sys.argv[1]
with open(romname, "rb") as f:
    rom = f.read()
    
# init emulator
timers = Timers()
cpu = Processor(Memory(), Display())
cpu.ram.load_rom(rom)

# main loop
while not rl.window_should_close():
    for _ in range(cpu.cpf):
        cpu.cycle()
    cpu.disp.render()

# deinit
cpu.disp.deinit()
timers.deinit()