import os
import re
import sys
import json
import string
import shutil
import winreg
import tkinter as tk
from tkinter import filedialog

# ==========================================
# 1. DEFAULT SCRIPT SETTINGS
# ==========================================
# Apply control bindings to Player 2 (local co-op) as well
MODIFY_P2 = True


# ==========================================
# 2. KEY NAME TO KEY CODE MAPPING DICTIONARIES
# ==========================================
KB_NAME_TO_CODE = {
    "None": 0,
    "LMB": -2, "RMB": -1, "MMB": -3, "MouseX1": -4, "MouseX2": -5,
    "Space": 32, "LShift": 160, "RShift": 161, "LCtrl": 162, "RCtrl": 163,
    "LAlt": 164, "RAlt": 165, "Tab": 9, "Esc": 27, "Backspace": 8, "Enter": 13,
    "Left": 37, "Up": 38, "Right": 39, "Down": 40
}
# Automatically populate uppercase letters A-Z and digits 0-9
for c in string.ascii_uppercase:
    KB_NAME_TO_CODE[c] = ord(c)
for i in range(10):
    KB_NAME_TO_CODE[str(i)] = 48 + i

PAD_NAME_TO_CODE = {
    "None": 0,
    "L_ANALOG_LEFT": -6, "L_ANALOG_RIGHT": -7, "L_ANALOG_UP": -8, "L_ANALOG_DOWN": -9,
    "DPAD_LEFT": -10, "DPAD_RIGHT": -11, "DPAD_UP": -12, "DPAD_DOWN": -13,
    "BUTTON_A": -14, "BUTTON_B": -15, "BUTTON_X": -16, "BUTTON_Y": -17,
    "R1": -18, "R2": -19, "L1": -20, "L2": -21,
    "BUTTON_START": -22, "BUTTON_SELECT": -23,
    "R_ANALOG_LEFT": -24, "R_ANALOG_RIGHT": -25, "R_ANALOG_UP": -26, "R_ANALOG_DOWN": -27,
    "BUTTON_L3": -28, "BUTTON_R3": -29
}

# Case-insensitive lookup and reverse dictionaries for console preview
KB_LOWER_TO_CODE = {k.lower(): v for k, v in KB_NAME_TO_CODE.items()}
PAD_LOWER_TO_CODE = {k.lower(): v for k, v in PAD_NAME_TO_CODE.items()}

CODE_TO_KB = {v: k for k, v in KB_NAME_TO_CODE.items()}
CODE_TO_PAD = {v: k for k, v in PAD_NAME_TO_CODE.items()}

# ==========================================
# 3. PRESET LOADING & CONFIG.INI DISCOVERY
# ==========================================
def print_usage():
    script_name = os.path.basename(sys.argv[0])
    print("==========================================================")
    print("ERROR: No preset file (.json) specified.")
    print("==========================================================")
    print("This script requires a path to a JSON preset file passed")
    print("via command-line arguments or Drag-and-Drop.\n")
    print("Usage:")
    print(f"  1. Drag and drop a .json preset file onto {script_name}")
    print(f"  2. Via terminal: python {script_name} <path_to_preset.json>")
    print("==========================================================")


def load_preset():
    """Load the JSON preset file passed via command-line arguments."""
    if len(sys.argv) < 2:
        print_usage()
        return None

    preset_path = sys.argv[1]

    if not os.path.isfile(preset_path):
        print(f"\n[ERROR] Specified preset file was not found:\n{preset_path}")
        return None

    try:
        with open(preset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "bindings" not in data or not isinstance(data["bindings"], dict):
            print("\n[ERROR] Invalid JSON structure: missing 'bindings' section.")
            return None
        print(f"\n[OK] Loaded preset: {data.get('preset_name', os.path.basename(preset_path))}")
        return data
    except json.JSONDecodeError as e:
        print(f"\n[ERROR] JSON syntax error: {e}")
        return None
    except Exception as e:
        print(f"\n[ERROR] Failed to read preset file: {e}")
        return None


def get_steam_libraries():
    """Read the Steam installation path from the Windows Registry and parse libraryfolders.vdf."""
    steam_path = None
    reg_locations = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
    ]

    for hkey, subkey, value_name in reg_locations:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                steam_path, _ = winreg.QueryValueEx(key, value_name)
                if steam_path and os.path.exists(steam_path):
                    break
        except OSError:
            continue

    if not steam_path:
        return []

    libraries = [os.path.normpath(steam_path)]
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")

    if os.path.isfile(vdf_path):
        try:
            with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for match in re.findall(r'"path"\s+"([^"]+)"', content):
                lib_path = os.path.normpath(match.replace("\\\\", "\\"))
                if lib_path not in libraries:
                    libraries.append(lib_path)
        except OSError:
            pass

    return libraries


def find_game_dir():
    """Locate the game installation directory via SALT_DIR env var or Steam libraries."""
    env_dir = os.environ.get("SALT_DIR")
    if env_dir and os.path.isfile(os.path.join(env_dir, "salt.exe")):
        return os.path.normpath(env_dir)

    for lib in get_steam_libraries():
        candidate = os.path.join(lib, "steamapps", "common", "Salt and Sanctuary")
        if os.path.isfile(os.path.join(candidate, "salt.exe")):
            return candidate

    return None


