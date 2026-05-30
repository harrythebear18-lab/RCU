# RAM Monitor & Cleaner

A comprehensive RAM management solution for Windows with both command-line and GUI applications for optimizing system memory during gaming sessions and general use.

## Features

### Command-Line Script (`ram_cleanup_script.py`)
- 🧹 Comprehensive RAM cleanup
- 🗑️ Clears Windows system cache
- 🔄 Closes unnecessary processes
- 📊 Memory usage reporting
- ⚡ Performance optimization

### GUI Application (`ram_monitor_gui.py`)
- 📈 Real-time RAM monitoring
- 📊 Live memory usage graph
- 🧹 One-click cache clearing
- ⚙️ Auto-cleanup when usage >80%
- 🎨 Modern dark theme interface
- 📱 Intuitive controls

## Installation

1. **Install Python** (if not already installed):
   - Download Python 3.8+ from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install packages individually:
   ```bash
   pip install psutil matplotlib numpy
   ```

## Usage

### Command-Line Script

Run the RAM cleanup script:
```bash
python ram_cleanup_script.py
```

**Features:**
- Shows initial and final memory states
- Clears DNS cache and temporary files
- Closes unnecessary processes
- Optimizes system memory
- Reports memory usage improvement

**For best results:**
- Run as Administrator (right-click → "Run as administrator")
- Use before gaming sessions or when system feels sluggish

### GUI Application

Launch the RAM Monitor GUI:
```bash
python ram_monitor_gui.py
```

**GUI Features:**
- **Real-time Monitoring**: Shows current RAM usage with updates every second
- **Live Graph**: Visual representation of memory usage over time (last 60 seconds)
- **Memory Information**: Displays total, used, available RAM and usage percentage
- **Clean RAM Cache**: One-click button to clear system cache and optimize memory
- **Auto-cleanup**: Optional feature to automatically clean when usage exceeds 80%
- **Status Indicators**: Color-coded status (Green: Good, Yellow: Moderate, Red: High Usage)

## System Requirements

- Windows 10/11 (recommended)
- Python 3.8 or higher
- 4GB+ RAM recommended
- Administrator privileges (for full functionality)

## Safety Features

- **Safe Process Termination**: Only closes non-essential processes using less than 500MB
- **Non-Destructive**: Clears only temporary files and caches
- **Reversible**: All operations are safe and don't harm system stability
- **Monitoring**: Real-time feedback on memory changes

## Troubleshooting

### Common Issues

1. **"Access Denied" Errors**:
   - Run the script as Administrator
   - Right-click → "Run as administrator"

2. **GUI Won't Start**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.8+)

3. **No Memory Improvement**:
   - Some systems may already be optimized
   - Try closing applications manually before running cleanup
   - Restart your computer if memory usage remains high

### Performance Tips

- **Before Gaming**: Run the cleanup script 5-10 minutes before starting games
- **Regular Maintenance**: Use the GUI app to monitor memory usage patterns
- **Auto-cleanup**: Enable auto-cleanup for hands-free optimization
- **Monitor Trends**: Use the graph to identify memory-hungry applications

## File Descriptions

- `ram_cleanup_script.py` - Command-line RAM cleanup utility
- `ram_monitor_gui.py` - GUI application with real-time monitoring
- `requirements.txt` - Python package dependencies
- `README.md` - This documentation file

## Advanced Usage

### Customizing Safe-to-Close Processes

Edit the `safe_to_close` list in `ram_cleanup_script.py` to add or remove processes:
```python
safe_to_close = [
    'notepad.exe', 'mspaint.exe', 'calc.exe',
    # Add your custom processes here
]
```

### Scheduling Automatic Cleanup

You can use Windows Task Scheduler to run the cleanup script automatically:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at specific time)
4. Action: "Start a program"
5. Program: `python`
6. Arguments: `"path\to\ram_cleanup_script.py"`

## Support

For issues or suggestions:
- Check the troubleshooting section above
- Ensure all dependencies are properly installed
- Verify you're running as Administrator for full functionality

---

**Disclaimer**: This tool is designed for memory optimization and should not cause system instability. However, always save important work before running cleanup operations.
