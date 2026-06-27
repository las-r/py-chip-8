import numpy as np
import pyray as rl
import math

class Timers:
    def __init__(self, vol: float = 0.05):
        self.delay = np.uint8(0)
        self.sound = np.uint8(0)
        self.playing = False
        
        rl.init_audio_device()
        smprate = 44100
        smps = int(smprate * 0.5)
        freq = 600
        raw = []
        for i in range(smps):
            t = i / smprate
            sample = math.sin(2 * math.pi * freq * t)
            raw.append(sample)
        self.data_buffer = rl.ffi.new(f"float[{smps}]", raw)
        rl.set_audio_stream_buffer_size_default(smps)
        self.stream = rl.load_audio_stream(smprate, 32, 1)
        rl.update_audio_stream(self.stream, self.data_buffer, smps)
        rl.set_audio_stream_volume(self.stream, vol)
        
    def set_delay(self, val):
        self.delay = np.uint8(int(val))
        
    def set_sound(self, val):
        self.sound = np.uint8(int(val))

    def update(self):
        if self.delay > 0:
            self.delay -= 1
        if self.sound > 0:
            self.sound -= 1
            self.play_beep()
        else:
            self.stop_beep()

    def play_beep(self):
        if not self.playing:
            rl.play_audio_stream(self.stream)
            self.playing = True
        if rl.is_audio_stream_processed(self.stream):
            rl.update_audio_stream(self.stream, self.data_buffer, len(self.data_buffer))

    def stop_beep(self):
        if self.playing:
            rl.stop_audio_stream(self.stream)
            self.playing = False
    
    def deinit(self):
        rl.unload_audio_stream(self.stream)
        rl.close_audio_device()