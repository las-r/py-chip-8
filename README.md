# pychip8
A modular, extensible CHIP-8 emulator ecosystem written in modern Python, with support for SUPER-CHIP (and soon XO-CHIP).

> **Note:** This is a remake of an old project of mine, [chip-8-python](https://github.com/las-r/chip-8-python), which aimed to do the same thing but was honestly pretty poorly made. It was monolithic and clunky, and this one is built to be an actual Python package.

## Installation
Requires Python 3.11+.

```sh
pip install chip8-py

# or in a local directory
git clone https://github.com/las-r/pychip8
cd pychip8
pip install -e .
```

## Usage
```sh
pychip8 path/to/rom.ch8
```

## Config
### File
On first run, a default config is created at:
- **Windows:** `C:/Users/YOUR_USER_PROFILE/AppData/Local/pychip8/`
- **macOS:** `~/Library/Application Support/pychip8/`
- **Linux:** `~/.config/pychip8/`

Edit this file to set your preferred defaults.

### Flags
Flags override the config file.

| Flag | Description |
|---|---|
| `--cpf <int>` | Cycles per frame (default: 10) |
| `--scale <int>` | Display scale (default: 12) |
| `--volume <float>` | Audio volume 0.0–1.0 (default: 0.2) |
| `--cosmac-shift / --no-cosmac-shift` | COSMAC VIP shift quirk |
| `--cosmac-jump / --no-cosmac-jump` | COSMAC VIP jump quirk |
| `--cosmac-i-add / --no-cosmac-i-add` | COSMAC VIP index add quirk |
| `--cosmac-font / --no-cosmac-font` | COSMAC VIP font quirk |
| `--cosmac-ls / --no-cosmac-ls` | COSMAC VIP load/store quirk |
| `--vf-reset / --no-vf-reset` | Reset VF after logic instructions |
| `--spr-clip / --no-spr-clip` | Clip sprites at screen edges instead of wrapping |
| `--schip-scroll / --no-schip-scroll` | Halve scroll distance in low-res mode |
| `--schip-hires-spr / --no-schip-hires-spr` | Restrict 16×16 sprites to high-res mode only |
| `--schip-vblank / --no-schip-vblank` | Wait for vblank before drawing |
| `--bg <hex>` | Background color |
| `--fg <hex>` | Foreground color |

## Keypad
The CHIP-8 hex keypad maps to the left side of a QWERTY keyboard:
```
CHIP-8    Keyboard
1 2 3 C   1 2 3 4
4 5 6 D   Q W E R
7 8 9 E   A S D F
A 0 B F   Z X C V
```

## Credits
- [raylib](https://www.raylib.com/) ([Python](https://github.com/electronstudio/raylib-python-cffi/))
- [Guide to making a CHIP-8 emulator](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/)
- [Timendus' CHIP-8 Test Suite](https://github.com/Timendus/chip8-test-suite)
- [SUPER-CHIP v1.1 Documentation](http://devernay.free.fr/hacks/chip8/schip.txt)
- [Mastering SuperChip](https://johnearnest.github.io/Octo/docs/SuperChip.html)