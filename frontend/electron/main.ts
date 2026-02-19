import { app, BrowserWindow, ipcMain, shell, Menu } from 'electron';
import path from 'path';
import { spawn, ChildProcess } from 'child_process';
import os from 'os';
import fs from 'fs';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

// Determine backend executable path
const isDev = !app.isPackaged;
const backendPath = isDev
    ? path.join(__dirname, '../../backend/venv/Scripts/python.exe') // Run via python in dev
    : path.join(process.resourcesPath, 'backend/backend_main.exe'); // Run via exe in prod

const backendArgs = isDev
    ? ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8001']
    : [];

function startBackend() {
    console.log(`Starting backend from: ${backendPath}`);

    if (isDev) {
        // In dev, we execute python with module args, cwd must be backend root
        backendProcess = spawn(backendPath, backendArgs, {
            cwd: path.join(__dirname, '../../backend'),
            stdio: 'inherit', // Pipe stdout/stderr to parent
            windowsHide: true // Hide console window on Windows
        });
    } else {
        // In prod, just execute the exe
        backendProcess = spawn(backendPath, [], {
            stdio: 'inherit',
            windowsHide: true
        });
    }

    backendProcess.on('error', (err) => {
        console.error('Failed to start backend:', err);
    });

    backendProcess.on('exit', (code, signal) => {
        console.log(`Backend exited with code ${code} and signal ${signal}`);
    });
}

function stopBackend() {
    if (backendProcess) {
        console.log('Stopping backend...');
        backendProcess.kill();
        backendProcess = null;
    }
}

// Settings Persistence
const settingsPath = path.join(app.getPath('userData'), 'settings.json');

// Default settings
const defaultSettings = {
    windowBounds: { width: 1000, height: 700 },
    customPaths: [] as string[],
    isOverlay: false
};

function loadSettings() {
    try {
        console.log(`Loading settings from: ${settingsPath}`);
        if (fs.existsSync(settingsPath)) {
            const data = fs.readFileSync(settingsPath, 'utf-8');
            return { ...defaultSettings, ...JSON.parse(data) };
        } else {
            console.log("Settings file not found, creating default settings");
            saveSettings(defaultSettings);
        }
    } catch (e) {
        console.error("Failed to load settings", e);
    }
    return defaultSettings;
}

function saveSettings(settings: any) {
    try {
        const dir = path.dirname(settingsPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
        console.log("Settings saved successfully");
    } catch (e) {
        console.error("Failed to save settings", e);
    }
}

let currentSettings = loadSettings();

function createWindow() {
    const { width, height } = currentSettings.windowBounds || defaultSettings.windowBounds;

    mainWindow = new BrowserWindow({
        width: width,
        height: height,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
        minWidth: 500,
        minHeight: 290,
    });

    // Remove the default menu bar (File, Edit, etc.)
    Menu.setApplicationMenu(null);

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    // Save window size on resize
    mainWindow.on('resize', () => {
        if (!mainWindow) return;
        const [w, h] = mainWindow.getSize();
        currentSettings.windowBounds = { width: w, height: h };
        saveSettings(currentSettings);
    });
}

// IPC Handlers for Settings
ipcMain.handle('get-settings', () => {
    return currentSettings;
});

ipcMain.handle('save-settings', (event, newSettings) => {
    currentSettings = { ...currentSettings, ...newSettings };
    saveSettings(currentSettings);
    return true;
});

ipcMain.handle('open-settings-folder', () => {
    shell.showItemInFolder(settingsPath);
    return true;
});

ipcMain.handle('toggle-overlay', (event, enable: boolean) => {
    if (!mainWindow) return;
    if (enable) {
        mainWindow.setAlwaysOnTop(true, 'screen-saver');
        mainWindow.setOpacity(0.8);
    } else {
        mainWindow.setAlwaysOnTop(false);
        mainWindow.setOpacity(1.0);
    }
});


app.whenReady().then(() => {
    startBackend();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    stopBackend();
});
