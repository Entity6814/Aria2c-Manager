#!/usr/bin/env python3
"""
PyQt6 GUI Dashboard for Aria2 Download Manager.
Modern browser-like interface with inline controls, crash resistance, and notifications.
"""

import sys
import json
import requests
import os
import subprocess
import webbrowser
import threading
import socket
from datetime import datetime
from flask import Flask, jsonify, request
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QProgressBar, QStatusBar, QMessageBox,
    QHeaderView, QAbstractItemView, QScrollArea, QFrame,
    QSystemTrayIcon, QMenu, QStyle
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject, QEvent
from PyQt6.QtGui import QColor, QPalette, QAction


# Flask API server for extension communication
flask_app = Flask(__name__)
api_server = None

@flask_app.route('/status', methods=['GET'])
def get_status():
    """Check if the application is running."""
    return jsonify({"status": "running", "app": "Aria2c Manager"})

@flask_app.route('/show', methods=['POST'])
def show_window():
    """Show the GUI window (bring to front)."""
    if api_server and hasattr(api_server, 'gui_window'):
        api_server.gui_window.show()
        api_server.gui_window.raise_()
        api_server.gui_window.activateWindow()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "GUI window not available"})

@flask_app.route('/start-daemon', methods=['POST'])
def start_daemon():
    """Start the aria2c daemon."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        daemon_script = os.path.join(script_dir, "start_aria2.py")
        
        # Start daemon in background
        subprocess.Popen(
            ["pyw", daemon_script],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW | 0x00000008,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


class APIServer:
    """Flask API server running in a separate thread."""
    
    def __init__(self, gui_window, port=5678):
        self.gui_window = gui_window
        self.port = port
        self.thread = None
        self.running = False
    
    def start(self):
        """Start the Flask server in a separate thread."""
        if self.running:
            return
        
        global api_server
        api_server = self
        
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"[INFO] API server started on port {self.port}")
    
    def _run_server(self):
        """Run the Flask server."""
        flask_app.run(host='127.0.0.1', port=self.port, use_reloader=False, debug=False)
    
    def stop(self):
        """Stop the Flask server."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)


def check_single_instance(port=5678):
    """Check if another instance is already running."""
    try:
        # Try to connect to the API server
        response = requests.get(f"http://127.0.0.1:{port}/status", timeout=1)
        if response.status_code == 200:
            return True  # Another instance is running
    except:
        pass
    return False  # No other instance running


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except:
            return True


