import pandas as pd
import folium
import streamlit as st
import json
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

# 한글 폰트 설정 (Windows에서 Malgun Gothic을 사용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 처리

# 데이터 경로 설정
geo_path = "./05. skorea_municipalities_geo_simple.json"  # 상대 경로
data_path = "./pop.xlsx"  # 상대 경로

# 지도 데이터 준비 (GeoJSON 로드)
geo_data = json.load(open(geo_path, encoding='utf-8'))

# Excel 데이터 로드
pop = pd.read_excel(data_path)

# 'ID'를 인덱스로 설정
pop_folium = pop.set_index('ID')

# Streamlit 대시보드 설정
st.sidebar.header("📊 2016년 대한민국 인구")  # 제목 변경

# 카테고리 선택
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])

# 동적으로 제목 설정
st.title(f"📊 {category} 대시보드")

# 카토그램 시각화 함수
def drawKorea(targetData, blockedMap, cmapname, title):
    gamma = .75
    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + min(blockedMap[targetData])
    vmin = min(blockedMap[targetData])
    vmax = max(blockedMap[targetData])

    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)

    for idx, row in blockedMap.iterrows():
        dispname = '\n'.join(row['ID'].split())
        fontsize, linespacing = 6, 1.2
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        ax.annotate(dispname, (row['x']+0.5, row['y']+0.5), weight='bold', fontsize=fontsize, ha='center',
                    va='center', color=annocolor, linespacing=linespacing)

    ax.invert_yaxis()
    ax.axis('off')
    cbar = fig.colorbar(c, ax=ax, shrink=.1, aspect=10)
    cbar.set_label(targetData)
    ax.set_title(title, fontsize=12)
    st.pyplot(fig)

# 페이지 레이아웃
col1, col2 = st.columns([2, 1])

# 카테고리별 코드 예시
if category == '총인구수':
    with col1:
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data,
            data=pop_folium['인구수합계'],
            columns=[pop_folium.index, '인구수합계'],
            key_on='feature.id',
            fill_color='YlGnBu',
            legend_name='총인구수'
        ).add_to(map)
        st_folium(map, width=700)
    with col2:
        st.write("상위 10개 지역")
        st.write(pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10))

elif category == '소멸위기지역':
    st.write("소멸위기지역 분석")

elif category == '여성비':
    st.write("여성비 분석")

elif category == '2030여성비':
    st.write("2030여성비 분석")
