#!/usr/bin/env python3
"""
Start aria2c as a background RPC daemon for Windows.
"""

import subprocess
import sys
import os
import socket
import requests

def is_aria2c_running(port=6800):
    """Check if aria2c daemon is already running."""
    try:
        # Try to connect to the RPC port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
    except:
        return False

def check_aria2c_rpc():
    """Check if aria2c RPC is responding."""
    try:
        response = requests.post(
            "http://127.0.0.1:6800/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "aria2.getVersion",
                "params": ["token:MyCustomSecret123"]
            },
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

def start_aria2_daemon():
    """Launch aria2c as a background RPC daemon with configured parameters."""
    
    # Check if aria2c is already running
    if is_aria2c_running(6800):
        if check_aria2c_rpc():
            print("[INFO] aria2c daemon is already running and responding")
            print("  RPC server listening on port 6800")
            sys.exit(0)
        else:
            print("[WARNING] Port 6800 is in use but aria2c is not responding")
            print("  Please check for stuck aria2c processes")
            sys.exit(1)
    
    # Configure aria2c RPC parameters
    # Explicitly set Downloads directory
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    
    # Create Downloads directory if it doesn't exist
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir, exist_ok=True)
    
    aria2_command = [
        "aria2c",
        "--enable-rpc",                    # Enable JSON-RPC server
        "--rpc-listen-all=true",           # Listen on all network interfaces
        "--rpc-allow-origin-all=true",     # Allow cross-origin requests
        "--rpc-listen-port=6800",          # RPC server port
        "--rpc-secret=MyCustomSecret123",  # RPC secret token
        "--max-connection-per-server=16",  # Max connections per server
        "--split=16",                      # Split file into 16 parts
        "--continue=true",                 # Enable auto-resume
        f"--dir={downloads_dir}"          # Explicitly set Downloads directory
    ]
    
    try:
        # Launch aria2c in background without console window
        # Use CREATE_NEW_PROCESS_GROUP and DETACHED_PROCESS for background operation
        # CREATE_NO_WINDOW flag prevents console window from appearing
        DETACHED_PROCESS = 0x00000008  # Windows flag for detached process
        process = subprocess.Popen(
            aria2_command,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | DETACHED_PROCESS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        
        print("[OK] aria2c daemon started successfully")
        print(f"  RPC server listening on port 6800")
        print(f"  RPC secret token: MyCustomSecret123")
        print(f"  Process ID: {process.pid}")
        print("\nDaemon is running in the background.")
        print("You can now start the GUI with: pyw app.pyw")
        
        # Exit immediately - daemon continues running in background
        sys.exit(0)
            
    except FileNotFoundError:
        print("[ERROR] aria2c is not installed or not in PATH")
        print("  Please install aria2c from: https://aria2.github.io/")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error starting aria2c daemon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_aria2_daemon()
