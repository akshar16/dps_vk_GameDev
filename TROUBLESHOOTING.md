# Cross-Platform Troubleshooting Guide

## Windows Issues

### Problem: "Python is not recognized as an internal or external command"
**Solution:**
1. Install Python from https://python.org
2. During installation, check "Add Python to PATH"
3. Or manually add Python to your system PATH

### Problem: "No module named 'pygame'"
**Solution:**
```cmd
pip install pygame-ce pytmx
```

### Problem: Audio not playing
**Solution:**
- Ensure your system has working audio drivers
- Try running with administrator privileges
- Check if Windows Defender is blocking the audio files

### Problem: Game window not appearing
**Solution:**
- Check if your graphics drivers are up to date
- Try running in compatibility mode
- Ensure you have sufficient display resolution (minimum 1280x720)

## Mac Issues

### Problem: "command not found: python"
**Solution:**
Use `python3` instead:
```bash
python3 start_screen.py
```

### Problem: "Permission denied"
**Solution:**
```bash
chmod +x run_game.sh
./run_game.sh
```

### Problem: "Framework not found" or security warnings
**Solution:**
1. Go to System Preferences > Security & Privacy
2. Allow the app to run
3. Or install pygame-ce using homebrew:
```bash
brew install python
pip3 install pygame-ce pytmx
```

## Linux Issues

### Problem: Missing dependencies
**Solution (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3-pip python3-dev
pip3 install pygame-ce pytmx
```

**Solution (Fedora/CentOS):**
```bash
sudo dnf install python3-pip python3-devel
pip3 install pygame-ce pytmx
```

### Problem: Audio issues
**Solution:**
```bash
sudo apt install pulseaudio alsa-utils
```

## General Issues

### Problem: Game crashes on startup
**Solutions:**
1. Check that all files are present in the correct directories
2. Verify folder names (note the spaces in "stage 1" and "stage 2")
3. Run from command line to see error messages
4. Update pygame-ce to the latest version:
   ```bash
   pip install --upgrade pygame-ce
   ```

### Problem: Poor performance
**Solutions:**
1. Close other applications
2. Update graphics drivers
3. Lower system load
4. Check if running on integrated graphics instead of dedicated GPU

### Problem: Font not loading
**Solution:**
The game includes fallback fonts, but for best experience:
1. Ensure `fonts/04B_30__.TTF` file exists
2. Check file permissions
3. The game will use system fonts if custom font fails

## Getting Help

If you're still experiencing issues:
1. Check the console output for error messages
2. Ensure you're running the latest version
3. Try the different launch methods (batch file, Python script, etc.)
4. Create an issue on GitHub with:
   - Your operating system and version
   - Python version (`python --version`)
   - Error messages
   - Steps to reproduce the problem

## File Structure Check

Your game folder should look like this:
```
game-folder/
├── start_screen.py
├── run_game.py
├── run_game.bat (Windows)
├── run_game.sh (Mac/Linux)
├── fonts/
│   └── 04B_30__.TTF
├── stage 1 /          # Note the trailing space
│   ├── code/
│   ├── audio/
│   ├── data/
│   └── images/
└──  stage 2/          # Note the leading space
    ├── code/
    ├── audio/
    ├── data/
    └── images/
```
