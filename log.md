# 開發日誌 (Development Log)

## 紀錄 1

**時間**: 2025/12/03 18:00:00 (預估)
**題文內容**:
請幫我使用這一個 URL 寫一個爬蟲程式碼
https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization=CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F&downloadType=WEB&format=JSON

**程式碼與任務簡述**:

- 建立 `weather_crawler.py`。
- 使用 `requests` 套件撰寫基本的 GET 請求邏輯。
- 嘗試讀取 `.env` 中的 Token。

## 紀錄 2

**時間**: 2025/12/03 18:05:00 (預估)
**題文內容**:
我現在已經開好了 venv 你有看到嗎？

**程式碼與任務簡述**:

- 確認 `venv` 環境並安裝 `requests` 套件。
- 解決 SSL 憑證錯誤 (`SSLCertVerificationError`)，加入 `verify=False` 與隱藏警告。
- 修正 JSON 資料解析邏輯，正確提取「地點」、「天氣現象」與「溫度」並顯示於終端機。

## 紀錄 3

**時間**: 2025/12/03 18:10:00 (預估)
**題文內容**:
請分析這份文件，並且幫我整理資料成一個 excel 檔，整理的方式，我需要你使用 python function 的方式

**程式碼與任務簡述**:

- 建立 `data_processor.py`。
- 定義 `json_to_excel` 函式。
- 使用 `pandas` 與 `openpyxl` 將 `weather_data.json` 轉換為 `weather_report.xlsx`。

## 紀錄 4

**時間**: 2025/12/03 18:15:00 (預估)
**題文內容**:
請幫我加入一個邏輯，我希望當我執行爬蟲後，把整理好的資料存進 sqlite DB 中

**程式碼與任務簡述**:

- 修改 `data_processor.py`：
  - 新增 `save_to_sqlite` 函式，使用 `sqlite3` 將 DataFrame 存入資料庫。
  - 重構 `process_weather_data` 主函式以同時支援 Excel 與 SQLite 輸出。
- 修改 `weather_crawler.py`：
  - 引入 `data_processor` 模組。
  - 在爬蟲成功後自動呼叫資料處理流程，實現自動化 (Crawl -> Save JSON -> Excel & DB)。

## 紀錄 5

**時間**: 2025/12/03 18:20:00 (預估)
**題文內容**:
你目前給我的 sqlite 我的最前面會需要一個 id ，請修改

**程式碼與任務簡述**:

- 修改 `data_processor.py` 中的 `save_to_sqlite` 函式。
- 在寫入資料庫前，於 DataFrame 最前方插入 `id` 欄位 (從 1 開始編號)。
- 重新執行爬蟲流程驗證資料庫欄位更新。

## 紀錄 6

**時間**: 2025/12/03 18:25:00 (預估)
**題文內容**:
我希望這個程式，可以部屬到 streamlit 上，請幫我調整

**程式碼與任務簡述**:

- 安裝 `streamlit` 套件。
- 建立 `app.py` 作為 Streamlit 應用程式入口。
- 整合 `weather_crawler.py` 與 `data_processor.py`，在網頁介面上提供「更新資料」按鈕與資料預覽、下載功能。
- 更新 `requirements.txt` 加入必要依賴。

## 紀錄 7

**時間**: 2025/12/03 18:30:00 (預估)
**題文內容**:
我覺得目前的功能不錯，但我希望可以在頁面上，呈現得更像專業互動式的 Dashboard

**程式碼與任務簡述**:

- 安裝 `plotly` 套件以支援互動式圖表。
- 大幅重構 `app.py` 介面：
  - **KPI 指標區**：顯示地點數、平均氣溫、最高/最低氣溫。
  - **側邊欄篩選**：新增「地區」與「日期範圍」篩選器。
  - **分頁設計 (Tabs)**：將內容分為「趨勢分析」、「詳細數據」、「資料下載」。
  - **視覺化圖表**：使用 Plotly 繪製氣溫折線圖與天氣現象圓餅圖。
  - **樣式優化**：設定 `wide` 佈局與自訂 CSS。

## 紀錄 8

**時間**: 2025/12/03 18:35:00 (預估)
**題文內容**:
請幫我加入 ignore 讓一些不必要的資訊推上去 github

**程式碼與任務簡述**:

- 建立 `.gitignore` 檔案。
- 設定忽略規則，排除以下檔案：
  - Python 編譯檔 (`__pycache__`, `*.pyc`)
  - 虛擬環境 (`venv/`)
  - 敏感資訊 (`.env`)
    - 編輯器設定 (`.vscode/`)
    - 程式產生的資料檔 (`weather_data.json`, `weather_report.xlsx`, `weather_data.db`)

## 紀錄 9

**時間**: 2025/12/03 18:40:00 (預估)
**題文內容**:
請幫我補充我的 README，我會需要包含操作流程 streamlit 的連結我會補上，請給我一個空味即可

**程式碼與任務簡述**:

- 更新 `README.md`，補充完整的專案說明。
- 內容包含：專案簡介、功能特色、安裝說明、操作流程 (爬蟲與 Dashboard)、專案結構。
- 預留 Streamlit 線上展示連結的欄位。
