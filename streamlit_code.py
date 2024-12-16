# C011230 전영은
# 배포 링크: https://population1217-jhixieghajrhgkeqe4baum.streamlit.app/
# streamlit 홈페이지에서 구현했을때, 자꾸 카토그램에 해당하는 글꼴이 깨집니다 ㅠㅠ... 계속 해결해봤는데도, 안돼서 그냥 제출하겠습니다.

import os
import pandas as pd
import folium
import streamlit as st
import json
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import plotly.express as px

# ----------- 1. Nanum Gothic 폰트 설정 -----------
# 정확한 경로에 있는 Nanum Gothic 폰트를 설정합니다.
font_path = "C:/Users/lynn9/AppData/Local/Microsoft/Windows/Fonts/NanumGothic-Regular.ttf"
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
else:
    raise FileNotFoundError(f"Font file not found at {font_path}")

# ----------- 2. 데이터 불러오기 -----------
geo_path = "05. skorea_municipalities_geo_simple.json"
geo_data = json.load(open(geo_path, encoding='utf-8'))
pop = pd.read_excel('pop.xlsx')
pop_folium = pop.set_index('ID')

# ----------- 3. Streamlit 설정 -----------
st.sidebar.header("📊 2016년 대한민국 인구")
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])

# ----------- 4. 페이지별 제목 설정 -----------
st.title(f"📊 {category} 대시보드")

# ----------- 5. 카토그램 시각화 함수 -----------
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
        dispname = row['ID']
        dispname = '\n'.join(dispname.split())  # 긴 이름을 여러 줄로 나누기
        fontsize, linespacing = 6, 1.2
        row['x'] = int(row['x'])
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        
        ax.annotate(
            dispname, 
            (row['x'] + 0.5, row['y'] + 0.5), 
            weight='bold', 
            fontsize=fontsize, 
            ha='center', 
            va='center', 
            color=annocolor, 
            linespacing=linespacing, 
            fontproperties=font_prop  # 폰트 설정 추가
        )

    ax.invert_yaxis()
    ax.axis('off')
    cbar = fig.colorbar(c, ax=ax, shrink=.1, aspect=10)
    cbar.set_label(targetData, fontproperties=font_prop)  # 폰트 설정 추가
    ax.set_title(title, fontsize=12, fontproperties=font_prop)  # 폰트 설정 추가
    st.pyplot(fig)  # Streamlit에서 그래프 출력

# ----------- 6. 페이지에 따른 데이터 및 시각화 -----------
col1, col2 = st.columns([2, 1])  # 왼쪽에 지도, 오른쪽에 표 및 분석 차트

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
            legend_name='총인구수'
        ).add_to(map)
        st_folium(map, width=700)
        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포')

if category == '소멸위기지역':
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
        drawKorea('소멸위기지역', pop, 'Reds', '지역별 소멸위기지역 분포')

if category == '여성비':
    with col1:
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
        drawKorea('여성비', pop, 'RdBu', '지역별 여성비 분포')

if category == '2030여성비':
    with col1:
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
        drawKorea('2030여성비', pop, 'RdBu', '지역별 2030여성비 분포')
