# Salt and Sanctuary — Control Preset Manager

> *"Yes, I am fully aware that you can just rebind your controls in the in-game settings menu. But where is the fun in that? Besides, I was way too lazy to click through every single keybind again after reinstalling the game... and playing a Souls-like with the default layout while your muscle memory actively fights against you is pure torture."*

A lightweight Python CLI & Drag-and-Drop utility for switching keyboard, mouse, and gamepad control schemes in **Salt and Sanctuary** using external `.json` preset files.

## Features

* **JSON-Based Presets:** Easily switch between layouts (e.g., Dark Souls-style controls, default bindings, or custom setups) without manually editing raw key codes in `config.ini`.
* **Drag-and-Drop & CLI Support:** Drop any `.json` preset file directly onto the script or pass it via command-line arguments.
* **Smart Config Discovery:** Automatically locates `config.ini` in your `Documents` folder, via the `SALT_DIR` environment variable, or across all Steam library folders (parsed from the Windows Registry and `libraryfolders.vdf`).
* **Side-by-Side Diff Preview:** Displays a clear comparison table (`Current -> Preset`) before applying changes, highlighting modified bindings with `*`.
* **Automatic Backup:** Creates a `config.ini.bak` backup before modifying your original configuration file.
* **Local Co-op Support:** Optionally mirrors bindings to Player 2 (`key_p1_*`) via the `MODIFY_P2` toggle.

---

## Requirements

* **OS:** Windows (uses `winreg` for Steam library detection)
* **Python:** Python 3.6+ (uses standard library modules only — no external `pip` packages required)

---

## Download / Installation

No Releases or complicated setup required — just grab the files directly from the repository:

1. Click the green **`<> Code`** button at the top of this page and select **Download ZIP** (or clone the repo via `git clone`).
2. Extract the archive anywhere on your PC.
3. Make sure **`salt_controls.py`** and the preset files (e.g., `preset_dark_souls.json`, `preset_original.json`) are kept in the same folder (or wherever is convenient for dragging and dropping).


---

## Usage

The script requires a path to a `.json` preset file as its first command-line argument. Running the script without arguments prints a usage guide and exits.

### 1. Drag-and-Drop (Windows Explorer)
Drag your desired preset file (e.g., `preset_dark_souls.json`) and drop it directly onto `salt_controls.py`.

> **Tip:** If Windows does not pass arguments when dropping files onto `.py` scripts due to file association settings, create a `run.bat` file in the same directory:
> ```bat
> @echo off
> python "%~dp0salt_controls.py" %1
> ```
> Then drag and drop `.json` files onto `run.bat`.

### 2. Command Line (CLI)
```bash
python salt_controls.py preset_dark_souls.json
```

### Applying a Preset
1. **Config Lookup:** The script searches for `config.ini` in the following order:
   * `%USERPROFILE%\Documents\Salt and Sanctuary\config\config.ini`
   * `%SALT_DIR%\config\config.ini` (if the `SALT_DIR` environment variable is set)
   * All Steam library folders detected via Registry and `libraryfolders.vdf` (verified by `salt.exe`)
   * Manual file selection dialog (fallback)
2. **Review Changes:** Inspect the comparison table in the console. Modified actions are marked with `*`.
3. **Confirm:** Type `y` and press `Enter` to write the changes. A `config.ini.bak` backup will be created automatically on the first run.

---

## Creating Custom Presets (`.json`)

Create a UTF-8 encoded `.json` file with the following structure:

```json
{
  "preset_name": "Dark Souls Style",
  "bindings": {
    "dodge": ["Space", "BUTTON_B"],
    "jump": ["LShift", "BUTTON_A"],
    "attack": ["LMB", "R1"],
    "strong": ["RMB", "R2"],
    "offhand": ["LCtrl", "L1"],
    "switch_loadout": ["V", "BUTTON_Y"]
  }
}
```

* **`preset_name`** *(string)* — Display name shown in the console when loaded.
* **`bindings`** *(object)* — Key-value pairs mapping an in-game action to `["KEYBOARD_OR_MOUSE_KEY", "GAMEPAD_BUTTON"]`. You do not need to list every action; omitted actions remain unchanged.

---

## Action Reference (`bindings`)

| Action Key | In-Game Function |
| :--- | :--- |
| `left` / `right` / `up` / `down` | Character movement |
| `attack` | Light attack |
| `strong` | Heavy attack |
| `jump` | Jump |
| `use` | Interact (doors, chests, shrines, dialogue) |
| `dodge` | Roll / Dodge |
| `offhand` | Block / Off-hand item (shield, wand, charm, firearm) |
| `switch_loadout` | Switch active loadout (`Loadout 1 / Loadout 2` & 1H/2H grip) |
| `inventory` | Open inventory / pause menu |
| `use_item` | Use quick-slot item (healing flask, consumables) |
| `item_left` / `item_right` | Cycle quick-slot items left / right |
| `torch` | Toggle torch |
| `look_left` / `look_right` / `look_up` / `look_down` | Pan camera |
| `accept` / `cancel` | Menu confirm / back |
| `y_option` / `x_option` | Secondary menu actions (Y / X) |

---

## Key & Button Reference

Key names are **case-insensitive** (`Space` and `space` are treated identically). Use `"None"` to unbind a key.

### Keyboard & Mouse
* **Mouse:** `LMB`, `RMB`, `MMB`, `MouseX1`, `MouseX2`
* **Alphanumeric:** `A`–`Z`, `0`–`9`
* **Arrow Keys:** `Left`, `Right`, `Up`, `Down`
* **Modifiers & Special Keys:** `Space`, `LShift`, `RShift`, `LCtrl`, `RCtrl`, `LAlt`, `RAlt`, `Tab`, `Esc`, `Backspace`, `Enter`
* **Raw Key Codes:** You can also pass a raw integer Windows Virtual-Key code directly instead of a string (e.g., `112` for `F1`).

### Gamepad
* **Face Buttons:** `BUTTON_A`, `BUTTON_B`, `BUTTON_X`, `BUTTON_Y`
* **Bumpers & Triggers:** `L1`, `R1`, `L2`, `R2`
* **Stick Clicks:** `BUTTON_L3`, `BUTTON_R3`
* **Menu Buttons:** `BUTTON_START`, `BUTTON_SELECT`
* **D-Pad:** `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`
* **Left Analog Stick:** `L_ANALOG_UP`, `L_ANALOG_DOWN`, `L_ANALOG_LEFT`, `L_ANALOG_RIGHT`
* **Right Analog Stick:** `R_ANALOG_UP`, `R_ANALOG_DOWN`, `R_ANALOG_LEFT`, `R_ANALOG_RIGHT`
