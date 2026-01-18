const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');
const { uIOhook, UiohookKey } = require('uiohook-napi');

let mainWindow;
let tray = null;
let isQuitting = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 450,
    height: 550,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      backgroundThrottling: false 
    }
  });

  mainWindow.loadFile('index.html');

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle minimize to background (Tray behavior)
  mainWindow.on('minimize', (event) => {
    event.preventDefault();
    mainWindow.hide();
  });

  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
    return false;
  });
}

function initHooks() {
  uIOhook.on('keydown', (e) => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('global-keydown', e);
    }
  });

  uIOhook.start();
}

app.whenReady().then(() => {
  createWindow();
  initHooks();
  
  // NOTE: For a real tray icon, place an 'icon.png' in the root or assets folder and uncomment:
  // tray = new Tray(path.join(__dirname, 'icon.png'));
  // const contextMenu = Menu.buildFromTemplate([
  //   { label: 'Show App', click: () => mainWindow.show() },
  //   { label: 'Quit', click: () => { isQuitting = true; app.quit(); } }
  // ]);
  // tray.setToolTip('KeyBeat');
  // tray.setContextMenu(contextMenu);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
    else mainWindow.show();
  });
});

app.on('before-quit', () => {
  isQuitting = true;
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
