// Popup script for Aria2 Download Manager extension
// Manages downloads from browser extension popup

const RPC_SECRET = "MyCustomSecret123";
const RPC_URL = "http://localhost:6800/jsonrpc";

let isPolling = false;
let pollInterval = null;

// RPC call helper
async function rpcCall(method, params = []) {
    try {
        const response = await fetch(RPC_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                jsonrpc: "2.0",
                id: Date.now().toString(),
                method: method,
                params: [`token:${RPC_SECRET}`, ...params]
            })
        });

        if (!response.ok) {
            throw new Error(`RPC error: ${response.status}`);
        }

        const result = await response.json();
        if (result.error) {
            throw new Error(result.error.message);
        }

        return result.result;
    } catch (error) {
        console.error("RPC call failed:", error);
        throw error;
    }
}

// Check if aria2c is running
async function checkConnection() {
    try {
        await rpcCall("aria2.getVersion");
        return true;
    } catch (error) {
        return false;
    }
}

// Format bytes to human readable
function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Format speed
function formatSpeed(bytesPerSecond) {
    return formatBytes(bytesPerSecond) + "/s";
}

// Get download status from aria2c
async function getDownloads() {
    try {
        const [active, waiting, stopped] = await Promise.all([
            rpcCall("aria2.tellActive"),
            rpcCall("aria2.tellWaiting", [0, 100]),
            rpcCall("aria2.tellStopped", [0, 100])
        ]);

        return {
            active: active || [],
            waiting: waiting || [],
            stopped: stopped || []
        };
    } catch (error) {
        console.error("Failed to get downloads:", error);
        return { active: [], waiting: [], stopped: [] };
    }
}

// Get filename from download item
function getFilename(download) {
    if (download.files && download.files.length > 0) {
        const path = download.files[0].path || download.files[0].uris[0]?.uri;
        if (path) {
            return path.split(/[\/\\]/).pop();
        }
    }
    return download.bittorrent?.info?.name || "Unknown";
}

// Render download card
function renderDownloadCard(download, status) {
    const filename = getFilename(download);
    const totalLength = parseInt(download.totalLength) || 0;
    const completedLength = parseInt(download.completedLength) || 0;
    const progress = totalLength > 0 ? (completedLength / totalLength * 100).toFixed(1) : 0;
    const downloadSpeed = parseInt(download.downloadSpeed) || 0;
    const gid = download.gid;

    let statusClass = "active";
    let statusText = "Active";

    // Check actual download status first (paused can be in any list)
    if (download.status === "paused") {
        statusClass = "paused";
        statusText = "Paused";
    } else if (status === "waiting") {
        statusClass = "waiting";
        statusText = "Waiting";
    } else if (status === "stopped") {
        if (download.errorCode && download.errorCode !== "0") {
            statusClass = "error";
            statusText = "Error";
        } else {
            statusClass = "completed";
            statusText = "Completed";
        }
    }

    let controlsHtml = "";
    // Check actual download status first (paused can be in any list)
    if (download.status === "paused") {
        controlsHtml = `
            <button class="control-btn resume-btn" data-action="resume" data-gid="${gid}">Resume</button>
            <button class="control-btn remove-btn" data-action="remove" data-gid="${gid}">Remove</button>
        `;
    } else if (status === "active" || status === "waiting") {
        controlsHtml = `
            <button class="control-btn pause-btn" data-action="pause" data-gid="${gid}">Pause</button>
            <button class="control-btn remove-btn" data-action="remove" data-gid="${gid}">Remove</button>
        `;
    } else if (status === "stopped") {
        controlsHtml = `
            <button class="control-btn remove-btn" data-action="remove" data-gid="${gid}">Remove</button>
        `;
    }

    return `
        <div class="download-card" data-gid="${gid}">
            <div class="download-header">
                <div class="filename">${filename}</div>
                <span class="status ${statusClass}">${statusText}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" data-progress="${progress}"></div>
            </div>
            <div class="download-info">
                <span>${formatBytes(completedLength)} / ${formatBytes(totalLength)}</span>
                <span>${downloadSpeed > 0 ? formatSpeed(downloadSpeed) : progress + "%"}</span>
            </div>
            <div class="controls">
                ${controlsHtml}
            </div>
        </div>
    `;
}

