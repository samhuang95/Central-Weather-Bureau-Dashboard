import streamlit as st
import pandas as pd
import os
import plotly.express as px
from weather_crawler import get_weather_data
from data_processor import extract_weather_data

# 設定頁面標題與配置 (必須是第一個 Streamlit 指令)
st.set_page_config(
    page_title="中央氣象戰情室",
    page_icon="🌾",
    layout="wide"
)

# 自訂 CSS 以優化視覺體驗
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌾 中央氣象戰情室")
st.markdown("### 即時監控全台中央氣象預報與趨勢分析")

# 側邊欄操作區
with st.sidebar:
    st.header("⚙️ 控制台")

    st.subheader("資料更新")
    if st.button("🔄 立即更新資料", type="primary", use_container_width=True):
        with st.spinner("正在連線至中央氣象署 API..."):
            try:
                get_weather_data()
                st.success("✅ 資料更新成功！")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 更新失敗: {e}")

    st.markdown("---")
    st.info("資料來源: [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)")

# 資料路徑
json_path = 'weather_data.json'
excel_path = 'weather_report.xlsx'
db_path = 'weather_data.db'

# 檢查資料是否存在
if os.path.exists(json_path):
    try:
        # 讀取資料
        df = extract_weather_data(json_path)

        if df is not None:
            # 資料前處理：轉換數值型態
            df['最低溫(°C)'] = pd.to_numeric(df['最低溫(°C)'], errors='coerce')
            df['最高溫(°C)'] = pd.to_numeric(df['最高溫(°C)'], errors='coerce')

            # 側邊欄篩選器
            with st.sidebar:
                st.subheader("🔍 篩選條件")

                # 地點篩選
                all_locations = sorted(df['地點'].unique())
                selected_locations = st.multiselect(
                    "選擇地區",
                    all_locations,
                    default=all_locations[:3] if len(all_locations) > 3 else all_locations
                )

                # 日期篩選
                all_dates = sorted(df['日期'].unique())
                selected_dates = st.select_slider(
                    "選擇日期範圍",
                    options=all_dates,
                    value=(all_dates[0], all_dates[-1])
                )

            # 根據篩選條件過濾資料
            mask = (df['地點'].isin(selected_locations)) & \
                   (df['日期'] >= selected_dates[0]) & \
                   (df['日期'] <= selected_dates[1])
            filtered_df = df[mask]

            # --- 儀表板 KPI 區塊 ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📍 監測地點數", f"{len(selected_locations)}", delta=f"總計 {len(all_locations)}")
            with col2:
                avg_temp = filtered_df[['最低溫(°C)', '最高溫(°C)']].mean().mean()
                st.metric("🌡️ 平均氣溫", f"{avg_temp:.1f}°C")
            with col3:
                max_temp = filtered_df['最高溫(°C)'].max()
                st.metric("🔥 最高氣溫", f"{max_temp}°C")
            with col4:
                min_temp = filtered_df['最低溫(°C)'].min()
                st.metric("❄️ 最低氣溫", f"{min_temp}°C")

            st.markdown("---")

            # --- 頁籤區塊 ---
            tab1, tab2, tab3 = st.tabs(["📈 趨勢分析", "📋 詳細數據", "📥 資料下載"])

            with tab1:
                st.subheader("氣溫走勢圖")

                if not filtered_df.empty:
                    # 繪製互動式折線圖
                    fig = px.line(
                        filtered_df,
                        x='日期',
                        y=['最低溫(°C)', '最高溫(°C)'],
                        color='地點',
                        markers=True,
                        title=f"各區氣溫變化 ({selected_dates[0]} ~ {selected_dates[1]})",
                        labels={'value': '溫度 (°C)', 'variable': '指標'}
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)

                    # 天氣現象分佈
                    st.subheader("天氣現象分佈")
                    weather_counts = filtered_df['天氣現象'].value_counts().reset_index()
                    weather_counts.columns = ['天氣現象', '次數']

                    fig_pie = px.pie(
                        weather_counts,
                        values='次數',
                        names='天氣現象',
                        title="天氣現象佔比",
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("⚠️ 目前篩選條件下無資料，請調整篩選器。")

            with tab2:
                st.subheader("詳細氣象數據")
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    column_config={
                        "最低溫(°C)": st.column_config.NumberColumn(format="%.1f°C"),
                        "最高溫(°C)": st.column_config.NumberColumn(format="%.1f°C"),
                    }
                )

            with tab3:
                st.subheader("資料匯出")
                col_d1, col_d2 = st.columns(2)

                # Excel 下載
                if os.path.exists(excel_path):
                    with open(excel_path, "rb") as file:
                        col_d1.download_button(
                            label="📄 下載完整 Excel 報表",
                            data=file,
                            file_name="weather_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

                # SQLite 下載
                if os.path.exists(db_path):
                    with open(db_path, "rb") as file:
                        col_d2.download_button(
                            label="🗄️ 下載 SQLite 資料庫",
                            data=file,
                            file_name="weather_data.db",
                            mime="application/x-sqlite3",
                            use_container_width=True
                        )

        else:
            st.warning("⚠️ 無法解析資料，請嘗試點擊左側「立即更新資料」。")

    except Exception as e:
        st.error(f"❌ 系統發生錯誤: {e}")
else:
    st.info("👋 歡迎使用！目前系統無資料，請點擊左側側邊欄的「立即更新資料」按鈕開始。")
