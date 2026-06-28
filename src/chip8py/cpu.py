from .display import Display
from .keypad import Keypad
from .memory import Memory
from .timers import Timers
import numpy as np
import random

# chip8py cpu
# by las-r

# exit exception
class InterpreterExit(Exception):
    pass

# processor class
class Processor:
    def __init__(self, ram: Memory, disp: Display, kp: Keypad, tm: Timers, cpf: int = 10):
        self.ram = ram
        self.disp = disp
        self.kp = kp
        self.tm = tm
        self.cpf = cpf
        
        # quirk options
        self.cosmac_shift = False # put the value of vy into vx before shifting vx; def: False
        self.cosmac_jump = False # jump to instruction at nn plus v0 instead of xnn plus vx; def: False
        self.cosmac_i_add = False # fx1e does not affect vf upon going above 4096; def: False
        self.cosmac_font = True # fx29 only takes the last nibble of vx; def: True
        self.cosmac_ls = False # increments i as fx55/fx65 work; def: False
        self.vf_reset = True # bitwise operation reset vf to 0; def: True
        self.spr_clip = False # sprites dont wrap around; def: False
        self.schip_scroll = False  # scroll down n/2 rows in lores; def: False
        self.schip_hires_spr = True  # dxy0 draws 16x16 in hires only; def: True
        self.schip_vblank = False  # wait for vblank before drawing; def: False
        
        # data storage
        self.v = np.zeros(16, np.uint8)
        self.pc = np.uint16(0x200)
        self.i = np.uint16(0)
        self.stack = []
        self.rplf = np.zeros(16, dtype=np.uint8)
        
        # other
        self.pkeys = np.zeros(16, dtype=np.uint8)
        
    def fetch(self) -> np.uint16:
        high = self.ram[self.pc]
        low = self.ram[self.pc + 1]
        opc = (np.uint16(high) << 8) | np.uint16(low)
        self.pc += 2
        return opc
    
    def execute(self, inst):
        l = inst >> 12
        x = (inst >> 8) & 0xf
        y = (inst >> 4) & 0xf
        n = inst & 0xf
        nn = inst & 0xff
        nnn = inst & 0xfff
        
        match (l, x, y, n):
            # scroll screen down
            case (0, 0, 12, _):
                h, w = self.disp.grid.shape
                scroll = n // 2 if (self.schip_scroll and w == 64) else n
                if 0 < scroll < self.disp.grid.shape[0]:
                    ogrid = self.disp.grid.copy()
                    ngrid = np.zeros_like(ogrid)
                    ngrid[scroll:] = ogrid[:scroll]
                    self.disp.grid = ngrid
            
            # clear screen
            case (0, 0, 14, 0):
                self.disp.clear()
                
            # scroll right
            case (0, 0, 15, 11):
                ngrid = np.zeros_like(self.disp.grid)
                ngrid[:, 4:] = self.disp.grid[:, :-4]
                self.disp.grid = ngrid
                
            # scroll left
            case (0, 0, 15, 12):
                ngrid = np.zeros_like(self.disp.grid)
                ngrid[:, :-4] = self.disp.grid[:, 4:]
                self.disp.grid = ngrid
                
            # exit emulator
            case (0, 0, 15, 13):
                raise InterpreterExit

            # disable high res mode
            case (0, 0, 15, 14):
                _, ow = self.disp.grid.shape
                if ow != 64:
                    self.disp.scale *= 2
                self.disp.grid = np.zeros((32, 64), dtype=np.uint8)
            
            # enable high res mode
            case (0, 0, 15, 15):
                _, ow = self.disp.grid.shape
                if ow != 128:
                    self.disp.scale //= 2
                self.disp.grid = np.zeros((64, 128), dtype=np.uint8)
                
            # return from subroutine
            case (0, 0, 14, 14):
                self.pc = self.stack.pop()
                
            # jump to nnn
            case (1, _, _, _):
                self.pc = nnn
                
            # call subroutine
            case (2, _, _, _):
                self.stack.append(self.pc)
                self.pc = nnn
                
            # skip if vx == nn
            case (3, _, _, _):
                if self.v[x] == nn:
                    self.pc += 2
                    
            # skip if vx != nn
            case (4, _, _, _):
                if self.v[x] != nn:
                    self.pc += 2
                    
            # skip if vx == vy
            case (5, _, _, 0):
                if self.v[x] == self.v[y]:
                    self.pc += 2
                
            # set vx
            case (6, _, _, _):
                self.v[x] = nn
                
            # add to vx
            case (7, _, _, _):
                self.v[x] += nn
                
            # set vx to vy
            case (8, _, _, 0):
                self.v[x] = self.v[y]
                
            # set vx to vx OR vy
            case (8, _, _, 1):
                self.v[x] |= self.v[y]
                if self.vf_reset:
                    self.v[0xf] = 0
                
            # set vx to vx AND vy
            case (8, _, _, 2):
                self.v[x] &= self.v[y]
                if self.vf_reset:
                    self.v[0xf] = 0
            
            # set vx to vx XOR vy
            case (8, _, _, 3):
                self.v[x] ^= self.v[y]
                if self.vf_reset:
                    self.v[0xf] = 0
                
            # set vx to vx + vy
            case (8, _, _, 4):
                o = self.v[x]
                self.v[x] += self.v[y]
                self.v[0xf] = 1 if o > self.v[x] else 0
            
            # set vx to vx - vy
            case (8, _, _, 5):
                self.v[0xf] = 1 if self.v[x] >= self.v[y] else 0
                self.v[x] -= self.v[y]
                
            # right shift
            case (8, _, _, 6):
                if self.cosmac_shift:
                    self.v[x] = self.v[y]
                flag = self.v[x] & 0x1
                self.v[x] >>= 1
                self.v[0xf] = flag
                
            # set vx to vy - vx
            case (8, _, _, 7):
                self.v[0xf] = 1 if self.v[y] >= self.v[x] else 0
                self.v[x] = self.v[y] - self.v[x]
            
            # left shift
            case (8, _, _, 14):
                if self.cosmac_shift:
                    self.v[x] = self.v[y]
                flag = self.v[x] >> 7
                self.v[x] <<= 1
                self.v[0xf] = flag
                
            # skip if vx != vy
            case (9, _, _, 0):
                if self.v[x] != self.v[y]:
                    self.pc += 2
            
            # set index register
            case (10, _, _, _):
                self.i = nnn
                
            # jump w/ offset
            case (11, _, _, _):
                self.pc = nnn + self.v[0 if self.cosmac_jump else x]
                
            # set vx to random AND nn
            case (12, _, _, _):
                self.v[x] = np.uint8(random.randint(0, 255) & nn)
            
            # draw
            case (13, _, _, _):
                if self.schip_vblank and not self.disp.vblank:
                    self.pc -= 2
                    return
                h, w = self.disp.grid.shape
                is16x16 = n == 0 and (w == 128 if self.schip_hires_spr else True)
                srows = 16 if is16x16 else n
                scols = 16 if is16x16 else 8
                sx = self.v[x]
                sy = self.v[y]
                if not self.spr_clip:
                    sx %= w
                    sy %= h
                else:
                    if sx >= w or sy >= h:
                        self.v[0xf] = 0
                        return
                self.v[0xf] = 0
                bpr = 2 if scols == 16 else 1
                tbytes = srows * bpr
                sbytes = self.ram.mem[self.i : self.i + tbytes]
                sbits = np.unpackbits(sbytes).reshape(srows, bpr * 8)
                for ri in range(srows):
                    ty = sy + ri
                    if self.spr_clip:
                        if ty >= h: break
                    else:
                        ty %= h
                    for ci in range(scols):
                        tx = sx + ci
                        if self.spr_clip:
                            if tx >= w: continue
                        else:
                            tx %= w
                        pixel = sbits[ri, ci]
                        if pixel:
                            if self.disp.grid[ty, tx] == 1:
                                self.v[0xf] = 1
                            self.disp.grid[ty, tx] ^= 1
                            
            # skip if key vx pressed
            case (14, _, 9, 14):
                if self.kp.is_pressed(self.v[x]):
                    self.pc += 2
                    
            # skip if key vx not pressed
            case (14, _, 10, 1):
                if not self.kp.is_pressed(self.v[x]):
                    self.pc += 2
                    
            # set vx to delay timer
            case (15, _, 0, 7):
                self.v[x] = self.tm.delay
                
            # get key
            case (15, _, 0, 10):
                released = None
                for k in range(16):
                    if self.pkeys[k] == 1 and self.kp.keys[k] == 0:
                        released = k
                        break
                if released is not None:
                    self.v[x] = released
                else:
                    self.pc -= 2
                
            # set delay timer to vx
            case (15, _, 1, 5):
                self.tm.set_delay(self.v[x])
                
            # set sound timer to vx
            case (15, _, 1, 8):
                self.tm.set_sound(self.v[x])
            
            # add to index
            case (15, _, 1, 14):
                self.i += self.v[x]
                if not self.cosmac_i_add:
                    if self.i > 0xfff:
                        self.v[0xf] = 1
                        
            # set i to font character
            case (15, _, 2, 9):
                ch = (self.v[x] & 0xf) if self.cosmac_font else self.v[x]
                self.i = ch * 5
                
            # set i to large font character
            case(15, _, 3, 0):
                lch = self.v[x] & 0xf
                self.i = 0x50 + lch * 10
                
            # bcd
            case (15, _, 3, 3):
                self.ram[int(self.i)] = np.uint8(self.v[x] // 100)
                self.ram[int(self.i) + 1] = np.uint8((self.v[x] // 10) % 10)
                self.ram[int(self.i) + 2] = np.uint8(self.v[x] % 10)
                
            # store in memory
            case (15, _, 5, 5):
                for j in range(0, x + 1):
                    self.ram[int(self.i) + j] = self.v[j]
                if self.cosmac_ls:
                    self.i += x + 1
                    
            # load from memory
            case (15, _, 6, 5):
                for j in range(0, x + 1):
                    self.v[j] = self.ram[int(self.i) + j]
                if self.cosmac_ls:
                    self.i += x + 1
                    
            # store into rpl flags
            case (15, _, 7, 5):
                for idx in range(x + 1):
                    self.rplf[idx] = self.v[idx]

            # load from rpl flags
            case (15, _, 8, 5):
                for idx in range(x + 1):
                    self.v[idx] = self.rplf[idx]
                            
    def cycle(self):
        self.execute(self.fetch())