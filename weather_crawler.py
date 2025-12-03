import requests
import json
import os
from data_processor import process_weather_data

def get_weather_data():
    # 預設 Token，來自您的請求
    api_token = "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F"

    # 嘗試從 .env 讀取 Token 以保持安全性
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('API_TOKEN='):
                        api_token = line.strip().split('=', 1)[1]
                        break
        except Exception as e:
            print(f"讀取 .env 失敗，將使用預設 Token。錯誤: {e}")

    # 建構 URL
    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={api_token}&downloadType=WEB&format=JSON"

    print(f"正在發送請求至: {url}")

    # 忽略 SSL 警告 (針對某些環境下的憑證問題)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # 檢查 HTTP 狀態碼

        data = response.json()

        # 儲存原始 JSON 資料
        output_filename = 'weather_data.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"成功！資料已儲存至 {output_filename}")

        # 自動執行資料處理與儲存 (Excel + SQLite)
        print("\n--- 開始資料處理與儲存 ---")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 確保讀取的是剛剛寫入的檔案 (使用絕對路徑比較保險)
        output_path = os.path.join(current_dir, output_filename)
        excel_path = os.path.join(current_dir, 'weather_report.xlsx')
        db_path = os.path.join(current_dir, 'weather_data.db')

        process_weather_data(output_path, excel_file_path=excel_path, db_file_path=db_path)
        print("--- 資料處理結束 ---\n")

        # 解析並顯示部分資料結構 (針對 F-A0010-001 格式)
        # 資料結構: cwaopendata -> resources -> resource -> data -> agrWeatherForecasts -> weatherForecasts -> location
        root = data.get('cwaopendata', {})
        resources = root.get('resources', {})
        resource = resources.get('resource', {})
        data_payload = resource.get('data', {})
        agr_forecasts = data_payload.get('agrWeatherForecasts', {})
        weather_forecasts = agr_forecasts.get('weatherForecasts', {})
        locations = weather_forecasts.get('location', [])

        if locations:
            print(f"\n取得 {len(locations)} 筆地點資料。以下是前 3 筆範例：")
            for loc in locations[:3]:
                name = loc.get('locationName', '未知地點')
                print(f"\n地點: {name}")

                # 取得天氣現象 (Wx) 和 溫度 (MinT, MaxT)
                weather_elements = loc.get('weatherElements', {})
                wx_daily = weather_elements.get('Wx', {}).get('daily', [])
                min_t_daily = weather_elements.get('MinT', {}).get('daily', [])
                max_t_daily = weather_elements.get('MaxT', {}).get('daily', [])

                # 顯示前 3 天的預報
                for i in range(min(3, len(wx_daily))):
                    date = wx_daily[i].get('dataDate', '未知日期')
                    weather = wx_daily[i].get('weather', '未知天氣')

                    # 嘗試對應溫度
                    min_temp = "N/A"
                    max_temp = "N/A"

                    if i < len(min_t_daily):
                        min_temp = min_t_daily[i].get('temperature', 'N/A')
                    if i < len(max_t_daily):
                        max_temp = max_t_daily[i].get('temperature', 'N/A')

                    print(f"  日期: {date}, 天氣: {weather}, 溫度: {min_temp}-{max_temp}°C")
        else:
            print("未找到地點資料，請檢查 API 回傳格式。")

    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤: {e}")
    except json.JSONDecodeError:
        print("無法解析回傳的 JSON 資料")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    get_weather_data()