def find_config_file():
    print("Searching for game config.ini...")

    # 1. Priority: standard user profile folder in Documents
    doc_path = os.path.expanduser(r"~\Documents\Salt and Sanctuary\config\config.ini")
    if os.path.isfile(doc_path):
        return doc_path

    # 2. Fallback: game installation directory (via SALT_DIR or Steam Registry + VDF)
    game_dir = find_game_dir()
    if game_dir:
        game_cfg = os.path.join(game_dir, "config", "config.ini")
        if os.path.isfile(game_cfg):
            return game_cfg

    # 3. Manual file selection dialog if not found automatically
    print("Could not locate config.ini automatically. Please select it manually.")
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Select config.ini", filetypes=[("INI files", "*.ini")])

# ==========================================
# 4. PREVIEW & CONFIG UPDATE LOGIC
# ==========================================
def resolve_key_code(name, mapping_dict, device_label, action):
    """Convert a key/button name into its numeric code with typo validation."""
    if isinstance(name, int):
        return name
    code = mapping_dict.get(str(name).strip().lower())
    if code is None:
        print(f"  [WARNING] Unknown {device_label} key '{name}' for action '{action}'. Defaulting to 'None' (0).")
        return 0
    return code


def apply_preset(file_path, preset_data):
    bindings = preset_data["bindings"]

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    controls = {}
    for line in lines:
        if line.startswith("key_p0_") or line.startswith("key_p1_"):
            action, values = line.strip().split('=', 1)
            controls[action] = values.split('|')

    # Print side-by-side comparison table (Current -> Preset)
    print("\n" + "=" * 84)
    print(f"{'ACTION':<16} | {'CURRENT (Keyboard / Gamepad)':<30} | {'PRESET (Keyboard / Gamepad)':<30}")
    print("=" * 84)

    for action, vals in controls.items():
        if not action.startswith("key_p0_"):
            continue
        short_name = action[7:]

        # Current bindings
        cur_kb = CODE_TO_KB.get(int(vals[0]), f"Code({vals[0]})")
        cur_pad = CODE_TO_PAD.get(int(vals[1]), f"Code({vals[1]})")
        cur_str = f"{cur_kb} / {cur_pad}"

        # Proposed preset bindings
        if short_name in bindings:
            new_kb_name, new_pad_name = bindings[short_name]
            new_kb_code = resolve_key_code(new_kb_name, KB_LOWER_TO_CODE, "Keyboard", short_name)
            new_pad_code = resolve_key_code(new_pad_name, PAD_LOWER_TO_CODE, "Gamepad", short_name)

            disp_kb = CODE_TO_KB.get(new_kb_code, str(new_kb_code))
            disp_pad = CODE_TO_PAD.get(new_pad_code, str(new_pad_code))
            new_str = f"{disp_kb} / {disp_pad}"
            marker = " *" if cur_str != new_str else ""
        else:
            new_str = "(unchanged)"
            marker = ""

        print(f"{short_name:<16} | {cur_str:<30} | {new_str:<30}{marker}")

    print("=" * 84)
    print("* — bindings that will be modified.")
    print(f"Mirror bindings to Player 2 (P2): {'YES' if MODIFY_P2 else 'NO'}")

    print("\nApply this preset? (y / n)")
    if input("> ").strip().lower() != 'y':
        print("\nCancelled by user. No changes were made.")
        return

    # Create a backup BEFORE modifying the file
    backup = file_path + ".bak"
    if not os.path.exists(backup):
        shutil.copy2(file_path, backup)
        print(f"\n[BACKUP] Created original config backup: {backup}")

    # Apply new keybindings
    for action_name, pair in bindings.items():
        kb_name, pad_name = pair
        kb_code = resolve_key_code(kb_name, KB_LOWER_TO_CODE, "Keyboard", action_name)
        pad_code = resolve_key_code(pad_name, PAD_LOWER_TO_CODE, "Gamepad", action_name)
        new_val = [str(kb_code), str(pad_code), "0"]

        p1_key = f"key_p0_{action_name}"
        if p1_key in controls:
            controls[p1_key] = new_val

        if MODIFY_P2:
            p2_key = f"key_p1_{action_name}"
            if p2_key in controls:
                controls[p2_key] = new_val

    for i, line in enumerate(lines):
        if line.startswith("key_p0_") or line.startswith("key_p1_"):
            action = line.split('=')[0]
            if action in controls:
                lines[i] = f"{action}={'|'.join(controls[action])}\n"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("\n==========================================")
    print("SUCCESS! Preset applied to config.ini.")
    print("You can now launch the game and close this window.")
    print("==========================================")


if __name__ == "__main__":
    try:
        preset = load_preset()
        if preset:
            path = find_config_file()
            if path:
                print(f"[OK] Config found: {path}")
                apply_preset(path, preset)
            else:
                print("\n[ERROR] No config.ini file selected.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")

    input("\nPress Enter to exit...")
