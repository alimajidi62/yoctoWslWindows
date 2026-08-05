# WSL Setup & Basic C Development Commands

## 1. WSL Installation (run in Windows PowerShell)

```powershell
# List all available Linux distributions you can install
wsl --list --online

# Install Ubuntu 24.04 as your WSL distribution
wsl --install -d Ubuntu-24.04

# Check installed distributions and their running status (Version 1 or 2)
wsl -l -v
```

---

## 2. Update Package Lists (run inside WSL/Ubuntu)

```bash
# Refresh the list of available packages from Ubuntu repositories
sudo apt update
```

---

## 3. Install C/C++ Build Tools

```bash
# Install GCC, G++, make, and other essential compilation tools
sudo apt install build-essential -y

# Verify GCC (C compiler) version
gcc --version

# Verify G++ (C++ compiler) version
g++ --version
```

---

## 4. Hello World in C

```bash
# Open (or create) hello.c in the nano text editor
nano hello.c
```

Paste this into the editor, then save with `Ctrl+O` and exit with `Ctrl+X`:

```c
#include <stdio.h>

int main()
{
    printf("Hello World\n");
    return 0;
}
```

```bash
# Compile hello.c and produce an executable named "hello"
gcc hello.c -o hello

# Run the compiled program
./hello
```

---

## 5. Install Common Development Tools

```bash
# Install git, cmake, gdb (debugger), vim, curl, wget, and unzip
sudo apt install git cmake gdb vim curl wget unzip -y
```

---

## 6. Install Python 3 and Test It

```bash
# Make sure package list is up to date
sudo apt update

# Install Python 3 and pip (package manager for Python)
sudo apt install python3 python3-pip -y

# Verify Python and pip versions
python3 --version
pip3 --version

# Quick sanity test — run a one-liner directly in the terminal
python3 -c "print('Hello from Python in WSL!')"

# Start the interactive Python shell (type exit() to quit)
python3
```

---

## 7. Write and Run a Python Script

```bash
# Create and open hello.py in the nano text editor
nano hello.py
```

Add this line, then save with `Ctrl+O` and exit with `Ctrl+X`:

```python
print("Hello Ali!")
```

```bash
# Run the script — expected output: Hello Ali!
python3 hello.py
```

---

## 8. Create and Use a Python Virtual Environment

```bash
# Create an isolated virtual environment named "myenv"
python3 -m venv myenv

# Activate the virtual environment
source myenv/bin/activate
# Your prompt will change to: (myenv) user@machine:~$

# Install packages inside the venv without affecting the system Python
pip install <package-name>

# Deactivate when done
deactivate
```

---

## 9. NVIDIA GPU Access in WSL2 (RTX 2000 Ada)

> **How it works:** WSL2 uses GPU Paravirtualization — the Windows NVIDIA driver
> (already installed on your machine, version 32.0.15.9595) handles the GPU and
> exposes it to WSL2. **Do NOT install the full NVIDIA Linux driver inside WSL** —
> it will break the paravirtualization layer.

### Step 1 — Verify the GPU is visible inside WSL

```bash
# Should list your NVIDIA GPU if the Windows driver supports WSL2
ls /dev/dxg
nvidia-smi
```

### Step 2 — Install CUDA Toolkit inside WSL (Ubuntu 24.04)

```bash
# Add the NVIDIA CUDA repository for Ubuntu 24.04
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update

# Install the CUDA toolkit (compiler, libraries, tools)
sudo apt install cuda-toolkit -y

# Verify the CUDA compiler is available
nvcc --version
```

### Step 3 — Test GPU with a Python Script

```bash
# Install PyTorch with CUDA support
pip install torch --index-url https://download.pytorch.org/whl/cu128

# Confirm PyTorch can see the GPU
python3 -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
# Expected output:
# True
# NVIDIA RTX 2000 Ada Generation Laptop GPU
```

### Notes
- The CUDA version installed must match your Windows driver's supported CUDA version.
  Run `nvidia-smi` on Windows first to see the max supported CUDA version.
- WSL2 is required (not WSL1). Confirm with `wsl -l -v` — version must be **2**.
- If `nvidia-smi` fails inside WSL, update your Windows NVIDIA driver from
  https://www.nvidia.com/drivers