class UpdateManager:
    """Handles application updates from GitHub."""
    
    def __init__(self, repo_owner="Entity6814", repo_name="Aria2c-Manager"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = "1.0.0"
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    def check_for_updates(self):
        """Check if a newer version is available on GitHub."""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            
            latest_version = release_data.get("tag_name", "").lstrip("v")
            download_url = release_data.get("html_url", "")
            release_notes = release_data.get("body", "")
            
            if self._is_newer_version(latest_version):
                return {
                    "has_update": True,
                    "current_version": self.current_version,
                    "latest_version": latest_version,
                    "download_url": download_url,
                    "release_notes": release_notes
                }
            else:
                return {
                    "has_update": False,
                    "current_version": self.current_version,
                    "latest_version": latest_version
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Error checking for updates: {e}")
            return {"has_update": False, "error": str(e)}
    
    def _is_newer_version(self, version_string):
        """Compare version strings to check if newer version exists."""
        try:
            current_parts = [int(x) for x in self.current_version.split(".")]
            latest_parts = [int(x) for x in version_string.split(".")]
            
            # Pad with zeros if lengths differ
            max_length = max(len(current_parts), len(latest_parts))
            current_parts += [0] * (max_length - len(current_parts))
            latest_parts += [0] * (max_length - len(latest_parts))
            
            return latest_parts > current_parts
        except:
            return False
    
    def open_download_page(self):
        """Open the GitHub releases page in browser."""
        webbrowser.open(f"https://github.com/{self.repo_owner}/{self.repo_name}/releases/latest")
    
    def get_app_update_url(self):
        """Get the direct download URL for the application."""
        return f"https://github.com/{self.repo_owner}/{self.repo_name}/releases/latest"


class DownloadState:
    """Persistent download state for crash resistance."""
    
    def __init__(self, state_file="downloads_state.json"):
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self):
        """Load download state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {"downloads": {}}
        return {"downloads": {}}
    
    def save_state(self):
        """Save download state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def add_download(self, gid, url, filename, source="gui"):
        """Add download to state."""
        self.state["downloads"][gid] = {
            "gid": gid,
            "url": url,
            "filename": filename,
            "source": source,
            "added_time": datetime.now().isoformat(),
            "status": "active"
        }
        self.save_state()
    
    def update_download_status(self, gid, status, progress=0):
        """Update download status."""
        if gid in self.state["downloads"]:
            self.state["downloads"][gid]["status"] = status
            self.state["downloads"][gid]["progress"] = progress
            self.state["downloads"][gid]["last_update"] = datetime.now().isoformat()
            self.save_state()
    
    def remove_download(self, gid):
        """Remove download from state."""
        if gid in self.state["downloads"]:
            del self.state["downloads"][gid]
            self.save_state()
    
    def get_downloads(self):
        """Get all downloads from state."""
        return self.state.get("downloads", {})


class Aria2RPCClient:
    """JSON-RPC client for communicating with aria2c daemon."""
    
    def __init__(self, rpc_url="http://localhost:6800/jsonrpc", rpc_secret="MyCustomSecret123"):
        self.rpc_url = rpc_url
        self.rpc_secret = rpc_secret
        self.connected = False
    
    def call_rpc(self, method, params=None):
        """Generic JSON-RPC 2.0 call method."""
        if params is None:
            params = []
        
        # Add secret token to params if not already present
        if method.startswith("aria2.") and not any(str(p).startswith("token:") for p in params):
            params = [f"token:{self.rpc_secret}"] + params
        
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": method,
            "params": params
        }
        
        try:
            response = requests.post(self.rpc_url, json=payload, timeout=5)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"RPC Error: {result['error']}")
            
            self.connected = True
            return result.get("result")
            
        except requests.exceptions.ConnectionError:
            self.connected = False
            raise ConnectionError("Cannot connect to aria2c RPC server")
        except requests.exceptions.RequestException as e:
            self.connected = False
            raise Exception(f"RPC request failed: {e}")
    
    def add_download(self, url, options=None):
        """Add a new download to aria2."""
        # Default options for better download reliability
        default_options = {
            "max-connection-per-server": "16",
            "split": "16",
            "continue": "true",
            "check-certificate": "false",
            "timeout": "60",
            "retry-wait": "5",
            "max-tries": "5"
        }
        
        # Don't set download directory - let aria2c use its default
        # This matches the extension behavior and avoids path issues
        
        # Merge with user-provided options
        if options:
            default_options.update(options)
        
        # aria2c expects [url] format (single array)
        params = [[url], default_options]
        return self.call_rpc("aria2.addUri", params)
    
    def tell_active(self):
        """Get list of active downloads."""
        return self.call_rpc("aria2.tellActive")
    
    def tell_waiting(self, offset=0, num=10):
        """Get list of waiting downloads."""
        return self.call_rpc("aria2.tellWaiting", [offset, num])
    
    def tell_stopped(self, offset=0, num=10):
        """Get list of stopped downloads."""
        return self.call_rpc("aria2.tellStopped", [offset, num])
    
    def pause_download(self, gid):
        """Pause a download by GID."""
        return self.call_rpc("aria2.pause", [gid])
    
    def resume_download(self, gid):
        """Resume a paused download by GID."""
        return self.call_rpc("aria2.unpause", [gid])
    
    def remove_download(self, gid):
        """Remove a download by GID."""
        return self.call_rpc("aria2.remove", [gid])
    
    def remove_download_result(self, gid):
        """Remove a download result by GID."""
        return self.call_rpc("aria2.removeDownloadResult", [gid])


