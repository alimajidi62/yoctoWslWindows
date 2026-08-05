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
