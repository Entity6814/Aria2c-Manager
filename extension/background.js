// Background service worker for Aria2 Download Manager
// Intercepts browser downloads and forwards them to aria2c daemon
// Features: download location handling, notifications, source tracking, app launching

const RPC_SECRET = "MyCustomSecret123";
const RPC_URL = "http://localhost:6800/jsonrpc";

// Check if aria2c daemon is running
async function checkAria2Connection() {
  try {
    const response = await fetch(RPC_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now().toString(),
        method: "aria2.getVersion",
        params: [`token:${RPC_SECRET}`]
      })
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Try to launch the desktop app
// Uses Flask API if available, falls back to notification
async function launchDesktopApp() {
  const API_URL = "http://127.0.0.1:5678";
  
  try {
    // Check if Flask API is running
    const response = await fetch(`${API_URL}/status`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });
    
    if (response.ok) {
      // API is running, try to show the window
      const showResponse = await fetch(`${API_URL}/show`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (showResponse.ok) {
        return { success: true, message: "Desktop app shown" };
      } else {
        return { success: false, message: "Failed to show window" };
      }
    } else {
      throw new Error("API not responding");
    }
  } catch (error) {
    // API not available, show notification
    showNotification(
      "Aria2 Manager Not Running",
      "Please start the Aria2 Manager desktop app. Open Start Menu and click 'Aria2c Manager' or run: %USERPROFILE%\\Aria2cManager\\start_manager.bat"
    );
    return { success: false, message: "Desktop app is not running" };
  }
}

// Start aria2c daemon via Flask API
async function startDaemon() {
  const API_URL = "http://127.0.0.1:5678";
  
  try {
    const response = await fetch(`${API_URL}/start-daemon`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    
    const result = await response.json();
    if (result.success) {
      showNotification("Daemon Started", "aria2c daemon started successfully");
      return { success: true };
    } else {
      throw new Error(result.error || "Failed to start daemon");
    }
  } catch (error) {
    showNotification("Daemon Failed", "Could not start aria2c daemon");
    return { success: false, error: error.message };
  }
}

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "launchApp") {
    launchDesktopApp().then(sendResponse);
    return true; // Keep message channel open for async response
  }
  
  if (request.action === "checkConnection") {
    checkAria2Connection().then(sendResponse);
    return true;
  }

  if (request.action === "startDaemon") {
    startDaemon().then(sendResponse);
    return true;
  }
});

// Get user-configured download directory from settings
async function getDownloadDirectory() {
  try {
    const result = await new Promise((resolve) => {
      chrome.storage.local.get(['downloadDir'], (data) => {
        resolve(data);
      });
    });
    
    const downloadDir = result.downloadDir;
    
    // If user configured a directory, clean it up
    if (downloadDir) {
      // Remove any trailing slashes
      return downloadDir.replace(/[\/\\]+$/, '');
    }
    
    return ""; // Empty means use aria2c default
  } catch (error) {
    console.log("Could not get download directory from settings:", error);
    return "";
  }
}

// Get advanced settings
async function getAdvancedSettings() {
  try {
    const result = await new Promise((resolve) => {
      chrome.storage.local.get(['downloadDir', 'connections', 'splits'], (data) => {
        resolve(data);
      });
    });

    return {
      downloadDir: result.downloadDir || "",
      connections: result.connections || 16,
      splits: result.splits || 16
    };
  } catch (error) {
    console.log("Could not get advanced settings:", error);
    return {
      downloadDir: "",
      connections: 16,
      splits: 16
    };
  }
}

// Show Chrome notification
function showNotification(title, message) {
  if (chrome.notifications) {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icon.png",
      title: title,
      message: message,
      priority: 2
    }, (notificationId) => {
      if (chrome.runtime.lastError) {
        console.log("Notification error:", chrome.runtime.lastError);
      }
    });
  }
}

