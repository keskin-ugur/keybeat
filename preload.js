const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    onGlobalKeyDown: (callback) => ipcRenderer.on('global-keydown', (event, value) => callback(value))
});