// Render all downloads
async function renderDownloads() {
    const downloadsSection = document.getElementById("downloadsSection");
    const statusBadge = document.getElementById("statusBadge");
    const startDaemonBtn = document.getElementById("startDaemonBtn");

    const isConnected = await checkConnection();

    if (isConnected) {
        statusBadge.textContent = "Connected";
        statusBadge.classList.remove("disconnected");
        startDaemonBtn.style.display = "none"; // Hide start daemon button when connected
    } else {
        statusBadge.textContent = "Disconnected";
        statusBadge.classList.add("disconnected");
        startDaemonBtn.style.display = "block"; // Show start daemon button when disconnected
    }

    if (!isConnected) {
        downloadsSection.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⚠️</div>
                <div class="empty-state-text">Cannot connect to aria2c daemon</div>
                <div class="empty-state-text empty-state-subtext">Make sure the desktop app is running</div>
            </div>
        `;
        startDaemonBtn.style.display = "block"; // Show start daemon button
        return;
    }

    const downloads = await getDownloads();
    const allDownloads = [
        ...downloads.active.map(d => ({ ...d, listStatus: "active" })),
        ...downloads.waiting.map(d => ({ ...d, listStatus: "waiting" })),
        ...downloads.stopped.map(d => ({ ...d, listStatus: "stopped" }))
    ];

    if (allDownloads.length === 0) {
        downloadsSection.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📥</div>
                <div class="empty-state-text">No downloads yet</div>
            </div>
        `;
        return;
    }

    downloadsSection.innerHTML = allDownloads
        .map(d => renderDownloadCard(d, d.listStatus))
        .join("");

    // Set progress bar widths after HTML is inserted (avoids inline styles)
    document.querySelectorAll(".progress-fill").forEach(el => {
        const progress = el.dataset.progress;
        if (progress) {
            el.style.width = progress + "%";
        }
    });
}

// Pause download
async function pauseDownload(gid) {
    try {
        await rpcCall("aria2.pause", [gid]);
        await renderDownloads();
    } catch (error) {
        console.error("Failed to pause download:", error);
        alert("Failed to pause download: " + error.message);
    }
}

// Resume download
async function resumeDownload(gid) {
    try {
        await rpcCall("aria2.unpause", [gid]);
        await renderDownloads();
    } catch (error) {
        console.error("Failed to resume download:", error);
        alert("Failed to resume download: " + error.message);
    }
}

// Remove download
async function removeDownload(gid) {
    if (!confirm("Are you sure you want to remove this download?")) {
        return;
    }

    try {
        // Try to remove from active/waiting first
        try {
            await rpcCall("aria2.remove", [gid]);
        } catch (removeError) {
            // If remove fails, it might be stopped - try removing from history
            console.log("Remove failed, trying to remove from history:", removeError);
            await rpcCall("aria2.removeDownloadResult", [gid]);
        }
        await renderDownloads();
    } catch (error) {
        console.error("Failed to remove download:", error);
        alert("Failed to remove download: " + error.message);
    }
}

// Add download from URL
async function addDownload() {
    const urlInput = document.getElementById("urlInput");
    const url = urlInput.value.trim();

    if (!url) {
        alert("Please enter a URL");
        return;
    }

    const addBtn = document.getElementById("addBtn");
    addBtn.disabled = true;
    addBtn.textContent = "Adding...";

    try {
        // Get advanced settings
        const settings = await getAdvancedSettings();
        
        const options = {
            "max-connection-per-server": settings.connections.toString(),
            split: settings.splits.toString(),
            continue: "true",
            "check-certificate": "false"
        };

        // Only set download directory if configured
        if (settings.downloadDir) {
            options.dir = settings.downloadDir;
        }

        const result = await rpcCall("aria2.addUri", [[url], options]);
        console.log("Download added:", result);

        urlInput.value = "";
        await renderDownloads();
    } catch (error) {
        console.error("Failed to add download:", error);
        alert("Failed to add download: " + error.message);
    } finally {
        addBtn.disabled = false;
        addBtn.textContent = "Add Download";
    }
}

// Get advanced settings from storage
async function getAdvancedSettings() {
    try {
        const result = await new Promise((resolve) => {
            chrome.storage.local.get(['downloadDir', 'connections', 'splits', 'advancedMode'], (data) => {
                resolve(data);
            });
        });

        return {
            downloadDir: result.downloadDir || "",
            connections: result.connections || 16,
            splits: result.splits || 16,
            advancedMode: result.advancedMode || false
        };
    } catch (error) {
        console.error("Failed to get settings:", error);
        return {
            downloadDir: "",
            connections: 16,
            splits: 16,
            advancedMode: false
        };
    }
}