// Listen for download creation events
chrome.downloads.onCreated.addListener(async (downloadItem) => {
  console.log("Download intercepted:", downloadItem);
  
  try {
    // Cancel the native browser download immediately
    await chrome.downloads.cancel(downloadItem.id);
    console.log("Native download cancelled:", downloadItem.id);
    
    // Clear the download from browser history
    await chrome.downloads.erase({ id: downloadItem.id });
    console.log("Download removed from history:", downloadItem.id);
    
    // Extract download information
    const url = downloadItem.url;
    
    // Get filename from download item (browser determines this best)
    let filename = downloadItem.filename;
    
    // If filename is not available yet, try to determine it
    if (!filename) {
      // Extract from URL
      filename = downloadItem.url.split('/').pop().split('?')[0];
      // Decode URL encoding
      try {
        filename = decodeURIComponent(filename);
      } catch (e) {
        // If decoding fails, use as-is
      }
      // Only remove problematic characters, preserve file extension
      filename = filename.replace(/[<>:"/\\|?*]/g, '_');
    }
    
    // Extract just the filename if it's a full path
    if (filename.includes('/') || filename.includes('\\')) {
      filename = filename.split(/[\/\\]/).pop();
    }
    
    // Ensure we have a file extension
    if (!filename.includes('.')) {
      // Try to get extension from URL
      const urlParts = downloadItem.url.split('.');
      if (urlParts.length > 1) {
        const extension = urlParts.pop().split('?')[0].split('#')[0];
        if (extension.length <= 5 && /^[a-zA-Z0-9]+$/.test(extension)) {
          filename += '.' + extension;
        }
      }
    }
    
    const referer = downloadItem.referrer || "";
    
    // Get user-configured download directory and advanced settings
    const settings = await getAdvancedSettings();
    
    // Construct JSON-RPC 2.0 payload for aria2.addUri
    const options = {
      referer: referer,
      "max-connection-per-server": settings.connections.toString(),
      split: settings.splits.toString(),
      continue: "true",
      "check-certificate": "false",
      timeout: "60",
      "retry-wait": "5",
      "max-tries": "5"
    };
    
    // Only set download directory if user configured one
    if (settings.downloadDir) {
      options.dir = settings.downloadDir;
      console.log("Using configured download directory:", settings.downloadDir);
    } else {
      console.log("Using aria2c default download directory");
    }
    
    // Only set output filename if we have a good one with extension
    if (filename && filename.includes('.')) {
      options.out = filename;
    }
    
    const rpcPayload = {
      jsonrpc: "2.0",
      id: Date.now().toString(),
      method: "aria2.addUri",
      params: [
        `token:${RPC_SECRET}`,
        [url],
        options
      ]
    };
    
    // Send RPC request to aria2c daemon
    const response = await fetch(RPC_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(rpcPayload)
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log("Successfully added to aria2:", result);
      
      // Show Chrome notification
      showNotification(
        "Download Started",
        `Downloading: ${filename}`
      );
      
      // Store download info for crash resistance
      if (result.result) {
        const downloadInfo = {
          gid: result.result,
          url: url,
          filename: filename,
          source: "extension",
          downloadDir: downloadDir,
          timestamp: Date.now()
        };
        
        // Store in chrome.storage for persistence
        chrome.storage.local.get(['downloads'], (result) => {
          const downloads = result.downloads || {};
          downloads[downloadInfo.gid] = downloadInfo;
          chrome.storage.local.set({ downloads: downloads });
        });
      }
    } else {
      console.error("Failed to add to aria2:", response.status, response.statusText);
      showNotification(
        "Download Failed",
        "Could not add download to aria2c. Make sure the daemon is running."
      );
    }
    
  } catch (error) {
    console.error("Error forwarding download to aria2:", error);
    // Handle network errors if aria2c RPC server is unreachable
    showNotification(
      "Connection Error",
      "Could not connect to aria2c daemon. Make sure it's running on port 6800."
    );
  }
});

// Restore downloads on extension startup (for crash resistance)
chrome.runtime.onStartup.addListener(() => {
  console.log("Extension started, checking for interrupted downloads...");
  // Could implement logic to check aria2c for active downloads
  // and notify the user about ongoing downloads
});

// Handle extension installation/update
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    showNotification(
      "Aria2 Manager Installed",
      "Browser downloads will now be intercepted by aria2c"
    );
  }
});