class DownloadItemWidget(QWidget):
    """Modern browser-like download item with inline controls."""
    
    def __init__(self, download_data, rpc_client, state_manager, parent_window=None):
        super().__init__()
        self.download_data = download_data
        self.rpc_client = rpc_client
        self.state_manager = state_manager
        self.parent_window = parent_window
        self.gid = download_data.get("gid", "")
        self.init_ui()
    
    def init_ui(self):
        """Initialize the download item UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Top row: filename and status
        top_layout = QHBoxLayout()
        
        # Extract filename
        filename = self.download_data.get("fileName")
        if not filename:
            files = self.download_data.get("files", [])
            if files and len(files) > 0:
                path = files[0].get("path", "")
                if path:
                    filename = path.split("\\")[-1].split("/")[-1]
        
        if not filename:
            filename = "Unknown"
        
        # Filename label
        self.filename_label = QLabel(filename)
        self.filename_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_layout.addWidget(self.filename_label)
        
        # Status label
        status = self.download_data.get("status", "unknown")
        self.status_label = QLabel(status.capitalize())
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        top_layout.addWidget(self.status_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Progress bar
        total_length = int(self.download_data.get("totalLength", 0))
        completed_length = int(self.download_data.get("completedLength", 0))
        progress = (completed_length / total_length * 100) if total_length > 0 else 0
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(int(progress))
        self.progress_bar.setMaximumHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #333;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3add2a;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Middle row: URL and speed info
        middle_layout = QHBoxLayout()
        
        # URL label (truncated)
        url = self.download_data.get("files", [{}])[0].get("uris", [{}])[0].get("uri", "Unknown URL")
        url_label = QLabel(url[:60] + "..." if len(url) > 60 else url)
        url_label.setStyleSheet("color: #666; font-size: 11px;")
        middle_layout.addWidget(url_label)
        
        # Speed and size info
        download_speed = int(self.download_data.get("downloadSpeed", 0))
        speed_mb = download_speed / (1024 * 1024)
        size_mb = total_length / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb < 1024 else f"{size_mb/1024:.2f} GB"
        
        info_label = QLabel(f"{speed_mb:.2f} MB/s • {size_str}")
        info_label.setStyleSheet("color: #888; font-size: 11px;")
        middle_layout.addWidget(info_label)
        
        middle_layout.addStretch()
        layout.addLayout(middle_layout)
        
        # Bottom row: inline controls
        controls_layout = QHBoxLayout()
        
        # Pause/Resume button
        self.pause_resume_button = QPushButton("Pause")
        self.pause_resume_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.pause_resume_button.clicked.connect(self.toggle_pause_resume)
        controls_layout.addWidget(self.pause_resume_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        cancel_button.clicked.connect(self.cancel_download)
        controls_layout.addWidget(cancel_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #333;")
        layout.addWidget(separator)
        
        self.setLayout(layout)
    
    def toggle_pause_resume(self):
        """Toggle pause/resume for this download."""
        try:
            status = self.download_data.get("status", "")
            if status == "active":
                self.rpc_client.pause_download(self.gid)
                self.pause_resume_button.setText("Resume")
                self.state_manager.update_download_status(self.gid, "paused")
            elif status == "paused":
                self.rpc_client.resume_download(self.gid)
                self.pause_resume_button.setText("Pause")
                self.state_manager.update_download_status(self.gid, "active")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle pause/resume: {e}")
    
    def cancel_download(self):
        """Cancel this download."""
        try:
            # Remove from aria2c
            self.rpc_client.remove_download(self.gid)
            
            # Also remove the download result so it doesn't reappear in stopped list
            try:
                self.rpc_client.remove_download_result(self.gid)
            except:
                pass  # Ignore if already removed
            
            # Remove from state
            self.state_manager.remove_download(self.gid)
            
            # Remove from parent's widget tracking
            if self.parent_window and self.gid in self.parent_window.download_widgets:
                del self.parent_window.download_widgets[self.gid]
            
            # Remove widget
            self.deleteLater()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to cancel download: {e}")
    
    def update_data(self, download_data):
        """Update the download data and UI."""
        self.download_data = download_data
        
        # Update progress
        total_length = int(download_data.get("totalLength", 0))
        completed_length = int(download_data.get("completedLength", 0))
        progress = (completed_length / total_length * 100) if total_length > 0 else 0
        self.progress_bar.setValue(int(progress))
        
        # Update status
        status = download_data.get("status", "unknown")
        self.status_label.setText(status.capitalize())
        
        # Update button text
        if status == "active":
            self.pause_resume_button.setText("Pause")
        elif status == "paused":
            self.pause_resume_button.setText("Resume")
        
        # Update speed and size
        download_speed = int(download_data.get("downloadSpeed", 0))
        speed_mb = download_speed / (1024 * 1024)
        size_mb = total_length / (1024 * 1024)
        size_str = f"{size_mb:.2f} MB" if size_mb < 1024 else f"{size_mb/1024:.2f} GB"
        
        # Find and update info label
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and isinstance(item.layout(), QHBoxLayout):
                for j in range(item.layout().count()):
                    widget = item.layout().itemAt(j).widget()
                    if isinstance(widget, QLabel) and "MB/s" in widget.text():
                        widget.setText(f"{speed_mb:.2f} MB/s • {size_str}")
                        break


class DownloadManagerGUI(QMainWindow):
    """Modern browser-like GUI for Aria2 Download Manager."""
    
    def __init__(self):
        super().__init__()
        self.rpc_client = Aria2RPCClient()
        self.state_manager = DownloadState()
        self.update_manager = UpdateManager()
        self.download_widgets = {}  # Map GID to widget
        self.selected_gid = None  # Track selected download
        self.api_server = APIServer(self, port=5678)  # Flask API server
        self.init_ui()
        self.setup_tray_icon()
        self.setup_timer()
        self.restore_downloads()
        self.check_for_updates_on_startup()
        self.api_server.start()  # Start Flask API server
    
    def init_ui(self):
        """Initialize the modern browser-like user interface."""
        self.setWindowTitle("Aria2 Download Manager")
        self.setGeometry(100, 100, 1000, 700)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header = QWidget()
        header.setStyleSheet("background-color: #2c2c2c; padding: 10px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title_label = QLabel("Downloads")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Clear completed button
        clear_button = QPushButton("Clear Completed")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        clear_button.clicked.connect(self.clear_completed)
        header_layout.addWidget(clear_button)
        
        main_layout.addWidget(header)
        
        # URL input section
        url_section = QWidget()
        url_section.setStyleSheet("background-color: #1e1e1e; padding: 15px;")
        url_layout = QHBoxLayout(url_section)
        url_layout.setContentsMargins(20, 10, 20, 10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter download URL...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                padding: 10px;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3add2a;
            }
        """)
        url_layout.addWidget(self.url_input)
        
        self.add_button = QPushButton("Add Download")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #3add2a;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #32c424;
            }
        """)
        self.add_button.clicked.connect(self.add_download_from_url)
        url_layout.addWidget(self.add_button)
        
        main_layout.addWidget(url_section)
        
        # Download list with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #252525; border: none;")
        
        self.download_list = QWidget()
        self.download_list_layout = QVBoxLayout(self.download_list)
        self.download_list_layout.setContentsMargins(0, 0, 0, 0)
        self.download_list_layout.setSpacing(0)
        self.download_list_layout.addStretch()
        
        scroll_area.setWidget(self.download_list)
        main_layout.addWidget(scroll_area)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #1e1e1e; color: #888;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Connecting to aria2c...")
        
        # Create menu bar
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """Create application menu bar with update functionality."""
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #2c2c2c; color: white;")
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Add update check
        check_update_action = QAction("Check for Updates", self)
        check_update_action.triggered.connect(self.check_for_updates)
        file_menu.addAction(check_update_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.force_quit)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # GitHub action
        github_action = QAction("GitHub Repository", self)
        github_action.triggered.connect(self.open_github)
        help_menu.addAction(github_action)
    
    def apply_dark_theme(self):
        """Apply modern dark theme to the application."""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(58, 221, 42))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(58, 221, 42))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        app.setPalette(palette)
    
    def setup_tray_icon(self):
        """Setup system tray icon for notifications."""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create a simple icon using standard style
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.force_quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Double-click to show window
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
            self.activateWindow()
    
    def force_quit(self):
        """Force quit the application."""
        QApplication.instance().quit()
    
    def show_notification(self, title, message):
        """Show system tray notification."""
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, 
                                      QSystemTrayIcon.MessageIcon.Information, 3000)
    
    def setup_timer(self):
        """Setup polling timer for updating download status."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_downloads)
        self.timer.start(2000)  # Update every 2 seconds (slower for better UX)
    
    def restore_downloads(self):
        """Restore downloads from persistent state after crash."""
        saved_downloads = self.state_manager.get_downloads()
        if saved_downloads:
            self.show_notification("Aria2 Manager", 
                                 f"Restored {len(saved_downloads)} downloads from previous session")
    
    def add_download_from_url(self):
        """Add download from URL input field."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
        
        try:
            result = self.rpc_client.add_download(url)
            if result:
                self.state_manager.add_download(result, url, url.split('/')[-1], "gui")
                self.show_notification("Download Started", 
                                      f"Download added: {url.split('/')[-1]}")
                self.url_input.clear()
                self.status_bar.showMessage(f"Download added with GID: {result}")
            else:
                QMessageBox.warning(self, "Error", "Failed to add download")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add download: {e}")
    
    def update_downloads(self):
        """Update download list with current status while preserving selection."""
        try:
            # Get active and waiting downloads (but not completed/stopped)
            active_downloads = self.rpc_client.tell_active()
            waiting_downloads = self.rpc_client.tell_waiting(0, 50)
            
            self.status_bar.showMessage("Connected to aria2c")
            
            # Combine active and waiting downloads only
            all_downloads = []
            if active_downloads:
                all_downloads.extend(active_downloads)
            if waiting_downloads:
                all_downloads.extend(waiting_downloads)
            
            # Track current GIDs
            current_gids = {download.get("gid") for download in all_downloads}
            
            # Remove widgets for downloads that no longer exist
            for gid in list(self.download_widgets.keys()):
                if gid not in current_gids:
                    widget = self.download_widgets[gid]
                    widget.deleteLater()
                    del self.download_widgets[gid]
            
            # Update or create widgets for current downloads
            for download in all_downloads:
                gid = download.get("gid", "")
                
                if gid in self.download_widgets:
                    # Update existing widget
                    self.download_widgets[gid].update_data(download)
                else:
                    # Create new widget
                    widget = DownloadItemWidget(download, self.rpc_client, self.state_manager, self)
                    
                    # Insert before the stretch at the end
                    self.download_list_layout.insertWidget(
                        self.download_list_layout.count() - 1, widget)
                    
                    self.download_widgets[gid] = widget
                    
                    # Check if this is a new download from extension
                    saved_downloads = self.state_manager.get_downloads()
                    if gid not in saved_downloads:
                        # Extract filename for notification
                        filename = download.get("fileName")
                        if not filename:
                            files = download.get("files", [])
                            if files and len(files) > 0:
                                path = files[0].get("path", "")
                                if path:
                                    filename = path.split("\\")[-1].split("/")[-1]
                        
                        if not filename:
                            filename = "Unknown file"
                        
                        # Add to state with source tracking
                        url = download.get("files", [{}])[0].get("uris", [{}])[0].get("uri", "")
                        
                        # Simple heuristic: if download exists in saved state, preserve its source
                        # Otherwise, assume it's from GUI (extension would have added it to state first)
                        if gid in saved_downloads:
                            download_source = saved_downloads[gid].get("source", "gui")
                        else:
                            download_source = "gui"
                        
                        self.state_manager.add_download(gid, url, filename, download_source)
                        
                        # Show notification based on source
                        if download_source == "extension":
                            self.show_notification("Download Started (Browser)", 
                                                  f"Browser started download: {filename}")
                        else:
                            self.show_notification("Download Started", 
                                                  f"Download added: {filename}")
                
                # Update state
                status = download.get("status", "unknown")
                total_length = int(download.get("totalLength", 0))
                completed_length = int(download.get("completedLength", 0))
                progress = (completed_length / total_length * 100) if total_length > 0 else 0
                self.state_manager.update_download_status(gid, status, progress)
                
                # Auto-remove completed downloads from aria2c to prevent reappearing
                if status == "complete":
                    try:
                        self.rpc_client.remove_download_result(gid)
                        if gid in self.download_widgets:
                            self.download_widgets[gid].deleteLater()
                            del self.download_widgets[gid]
                    except:
                        pass  # Ignore errors during auto-cleanup
                
        except ConnectionError:
            self.status_bar.showMessage("Disconnected from aria2c")
        except Exception as e:
            self.status_bar.showMessage(f"Error: {str(e)}")
    
    def clear_completed(self):
        """Clear completed downloads from the list and aria2c."""
        try:
            stopped_downloads = self.rpc_client.tell_stopped(0, 100)
            if stopped_downloads:
                cleared_count = 0
                for download in stopped_downloads:
                    gid = download.get("gid")
                    if gid:
                        try:
                            # Remove the download result from aria2c so it won't reappear
                            self.rpc_client.remove_download_result(gid)
                            
                            # Remove widget if it exists
                            if gid in self.download_widgets:
                                self.download_widgets[gid].deleteLater()
                                del self.download_widgets[gid]
                            
                            # Remove from state
                            self.state_manager.remove_download(gid)
                            cleared_count += 1
                        except Exception as e:
                            print(f"Error clearing download {gid}: {e}")
                            continue
                
                if cleared_count > 0:
                    self.status_bar.showMessage(f"Cleared {cleared_count} completed downloads")
                else:
                    self.status_bar.showMessage("No completed downloads to clear")
            else:
                self.status_bar.showMessage("No completed downloads to clear")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear downloads: {e}")
    
    def check_for_updates_on_startup(self):
        """Check for updates when application starts."""
        try:
            update_info = self.update_manager.check_for_updates()
            if update_info.get("has_update"):
                self.show_notification("Update Available", 
                                      f"New version {update_info['latest_version']} available")
                self.status_bar.showMessage(f"Update available: v{update_info['latest_version']}")
        except Exception as e:
            print(f"Error checking for updates on startup: {e}")
    
    def check_for_updates(self):
        """Manually check for updates and show dialog."""
        try:
            update_info = self.update_manager.check_for_updates()
            
            if update_info.get("error"):
                QMessageBox.warning(self, "Update Check Failed", 
                                f"Could not check for updates: {update_info['error']}")
                return
            
            if update_info.get("has_update"):
                # Show update available dialog
                reply = QMessageBox.question(
                    self,
                    "Update Available",
                    f"A new version ({update_info['latest_version']}) is available!\n\n"
                    f"Current version: {update_info['current_version']}\n"
                    f"Latest version: {update_info['latest_version']}\n\n"
                    f"Would you like to download the update?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.update_manager.open_download_page()
                    self.show_notification("Update Download", 
                                          "Opening download page in browser")
            else:
                QMessageBox.information(self, "No Updates", 
                                      f"You are running the latest version ({update_info['latest_version']})")
                
        except Exception as e:
            QMessageBox.critical(self, "Update Check Error", f"Failed to check for updates: {e}")
    
    def show_about(self):
        """Show about dialog with version information."""
        about_text = (
            "Aria2 Download Manager\n\n"
            "Version: 1.0.0\n\n"
            "A modern download manager system built around aria2c with "
            "browser extension integration and PyQt6 GUI.\n\n"
            "Features:\n"
            "• Multi-threaded downloads (16 connections, 16 splits)\n"
            "• Browser download interception\n"
            "• Modern PyQt6 GUI with dark theme\n"
            "• System tray integration\n"
            "• Crash resistance with persistent state\n"
            "• Real-time progress monitoring\n"
            "• Inline download controls\n\n"
            "License: MIT License\n"
            "GitHub: https://github.com/Entity6814/Aria2c-Manager"
        )
        
        QMessageBox.about(self, "About Aria2 Manager", about_text)
    
    def open_github(self):
        """Open GitHub repository in browser."""
        webbrowser.open("https://github.com/Entity6814/Aria2c-Manager")
    
    def closeEvent(self, event):
        """Handle window close event - minimize to tray instead of closing."""
        event.ignore()
        self.hide()
        self.show_notification("Aria2 Manager", "Application minimized to system tray")
    
    def changeEvent(self, event):
        """Handle window state changes - minimize to tray."""
        if event.type() == QEvent.Type.WindowStateChange:
            if self.isMinimized():
                event.ignore()
                self.hide()
                self.show_notification("Aria2 Manager", "Application minimized to system tray")


def main():
    """Main entry point for the application."""
    # Check if another instance is already running
    if check_single_instance():
        print("[INFO] Another instance is already running")
        # Try to show the existing window
        try:
            requests.post("http://127.0.0.1:5678/show", timeout=2)
            print("[INFO] Brought existing window to front")
        except:
            print("[WARNING] Could not show existing window")
        sys.exit(0)
    
    # Check if port is available
    if is_port_in_use(5678):
        print("[ERROR] Port 5678 is already in use but API not responding")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    
    # Don't quit when last window is closed (since we run in tray)
    app.setQuitOnLastWindowClosed(False)
    
    window = DownloadManagerGUI()
    
    # Check if --minimized flag is present to start in tray
    if "--minimized" in sys.argv or "-m" in sys.argv:
        window.hide()
        window.show_notification("Aria2 Manager", "Application started in system tray")
    else:
        window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
