# AutoKey - Keyboard Automation Tool

A PyQt6-based application for automating keyboard input on Windows, macOS, and Linux.

## Features

- **Text Input**: Send text with customizable character delays
- **Key Sending**: Send individual keys and key combinations
- **Automation**: Repeat text or actions with configurable intervals
- **Recording**: Record and replay keyboard sequences
- **Predefined Shortcuts**: Quick access to common key combinations (Ctrl+C, Ctrl+V, Alt+Tab, etc.)

## Installation

1. Install Python 3.7 or higher
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Tabs Overview

#### 1. Text Input
- Enter text in the text area
- Set delay between characters (in milliseconds)
- Click "Send Text" to type the text automatically

#### 2. Keys & Combinations
- **Single Key**: Send individual keys (e.g., 'enter', 'space', 'a')
- **Predefined Combinations**: Quick buttons for common shortcuts
- **Custom Combinations**: Create your own key combinations using '+' separator

#### 3. Automation
- Set text to repeat
- Configure number of repetitions and interval
- Start/stop repeating actions

#### 4. Recording
- Record keyboard input sequences
- Replay recorded sequences with customizable delay
- Clear recorded sequences

## Key Names Reference

### Special Keys
- `enter` - Enter key
- `space` - Space bar
- `tab` - Tab key
- `shift` - Shift key
- `ctrl` - Control key
- `alt` - Alt key
- `cmd` - Command key (macOS)
- `esc` - Escape key
- `backspace` - Backspace key
- `delete` - Delete key
- `up`, `down`, `left`, `right` - Arrow keys
- `f1`, `f2`, ..., `f12` - Function keys

### Regular Characters
Just use the character itself: `a`, `b`, `1`, `2`, `!`, `@`, etc.

## Key Combinations

Use the '+' separator to combine keys:
- `ctrl+c` - Copy
- `ctrl+v` - Paste
- `ctrl+shift+s` - Save As
- `alt+f4` - Close window

## Important Notes

- **Permissions**: On some systems, you may need to grant accessibility permissions for the app to control the keyboard
- **Focus**: Make sure the target application has focus when sending keys
- **Timing**: Adjust delays if keys are being sent too quickly for the target application
- **Recording**: Be careful when recording - all keyboard input will be captured

## Troubleshooting

### Permission Issues
- **macOS**: Go to System Preferences > Security & Privacy > Privacy > Accessibility and add Python or your terminal
- **Linux**: May require running with sudo depending on your system configuration
- **Windows**: Usually works without additional permissions

### Keys Not Working
- Try using lowercase key names
- For special characters, try using the character directly instead of key names
- Check that the target application can receive the input

## Safety Features

- The application runs in user space and doesn't require admin privileges on most systems
- Recording can be stopped at any time
- All automation can be stopped using the Stop buttons

## License

This project is open source. See LICENSE file for details.
