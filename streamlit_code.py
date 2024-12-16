# C011230 전영은
# 배포 링크:

import pandas as pd
import folium
import streamlit as st
import json
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import os
import matplotlib.font_manager as fm

# 폰트 경로 설정
font_path = os.path.join("fonts", "NanumGothic.ttf")

# 폰트 적용
if os.path.exists(font_path):
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rcParams['font.family'] = font_name  # 한글 폰트 적용
else:
    raise FileNotFoundError(f"Font file not found at {font_path}. Ensure the file exists in the 'fonts' directory.")


# 지도 데이터 준비 (GeoJSON 경로 지정)
geo_path = "./05. skorea_municipalities_geo_simple.json"
geo_data = json.load(open(geo_path, encoding='utf-8'))

# 데이터 준비 (엑셀 데이터 로딩)
pop = pd.read_excel('./pop.xlsx')

# 'ID'를 인덱스로 설정
pop_folium = pop.set_index('ID')

# Streamlit 대시보드 설정
st.sidebar.header("📊 2016년 대한민국 인구")  # 제목 변경

# 카테고리 선택
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])

# 각 카테고리별로 동적으로 제목 설정
if category == '총인구수':
    st.title("👨‍👩‍👧 총인구수 대시보드")
elif category == '소멸위기지역':
    st.title("🚨 소멸위기지역 대시보드")
elif category == '여성비':
    st.title("💁‍♀️👵 여성비 대시보드")
elif category == '2030여성비':
    st.title("💁‍♀️ 2030여성비 대시보드")

# 카토그램 시각화 함수
def drawKorea(targetData, blockedMap, cmapname, title):
    gamma = .75
    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + min(blockedMap[targetData])
    vmin = min(blockedMap[targetData])
    vmax = max(blockedMap[targetData])
    
    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)
    
    # Matplotlib 그래프 수정
    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)
    
    for idx, row in blockedMap.iterrows():
        dispname = row['ID']
        dispname = '\n'.join(dispname.split())
        
        fontsize, linespacing = 6, 1.2
        row['x'] = int(row['x'])
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        ax.annotate(dispname, (row['x']+0.5, row['y']+0.5), weight='bold', fontsize=fontsize, ha='center', va='center', color=annocolor, linespacing=linespacing)

    ax.invert_yaxis()
    ax.axis('off')
    cbar = fig.colorbar(c, ax=ax, shrink=.1, aspect=10)
    cbar.set_label(targetData)
    
    ax.set_title(title, fontsize=12)
    st.pyplot(fig)

# Streamlit Columns 설정
col1, col2 = st.columns([2, 1])

if category == '총인구수':
    with col1:
        map_data = pop_folium['인구수합계']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data,
            data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='YlGnBu',
            key_on='feature.id',
            legend_name='인구수 합계'
        ).add_to(map)
        st_folium(map, width=700)
        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포')

    with col2:
        st.subheader('지역별 총인구수')
        table = pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10)
        st.write(table)

elif category == '소멸위기지역':
    with col1:
        map_data = pop_folium['소멸위기지역']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data,
            data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='PuRd',
            key_on='feature.id',
            legend_name='소멸위기지역'
        ).add_to(map)
        st_folium(map, width=700)
        drawKorea('소멸위기지역', pop, 'Reds', '지역별 소멸위기 분포')

elif category == '여성비':
    with col1:
        pop['여성비'] = (pop['인구수여자'] / pop['인구수합계'] - 0.5) * 100
        map_data = pop_folium['여성비']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data,
            data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='RdBu',
            key_on='feature.id',
            legend_name='여성비'
        ).add_to(map)
        st_folium(map, width=700)

elif category == '2030여성비':
    with col1:
        pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
        map_data = pop_folium['2030여성비']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data,
            data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='RdBu',
            key_on='feature.id',
            legend_name='2030여성비'
        ).add_to(map)
        st_folium(map, width=700)
