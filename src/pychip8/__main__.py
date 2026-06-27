from .cpu import Processor
from .display import Display
from .keypad import Keypad
from .memory import Memory
from .timers import Timers

from pathlib import Path
from platformdirs import user_config_dir
import argparse
import shutil
import tomllib
import pyray as rl

# setup and load config
CONFDIR = Path(user_config_dir("pychip8"))
CONFPATH = CONFDIR / "config.toml"
if not CONFPATH.exists():
    CONFDIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent / "config.toml", CONFPATH)
with open(CONFPATH, "rb") as f:
    cfg = tomllib.load(f)

# main
def main():
    # args
    parser = argparse.ArgumentParser(prog="pychip8", description="A CHIP-8 emulator.")
    parser.add_argument("rom", help="path to rom file")
    parser.add_argument("--cpf", type=int, help="cycles per frame")
    parser.add_argument("--scale", type=int, help="display scale")
    parser.add_argument("--volume", type=float, help="audio volume (0.0-1.0)")
    parser.add_argument("--cosmac-shift", action=argparse.BooleanOptionalAction)
    parser.add_argument("--cosmac-jump", action=argparse.BooleanOptionalAction)
    parser.add_argument("--cosmac-i-add", action=argparse.BooleanOptionalAction)
    parser.add_argument("--cosmac-font", action=argparse.BooleanOptionalAction)
    parser.add_argument("--cosmac-ls", action=argparse.BooleanOptionalAction)
    parser.add_argument("--vf-reset", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    # config helpers
    def gcpu(key, flag):
        return flag if flag is not None else cfg["cpu"][key]
    def gdisp(key, flag):
        return flag if flag is not None else cfg["display"][key]
    def gaud(key, flag):
        return flag if flag is not None else cfg["audio"][key]

    # load rom
    with open(args.rom, "rb") as f:
        rom = f.read()

    # init
    display = Display(scale=gdisp("scale", args.scale))
    keypad = Keypad()
    timers = Timers(vol=gaud("volume", args.volume))
    memory = Memory()
    memory.load_rom(rom)
    cpu = Processor(memory, display, keypad, timers, cpf=gcpu("cpf", args.cpf))

    # apply quirks
    cpu.cosmac_shift = gcpu("cosmac_shift", args.cosmac_shift)
    cpu.cosmac_jump = gcpu("cosmac_jump", args.cosmac_jump)
    cpu.cosmac_i_add = gcpu("cosmac_i_add", args.cosmac_i_add)
    cpu.cosmac_font = gcpu("cosmac_font", args.cosmac_font)
    cpu.cosmac_ls = gcpu("cosmac_ls", args.cosmac_ls)
    cpu.vf_reset = gcpu("vf_reset", args.vf_reset)

    # main loop
    while not rl.window_should_close():
        cpu.pkeys = cpu.kp.keys.copy()
        cpu.kp.update()
        for _ in range(cpu.cpf):
            cpu.cycle()
        cpu.tm.update()
        cpu.disp.render()

    # deinit
    cpu.disp.deinit()
    cpu.tm.deinit()

if __name__ == "__main__":
    main()