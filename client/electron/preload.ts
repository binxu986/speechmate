import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config: any) => ipcRenderer.invoke('save-config', config),
  setRecording: (status: boolean) => ipcRenderer.invoke('set-recording', status),
  writeClipboard: (text: string) => ipcRenderer.invoke('write-clipboard', text),
  onRecordingStatus: (callback: (status: boolean) => void) => {
    ipcRenderer.on('recording-status', (_, status) => callback(status));
  }
});
