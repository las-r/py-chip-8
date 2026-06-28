import pyray as rl
import numpy as np

# chip8py keypad
# by las-r

# chip8 key map
KEYMAP = {
    rl.KeyboardKey.KEY_ONE: 1, rl.KeyboardKey.KEY_TWO: 2, rl.KeyboardKey.KEY_THREE: 3, rl.KeyboardKey.KEY_FOUR: 12,
    rl.KeyboardKey.KEY_Q: 4, rl.KeyboardKey.KEY_W: 5, rl.KeyboardKey.KEY_E: 6, rl.KeyboardKey.KEY_R: 13,
    rl.KeyboardKey.KEY_A: 7, rl.KeyboardKey.KEY_S: 8, rl.KeyboardKey.KEY_D: 9, rl.KeyboardKey.KEY_F: 14,
    rl.KeyboardKey.KEY_Z: 10, rl.KeyboardKey.KEY_X: 0, rl.KeyboardKey.KEY_C: 11, rl.KeyboardKey.KEY_V: 15,
}

# keypad class
class Keypad:
    def __init__(self):
        self.keys = np.zeros(16, dtype=np.uint8)

    def update(self):
        for raykey, chip8key in KEYMAP.items():
            self.keys[chip8key] = 1 if rl.is_key_down(raykey) else 0

    def is_pressed(self, key) -> bool:
        return self.keys[int(key)] == 1