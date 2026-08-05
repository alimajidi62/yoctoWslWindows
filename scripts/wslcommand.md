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
