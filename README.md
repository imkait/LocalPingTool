# 本地網路設備 Ping 監測網頁

本專案提供一個本地端的網頁介面，用於監測 IP 列表的連線狀態 (Ping)。

程式由AI撰寫，歡迎自由修改使用。

![example](/example.png)
## 快速開始

### 1. 啟動伺服器
打開終端機，進入專案目錄並執行 Python 腳本：

```bash
python server.py
```

您會看到類似以下的輸出：
```
Serving at http://localhost:8000
Press Ctrl+C to stop.
```

### 2. 開啟網頁
在瀏覽器中輸入網址：[http://localhost:8000](http://localhost:8000)

### 3. 使用功能
1.  在輸入框輸入 **名稱** (例如 `Google DNS`) 與 **IP** (例如 `8.8.8.8`)。
2.  點擊「新增」按鈕。
3.  監測清單會自動儲存成ips.csv檔案，以方便每次開啟前讀取。
4.  網頁會自動每 60 秒 Ping 一次該 IP（可自行修訂)。 
    - 🟢 **綠燈**：連線正常
    - 🔴 **紅燈**：無法連線 (Timeout)

## 檔案列表
- `server.py`: Python 後端，負責執行 Ping 指令。
- `index.html`: 前端介面。
- `ips.csv`: 監控IP設備清單（自動產生)。

> [!NOTE]
> **如何重啟伺服器？**
> 1. 在終端機按 `Ctrl+C` 停止目前的伺服器。
> 2. 再次輸入 `python server.py` 並按 Enter 啟動。

### 4. 懶人包，使用編譯好的版本，點選直接執行（系統需已安裝python)
1. Windows版下載：[https://github.com/imkait/LocalPingTool/releases/download/v0.1.0/LocalPingtool-v0.1.0-win.exe](https://github.com/imkait/LocalPingTool/releases/download/v0.1.0/LocalPingtool-v0.1.0-win.exe)
3. Mac版下載：[https://github.com/imkait/LocalPingTool/releases/download/v0.1.0/LocalPingtool-v0.1.0-mac.dmg](https://github.com/imkait/LocalPingTool/releases/download/v0.1.0/LocalPingtool-v0.1.0-mac.dmg)
