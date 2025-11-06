# 🚀 CODESENTINEL - START HERE

**Easiest Installation with GUI Wizard**

## ⚡ Quick Start (Choose Your OS)

### 🪟 Windows Users

**Double-click this file:**

```
INSTALL_CODESENTINEL_GUI.bat
```

That's it! The GUI setup wizard will launch automatically.

---

### 🍎 macOS Users

**Run this command:**

```bash
bash INSTALL_CODESENTINEL_GUI.sh
```

Or double-click `INSTALL_CODESENTINEL_GUI.sh` if you made it executable.

---

### 🐧 Linux Users

**Run this command:**

```bash
bash INSTALL_CODESENTINEL_GUI.sh
```

Or make it executable first:

```bash
chmod +x INSTALL_CODESENTINEL_GUI.sh
./INSTALL_CODESENTINEL_GUI.sh
```

---

## 📋 What These Installers Do

1. **Automatically install all dependencies** - No manual pip install needed
2. **Launch the interactive setup wizard** - Configure everything through the GUI
3. **Save your configuration** - All settings stored securely

**No documentation required.** The installer handles everything.

---

## ✨ What You'll Configure

After launching the installer, the wizard will guide you through:

- **📍 Installation Location** - Where to store CodeSentinel data
- **🔔 Alerts** - Console, file, email, or Slack notifications
- **🐙 GitHub Integration** - Connect your repositories (optional)
- **💻 IDE Detection** - Integrate with VS Code, PyCharm, etc. (optional)
- **⚙️ Advanced Features** - Scheduler, git hooks, CI templates (optional)

Everything is optional except location. You can skip advanced features for now.

---

## 🆘 If You Have Issues

### Problem: "Python not found"

- **Windows:** Install Python from <https://www.python.org/>
- **macOS:** Run `brew install python3`
- **Linux:** Run `sudo apt-get install python3` (Ubuntu/Debian)

**Make sure to check "Add Python to PATH" during Windows installation.**

### Problem: Installation hangs

- Close the window and try again
- Try running the Python script directly:

  ```bash
  python INSTALL_CODESENTINEL_GUI.py
  ```

### Problem: "No module named 'tkinter'"

- **Ubuntu/Debian:** Run `sudo apt-get install python3-tk`
- **Fedora:** Run `sudo dnf install python3-tkinter`
- **macOS:** TK is included with Python

---

## 📖 Advanced Installation

If you prefer command-line installation:

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup
codesentinel setup

# Verify installation
codesentinel status
```

---

## 🎯 After Installation

Once installed, you can use CodeSentinel:

```bash
# Check system status
codesentinel status

# View configuration
codesentinel config

# Run security audit
codesentinel !!!!

# Run maintenance
codesentinel maintenance --schedule daily
```

---

## 📚 Full Documentation

For detailed documentation, see:

- `README.md` - Main documentation
- `SECURITY.md` - Security policies
- `docs/` - Additional guides

---

## ❓ Still Confused?

**Just run one of these:**

- **Windows:** Double-click `INSTALL_CODESENTINEL_GUI.bat`
- **macOS/Linux:** `bash INSTALL_CODESENTINEL_GUI.sh`

**That's all you need to do.** Everything else is automatic.

---

**Happy monitoring! 🎉**
