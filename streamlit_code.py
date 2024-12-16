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

# 한글 폰트 설정
font_path = os.path.join("fonts", "NANUMGOTHIC-REGULAR.TTF")
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    raise FileNotFoundError(f"Font file not found at {font_path}")

plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 처리

# 지도 데이터 준비
geo_path = "05. skorea_municipalities_geo_simple.json"
geo_data = json.load(open(geo_path, encoding='utf-8'))

# 데이터 준비
pop = pd.read_excel('pop.xlsx')
pop_folium = pop.set_index('ID')

# Streamlit 설정
st.sidebar.header("📊 2016년 대한민국 인구")
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])

# 제목 설정
st.title({
    '총인구수': "👨‍👩‍👧 총인구수 대시보드",
    '소멸위기지역': "🚨 소멸위기지역 대시보드",
    '여성비': "💁‍♀️👵 여성비 대시보드",
    '2030여성비': "💁‍♀️ 2030여성비 대시보드"
}[category])

# 카토그램 시각화 함수
def drawKorea(targetData, blockedMap, cmapname, title):
    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)
    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)
    ax.invert_yaxis()
    ax.axis('off')
    cbar = fig.colorbar(c, ax=ax, shrink=.1, aspect=10)
    ax.set_title(title, fontsize=12)
    st.pyplot(fig)

# Streamlit의 Columns 사용
col1, col2 = st.columns([2, 1])

if category == '총인구수':
    with col1:
        map_data = pop_folium['인구수합계']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data, data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='YlGnBu', key_on='feature.id',
            legend_name='인구수 합계'
        ).add_to(map)
        st_folium(map, width=700)
        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포')

    with col2:
        st.subheader('지역별 총인구수')
        table = pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10)
        st.write(table)
        st.markdown("🔍 **요약**: 인구수 분포와 주요 지역 확인")

elif category == '소멸위기지역':
    with col1:
        map_data = pop_folium['소멸위기지역']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data, data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='PuRd', key_on='feature.id',
            legend_name='소멸위기지역'
        ).add_to(map)
        st_folium(map, width=700)
        drawKorea('소멸위기지역', pop, 'Reds', '지역별 소멸위기지역')

    with col2:
        crisis_count = pop['소멸위기지역'].value_counts()
        fig = px.pie(values=crisis_count, names=crisis_count.index, hole=0.4, title="소멸위기지역 비율")
        st.plotly_chart(fig)

elif category == '여성비':
    with col1:
        map_data = pop_folium['여성비']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data, data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='RdBu', key_on='feature.id',
            legend_name='여성비'
        ).add_to(map)
        st_folium(map, width=700)
        pop['여성비'] = (pop['인구수여자'] / pop['인구수합계'] - 0.5) * 100
        drawKorea('여성비', pop, 'RdBu', '지역별 여성비 분포')

elif category == '2030여성비':
    with col1:
        map_data = pop_folium['2030여성비']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(
            geo_data=geo_data, data=map_data,
            columns=[pop_folium.index, map_data],
            fill_color='RdBu', key_on='feature.id',
            legend_name='2030여성비'
        ).add_to(map)
        st_folium(map, width=700)
        pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
        drawKorea('2030여성비', pop, 'RdBu', '지역별 2030여성비 분포')

