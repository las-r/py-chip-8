import numpy as np
import pyray as rl

# chip8py display
# by las-r

# display class
class Display:
    def __init__(self, scale: int = 12, fg: int = 0xFFFFFFFF, bg: int = 0x000000FF):
        self.scale = scale
        self.grid = np.zeros((32, 64), dtype=np.uint8)
        self.on = rl.get_color(fg)
        self.off = rl.get_color(bg)

        h, w = self.grid.shape
        rl.init_window(w * self.scale, h * self.scale, "pychip8")
        rl.set_target_fps(60)
        self.vblank = False

    def clear(self):
        self.grid.fill(0)

    def render(self):
        self.vblank = True
        rl.begin_drawing()
        rl.clear_background(self.off)

        h, w = self.grid.shape
        for y in range(h):
            for x in range(w):
                if self.grid[y, x] == 1:
                    rl.draw_rectangle(
                        x * self.scale,
                        y * self.scale,
                        self.scale,
                        self.scale,
                        self.on
                    )
                    
        rl.end_drawing()
        self.vblank = False

    def deinit(self):
        rl.close_window()