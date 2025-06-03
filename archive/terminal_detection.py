#!/usr/bin/env python3
"""
Terminal Detection Script
Helps identify why drag and drop might not work in Claude Code CLI
"""

import os
import sys
import subprocess
import platform

def check_terminal_capabilities():
    print("🔍 Terminal Environment Analysis")
    print("=" * 50)
    
    # Basic environment info
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Terminal: {os.environ.get('TERM', 'Unknown')}")
    print(f"Shell: {os.environ.get('SHELL', 'Unknown')}")
    
    # Check if we're in WSL
    try:
        with open('/proc/version', 'r') as f:
            version = f.read()
            if 'microsoft' in version.lower() or 'wsl' in version.lower():
                print("🐧 Detected WSL environment")
            else:
                print("🐧 Native Linux environment")
    except:
        print("❓ Could not determine Linux environment type")
    
    # Check for display server
    display = os.environ.get('DISPLAY')
    wayland = os.environ.get('WAYLAND_DISPLAY')
    
    print(f"DISPLAY: {display or 'Not set'}")
    print(f"WAYLAND_DISPLAY: {wayland or 'Not set'}")
    
    if not display and not wayland:
        print("⚠️  No display server detected - this may prevent drag & drop")
    
    # Check for clipboard tools
    clipboard_tools = ['xclip', 'xsel', 'pbcopy', 'clip.exe']
    available_tools = []
    
    for tool in clipboard_tools:
        try:
            subprocess.run(['which', tool], check=True, capture_output=True)
            available_tools.append(tool)
        except subprocess.CalledProcessError:
            pass
    
    print(f"Clipboard tools available: {', '.join(available_tools) if available_tools else 'None'}")
    
    # Check for window manager
    window_managers = ['gnome-session', 'kde-session', 'xfce4-session', 'i3', 'sway']
    running_wm = []
    
    for wm in window_managers:
        try:
            subprocess.run(['pgrep', wm], check=True, capture_output=True)
            running_wm.append(wm)
        except subprocess.CalledProcessError:
            pass
    
    print(f"Window managers running: {', '.join(running_wm) if running_wm else 'None detected'}")
    
    # Check SSH connection
    if os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'):
        print("🔗 SSH connection detected - drag & drop may not work over SSH")
    
    # Check if we're in VS Code terminal
    if os.environ.get('VSCODE_INJECTION'):
        print("📝 VS Code terminal detected")
        print("   💡 VS Code terminal supports drag & drop directly")
    
    # Check if we're in Windows Terminal
    if os.environ.get('WT_SESSION'):
        print("💻 Windows Terminal detected")
        print("   💡 Windows Terminal supports drag & drop")
    
    print("\n🔧 Potential Issues & Solutions:")
    print("-" * 30)
    
    if not display and not wayland:
        print("❌ No GUI environment detected")
        print("   Solution: Use X11 forwarding with SSH or run in a GUI terminal")
    
    if os.environ.get('SSH_CLIENT'):
        print("❌ SSH connection detected")
        print("   Solution: Use local terminal or enable X11 forwarding")
    
    if not available_tools:
        print("❌ No clipboard tools found")
        print("   Solution: Install xclip (sudo apt install xclip)")
    
    if not running_wm:
        print("❌ No window manager detected")
        print("   Solution: Run in a desktop environment")
    
    print("\n✅ Recommendations:")
    print("- Use VS Code integrated terminal")
    print("- Use Windows Terminal if on Windows")
    print("- Ensure X11 forwarding if using SSH")
    print("- Try copy/paste instead of drag & drop")

if __name__ == "__main__":
    check_terminal_capabilities()