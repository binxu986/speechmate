import { app, BrowserWindow, globalShortcut, Tray, Menu, nativeImage, ipcMain, clipboard } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import log from 'electron-log';

log.transports.file.level = 'info';
log.info('SpeechMate starting...');

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let isRecording = false;

interface Config {
  base_url: string;
  api_key: string;
  hotkey_asr: string;
  hotkey_translate_zh_en: string;
  hotkey_translate_en_zh: string;
}

let config: Config = {
  base_url: 'http://localhost:3456',
  api_key: '',
  hotkey_asr: 'alt',
  hotkey_translate_zh_en: 'shift',
  hotkey_translate_en_zh: 'shift+a'
};

function loadConfig(): void {
  const configPath = path.join(app.getPath('userData'), 'config.json');
  if (fs.existsSync(configPath)) {
    try {
      const loaded = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      config = { ...config, ...loaded };
    } catch (e) {
      log.error('Failed to load config:', e);
    }
  }
}

function saveConfig(): void {
  const configPath = path.join(app.getPath('userData'), 'config.json');
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 560,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    resizable: false,
    show: false,
    title: 'SpeechMate'
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('close', (event) => {
    event.preventDefault();
    mainWindow?.hide();
  });
}

function createTray(): void {
  const icon = nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKLSURBVFiFxZdLiFRnFMd/595kRjOSSZqkTWPa1tZWW9sKVi0uXIiIcBFBXAiCcCHiRrwQEbyJCyFeBBdCcCGEiItwIYSL4EIIEQTxImqtVq3W2mrbNjOZyUzmde6FmWQyk5lJ4g/8wH33nv/7f+c7994Buvw3/gfABDAAnAPuALuBBiClXP2Y+0MYeA84BQwAD4EB4CQwAkwBd4DfgRvARaAX+L4e8GqMdwB3gMvAJHALKAGHgDNAJyAB3AKmgOvAZqAT+K4G8GqMDwEPgAvAJHAJKAMHgRNAOaAB3ALKwCVgPdABfFsD+GqMDwJPgAvAJHAJKAMHgRNAKTAK3ATKwEVgHdAO/FAD+NUMPwQ+AyeBMnAROAucBEqBCeAmUAouAGuA9kAD+NUM/w14DJwESoFF4BZwHCgBxoAbQDdwDVgDtAcf1AC+NsJ/Ah4CJ4BvwDXgOHAcKAa2AdcBb8BVoA3YCbQFGsA3RvhP4AFwHPgGXAOOA8eBYmAbsAl4C3wCrgFtgY5AA/jGCP8JPACOA9+Aa8Bx4DhQDGwDNgFvge+AtkB7oAH8d4TvxvhP4D5wDPgGXAOOA8eBYmAbsAl4C3wBqgPdgQbwnzH+E7gfOA58A64Bx4HjQDGwDdgEvAW+A9WC7kAD+M8Y/wncB44D34BrwHHgOFAMbAM2AW+B70C1oCfQAP4b4z+B+8Fx4BtwDTgOHAeKgW3AJuAt8B2oFvQEGsB/Y/w/AH8BLl9M+Q2tJZQAAAAASUVORK5CYII=');
  
  tray = new Tray(icon);
  
  const contextMenu = Menu.buildFromTemplate([
    { label: '显示主界面', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: '设置', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: '退出', click: () => { mainWindow?.destroy(); app.quit(); } }
  ]);
  
  tray.setToolTip('SpeechMate');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => mainWindow?.show());
}

function registerHotkeys(): void {
  globalShortcut.unregisterAll();
  
  globalShortcut.register('Alt', () => {
    if (!isRecording) {
      isRecording = true;
      mainWindow?.webContents.send('recording-status', true);
      log.info('Recording started - ASR');
    }
  });
  
  globalShortcut.register('Shift', () => {
    if (!isRecording) {
      isRecording = true;
      mainWindow?.webContents.send('recording-status', true);
      log.info('Recording started - Translate ZH->EN');
    }
  });
}

app.whenReady().then(() => {
  loadConfig();
  createWindow();
  createTray();
  registerHotkeys();
  mainWindow?.show();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

ipcMain.handle('get-config', () => config);
ipcMain.handle('save-config', (_, newConfig) => {
  config = { ...config, ...newConfig };
  saveConfig();
  return true;
});

ipcMain.handle('set-recording', (_, status: boolean) => {
  isRecording = status;
  mainWindow?.webContents.send('recording-status', status);
});

ipcMain.handle('write-clipboard', (_, text: string) => {
  clipboard.writeText(text);
  log.info('Written to clipboard:', text);
});
