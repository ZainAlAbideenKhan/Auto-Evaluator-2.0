const {
  app,
  BrowserWindow,
  globalShortcut,
  ipcMain,
  dialog,
} = require("electron");
const { globalAgent } = require("http");
const path = require("path");

// SECTION - HANDLING MAIN THREAD

function createWindow() {
  const win = new BrowserWindow({
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  win.loadFile(path.join(__dirname, "index.html"));
  // shortcut to refresh
  globalShortcut.register("Ctrl+R", () => {
    win.reload();
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on("window-all-closed", function () {
    if (process.platform !== "win32") app.quit();
  });
});

// IPC FORM INDEX
ipcMain.on("invalid-username", (event, message) => {
  dialog.showMessageBox({
    type: "error",
    title: "Invalid Username",
    message: message,
    buttons: ["OK"],
  });
});

ipcMain.on("invalid-password", (event, message) => {
  dialog.showMessageBox({
    type: "error",
    title: "Invalid Password",
    message: message,
    buttons: ["OK"],
  });
});
