import json
import pandas as pd
import os
import sqlite3

def extract_weather_data(json_file_path):
    """
    讀取天氣 JSON 檔案，解析並回傳 DataFrame。
    """
    print(f"正在讀取 JSON 檔案: {json_file_path}")

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 解析 JSON 結構
        try:
            root = data.get('cwaopendata', {})
            resources = root.get('resources', {})
            resource = resources.get('resource', {})
            data_payload = resource.get('data', {})
            agr_forecasts = data_payload.get('agrWeatherForecasts', {})
            weather_forecasts = agr_forecasts.get('weatherForecasts', {})
            locations = weather_forecasts.get('location', [])
        except AttributeError:
            print("JSON 結構解析錯誤，請確認檔案格式是否正確。")
            return None

        if not locations:
            print("未找到地點資料。")
            return None

        # 準備資料列表
        records = []

        for loc in locations:
            location_name = loc.get('locationName', '未知地點')

            weather_elements = loc.get('weatherElements', {})

            # 取得各項數據的 daily 列表
            wx_daily = weather_elements.get('Wx', {}).get('daily', [])
            min_t_daily = weather_elements.get('MinT', {}).get('daily', [])
            max_t_daily = weather_elements.get('MaxT', {}).get('daily', [])

            daily_data = {}

            # 處理天氣現象
            for item in wx_daily:
                date = item.get('dataDate')
                if date:
                    if date not in daily_data:
                        daily_data[date] = {}
                    daily_data[date]['weather'] = item.get('weather')

            # 處理最低溫
            for item in min_t_daily:
                date = item.get('dataDate')
                if date:
                    if date not in daily_data:
                        daily_data[date] = {}
                    daily_data[date]['min_temp'] = item.get('temperature')

            # 處理最高溫
            for item in max_t_daily:
                date = item.get('dataDate')
                if date:
                    if date not in daily_data:
                        daily_data[date] = {}
                    daily_data[date]['max_temp'] = item.get('temperature')

            # 將整理好的資料加入 records
            for date, info in daily_data.items():
                records.append({
                    '地點': location_name,
                    '日期': date,
                    '天氣現象': info.get('weather', 'N/A'),
                    '最低溫(°C)': info.get('min_temp', 'N/A'),
                    '最高溫(°C)': info.get('max_temp', 'N/A')
                })

        if not records:
            print("沒有解析到任何有效資料。")
            return None

        # 建立 DataFrame
        df = pd.DataFrame(records)

        # 排序 (依地點和日期)
        df = df.sort_values(by=['地點', '日期'])
        return df

    except FileNotFoundError:
        print(f"找不到檔案: {json_file_path}")
        return None
    except Exception as e:
        print(f"發生錯誤: {e}")
        return None

def save_to_excel(df, excel_file_path):
    if df is None or df.empty:
        print("沒有資料可寫入 Excel")
        return
    print(f"正在寫入 Excel 檔案: {excel_file_path}")
    df.to_excel(excel_file_path, index=False, engine='openpyxl')
    print("Excel 轉換完成！")

def save_to_sqlite(df, db_file_path, table_name='weather_forecast'):
    if df is None or df.empty:
        print("沒有資料可寫入 SQLite")
        return

    print(f"正在寫入 SQLite 資料庫: {db_file_path}")

    # 建立副本並加入 id 欄位 (從 1 開始)
    df_sql = df.copy()
    df_sql.insert(0, 'id', range(1, len(df_sql) + 1))

    try:
        with sqlite3.connect(db_file_path) as conn:
            # if_exists='replace' 會重建資料表，若要累加可改用 'append'
            df_sql.to_sql(table_name, conn, if_exists='replace', index=False)
        print("SQLite 儲存完成！")
    except Exception as e:
        print(f"寫入 SQLite 失敗: {e}")

def process_weather_data(json_file_path, excel_file_path=None, db_file_path=None):
    """
    主處理函數：讀取 JSON，並選擇性儲存為 Excel 或 SQLite
    """
    df = extract_weather_data(json_file_path)
    if df is not None:
        if excel_file_path:
            save_to_excel(df, excel_file_path)
        if db_file_path:
            save_to_sqlite(df, db_file_path)

if __name__ == "__main__":
    # 設定輸入與輸出檔案路徑
    input_json = 'weather_data.json'
    output_excel = 'weather_report.xlsx'
    output_db = 'weather_data.db'

    # 確保使用絕對路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, input_json)
    output_excel_path = os.path.join(current_dir, output_excel)
    output_db_path = os.path.join(current_dir, output_db)

    process_weather_data(input_path, excel_file_path=output_excel_path, db_file_path=output_db_path)