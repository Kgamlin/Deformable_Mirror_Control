# DM_Control

Python interface for the Boston Micromachines (BMC) deformable mirror (DM).
This submodule is part of the `ArbPotential_Optical_Control` project.

---

## Environment overview

This submodule requires **two separate Python environments** that must never be mixed:

| Environment | Python | Purpose |
|---|---|---|
| `venv_bmc_py36` | **3.6.8 only** | Scripts that directly control the DM hardware |
| `venv_main` | 3.11+ | Analysis, plotting, profile generation |

The split is forced by the BMC SDK: its compiled extension (`_bmc.pyd`) is
ABI-locked to Python 3.6. No other Python version will load it (to my knowledge was the "newest version" where I hadn't any issues).

---

## Prerequisites

Install these before setting up any environment:

1. **Python 3.6.8 (64-bit)** — download from [python.org](https://www.python.org/downloads/release/python-368/)
2. **BMC DM SDK 4.2.1** — download and install from [bostonmicromachines.com/dmsdk](https://bostonmicromachines.com/dmsdk/)
   After installation the SDK lives at:
   ```
   C:\Program Files\Boston Micromachines\Bin64\
   C:\Program Files\Boston Micromachines\Bin64\Python3\site-packages\bmc\
   ```
3. **Microsoft Visual C++ Redistributable (x64)** — required for the native DLLs
4. Ensure the BMC Bin64 folder is on your system `PATH`:
   ```
   C:\Program Files\Boston Micromachines\Bin64
   ```

---

## 1. Hardware control environment (`venv_bmc_py36`)

This environment lives **outside the project** in a central location so it can be
reused across future DM-related projects. (can also live inside if you have good reason)

### Create the environment

```powershell
# Verify Python 3.6 is available
py -3.6 --version   # expected: Python 3.6.8

# Create the environment (adjust path to your preference)
py -3.6 -m venv C:\Users\<username>\Documents\my_venvs\venv_bmc_py36

# Activate
C:\Users\<username>\Documents\my_venvs\venv_bmc_py36\Scripts\activate
```

### Install packages

```powershell
pip install -r requirements_bmc.txt
```

`requirements_bmc.txt` is at the root of `ArbPotential_Optical_Control`.

### Integrate the BMC SDK

The `bmc` package is **not on PyPI**. Expose it to the environment via a `.pth` file:

```powershell
# From inside the activated environment
cd C:\Users\<username>\Documents\my_venvs\venv_bmc_py36\Lib\site-packages

# Create the .pth file (PowerShell)
"C:\Program Files\Boston Micromachines\Bin64\Python3\site-packages" | Out-File bmc_sdk.pth -Encoding ascii
```

Deactivate and reactivate the environment, then verify:

```powershell
python -c "import bmc; print(bmc.BmcDm_version_string())"
# Expected output: 4.2.1
```

---

## 2. Analysis environment (`venv_main`)

This environment is already created at the project root (`ArbPotential_Optical_Control/venv_main/`).
To recreate it from scratch:

```powershell
py -3.11 -m venv venv_main
venv_main\Scripts\activate
pip install -r requirements_main.txt
```

This environment **never imports `bmc`** and never controls hardware.

---

## PyCharm setup

1. Set `venv_main` as the **project default interpreter**
   (`Settings → Project → Python Interpreter → venv_main\Scripts\python.exe`)
2. For scripts that control the DM hardware, create a dedicated **Run Configuration**:
   - `Run → Edit Configurations → + → Python`
   - Set interpreter to `venv_bmc_py36\Scripts\python.exe`
   - Save the configuration — you will reuse it for all hardware scripts

This means you never manually switch environments: analysis scripts run with the
project default, hardware scripts run via their saved configuration.

---

## Project structure

```
DM_Control/
├── DM_Control_Class/
│   ├── dm_wrapper.py        # DMClass — hardware wrapper (venv_bmc only)
│   ├── patterns.py          # Zernike and flat pattern generators
│   └── project_DM_shape.py  # Projects a target shape onto the DM
├── DM_generate_profiles/
│   └── DM_generate_Profile.py  # Generates DM command profiles (venv_main)
└── RIN_analysis/
    └── Spectrum_RIN_class.py   # RIN spectrum analysis (venv_main)
```

### Which environment to use per script

| File | Environment |
|---|---|
| `DM_Control_Class/dm_wrapper.py` | `venv_bmc_py36` |
| `DM_Control_Class/patterns.py` | `venv_bmc_py36` |
| `DM_Control_Class/project_DM_shape.py` | `venv_bmc_py36` |
| `DM_generate_profiles/` | `venv_main` |
| `RIN_analysis/` | `venv_main` |

---

## Safety guards

The following guards are at the top of hardware control scripts to prevent
accidental execution with the wrong interpreter:

```python
import sys
if sys.version_info[:2] != (3, 6):
    raise RuntimeError(
        "BMC DM control requires Python 3.6 — activate venv_bmc_py36"
    )
```

Analysis scripts that must not run in the BMC environment:

```python
import sys
if sys.version_info < (3, 10):
    raise RuntimeError("This script requires Python >= 3.10 — activate venv_main")
```