// Save advanced settings
async function saveAdvancedSettings() {
    const downloadDir = document.getElementById("downloadDirInput").value.trim();
    const connections = parseInt(document.getElementById("connectionsInput").value) || 16;
    const splits = parseInt(document.getElementById("splitsInput").value) || 16;

    // Validate ranges
    const validConnections = Math.max(1, Math.min(32, connections));
    const validSplits = Math.max(1, Math.min(32, splits));

    const settings = {
        downloadDir: downloadDir,
        connections: validConnections,
        splits: validSplits
    };

    chrome.storage.local.set(settings, () => {
        if (chrome.runtime.lastError) {
            console.error("Failed to save settings:", chrome.runtime.lastError);
            alert("Failed to save settings");
        } else {
            alert("Settings saved successfully!");
        }
    });
}

// Toggle advanced mode
function toggleAdvancedMode() {
    const toggleSwitch = document.getElementById("toggleSwitch");
    const advancedSettings = document.getElementById("advancedSettings");
    const isActive = toggleSwitch.classList.contains("active");

    if (isActive) {
        toggleSwitch.classList.remove("active");
        advancedSettings.classList.remove("visible");
        chrome.storage.local.set({ advancedMode: false });
    } else {
        toggleSwitch.classList.add("active");
        advancedSettings.classList.add("visible");
        chrome.storage.local.set({ advancedMode: true });
    }
}

// Load advanced settings into inputs
async function loadAdvancedSettings() {
    const settings = await getAdvancedSettings();

    // Update toggle state
    const toggleSwitch = document.getElementById("toggleSwitch");
    const advancedSettings = document.getElementById("advancedSettings");
    
    if (settings.advancedMode) {
        toggleSwitch.classList.add("active");
        advancedSettings.classList.add("visible");
    }

    // Update input values
    document.getElementById("downloadDirInput").value = settings.downloadDir;
    document.getElementById("connectionsInput").value = settings.connections;
    document.getElementById("splitsInput").value = settings.splits;
}

// Launch desktop app
function launchApp() {
  // Send message to background script to launch the app
  chrome.runtime.sendMessage({ action: "launchApp" }, (response) => {
    if (chrome.runtime.lastError) {
      console.error("Failed to launch app:", chrome.runtime.lastError);
      alert("Failed to launch desktop app. Please start it manually.");
    } else {
      if (response && response.success) {
        alert("Desktop app is now visible");
      } else {
        alert(response.message || "Failed to launch desktop app");
      }
    }
  });
}

// Start aria2c daemon
function startDaemon() {
  chrome.runtime.sendMessage({ action: "startDaemon" }, (response) => {
    if (chrome.runtime.lastError) {
      console.error("Failed to start daemon:", chrome.runtime.lastError);
      alert("Failed to start daemon. Please start it manually.");
    } else {
      if (response && response.success) {
        alert("Daemon started successfully");
        renderDownloads(); // Refresh to show connection
      } else {
        alert(response.error || "Failed to start daemon");
      }
    }
  });
}

// Start polling
function startPolling() {
    if (isPolling) return;
    isPolling = true;

    renderDownloads();
    pollInterval = setInterval(renderDownloads, 2000);
}

// Stop polling
function stopPolling() {
    isPolling = false;
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Event listeners
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("addBtn").addEventListener("click", addDownload);
    document.getElementById("urlInput").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            addDownload();
        }
    });
    document.getElementById("refreshBtn").addEventListener("click", renderDownloads);
    document.getElementById("launchAppBtn").addEventListener("click", launchApp);
    document.getElementById("advancedToggle").addEventListener("click", toggleAdvancedMode);
    document.getElementById("saveSettingsBtn").addEventListener("click", saveAdvancedSettings);
    document.getElementById("startDaemonBtn").addEventListener("click", startDaemon);

    // Event delegation for dynamically created control buttons
    document.getElementById("downloadsSection").addEventListener("click", async (e) => {
        const button = e.target.closest(".control-btn");
        if (!button) return;

        const action = button.dataset.action;
        const gid = button.dataset.gid;

        if (action === "pause") {
            await pauseDownload(gid);
        } else if (action === "resume") {
            await resumeDownload(gid);
        } else if (action === "remove") {
            await removeDownload(gid);
        }
    });

    // Load advanced settings
    loadAdvancedSettings();

    // Start polling when popup opens
    startPolling();
});

// Stop polling when popup closes
window.addEventListener("unload", () => {
    stopPolling();
});
