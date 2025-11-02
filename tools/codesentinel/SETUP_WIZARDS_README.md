# CodeSentinel Setup Wizards

CodeSentinel provides two setup wizards to accommodate different user preferences and environments:

## Terminal Wizard (Default)

The traditional command-line interface wizard that guides you through setup with text prompts.

### Usage

```bash
# Interactive setup (recommended for most users)
codesentinel-setup

# Automated setup with defaults
codesentinel-setup --non-interactive

# Specify custom install location
codesentinel-setup --install-location /path/to/install
```

### Features

- ✅ Works in any terminal environment
- ✅ Perfect for headless servers and CI/CD
- ✅ Keyboard navigation
- ✅ Detailed progress feedback
- ✅ Scriptable and automatable

## GUI Wizard (Pop-up Interface)

A modern graphical interface that provides an intuitive setup experience with forms and dialogs.

### Usage

```bash
# Launch GUI wizard
codesentinel-setup --gui

# Or use the direct launcher
codesentinel-setup-gui
```

### Features

- 🎨 Modern graphical interface
- 🖱️ Point-and-click navigation
- 📋 Form-based configuration
- 🔍 Real-time validation
- 📊 Visual progress indicators
- 🎯 User-friendly for beginners

## Unified Launcher

Use the unified launcher to choose between interfaces:

```bash
# Show available options
codesentinel-setup --help

# Terminal mode (default)
codesentinel-setup

# GUI mode
codesentinel-setup --gui
```

## Setup Flow Comparison

### Terminal Wizard Flow

```
Welcome Message
├── Install Location (prompt)
├── System Requirements Check
├── Environment Variables Setup
├── Alert System Configuration
│   ├── Console/File alerts
│   ├── Email configuration (optional)
│   └── Slack configuration (optional)
├── GitHub Integration (if in repo)
├── IDE Integration
├── Optional Features
└── Summary & Completion
```

### GUI Wizard Flow

```
[Welcome Screen]
├── Installation Location (form)
├── System Requirements (progress)
├── Environment Setup (info)
├── Alert System (checkboxes + forms)
├── GitHub Integration (checkboxes + forms)
├── IDE Integration (checkboxes)
├── Optional Features (checkboxes)
└── Summary & Finish
```

## Configuration Options

Both wizards configure the same CodeSentinel features:

### Alert Channels

- **Console**: Terminal output notifications
- **File**: Log file storage
- **Email**: SMTP-based email alerts (multiple recipients supported)
- **Slack**: Webhook-based Slack notifications

### GitHub Integration

- **Copilot**: Integration instructions and commands
- **API**: Advanced features with token authentication
- **Repository**: Issue templates and workflow automation

### IDE Support

- **VS Code**: Tasks and settings integration

### Optional Features

- **Cron Jobs**: Automated maintenance scheduling
- **Git Hooks**: Pre-commit validation
- **CI/CD**: Workflow templates

## Choosing the Right Wizard

### Use Terminal Wizard When

- Setting up on a server/headless environment
- Automating installation in scripts
- Preferring keyboard navigation
- Working in terminals/SSH sessions

### Use GUI Wizard When

- First-time setup on desktop environment
- Preferring graphical interfaces
- Need visual feedback and validation
- Want to explore options interactively

## Requirements

### Terminal Wizard

- Python 3.13+
- Terminal access

### GUI Wizard

- Python 3.13+
- tkinter (usually included with Python)
- Display environment (X11, Wayland, or Windows GUI)

## Troubleshooting

### GUI Wizard Won't Start

```bash
# Check if tkinter is available
python -c "import tkinter; print('tkinter available')"

# Install tkinter if missing (Ubuntu/Debian)
sudo apt-get install python3-tk

# Install tkinter if missing (macOS with Homebrew)
brew install python-tk
```

### Permission Issues

Both wizards require write permissions to the installation directory and may need to modify shell profiles for environment variables.

### GitHub Integration

GitHub features are only available when running in a git repository. The wizards will automatically detect and configure accordingly.
