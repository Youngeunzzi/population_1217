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

# 한글 폰트 설정
font_path = os.path.join("fonts", "NANUMGOTHIC-REGULAR.TTF")
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    raise FileNotFoundError(f"Font file not found at {font_path}")

plt.rcParams['axes.unicode_minus'] = False

# 데이터 준비
geo_path = "05. skorea_municipalities_geo_simple.json"
geo_data = json.load(open(geo_path, encoding='utf-8'))
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

# 카토그램 함수
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

# 페이지별 구현
col1, col2 = st.columns([2, 1])

if category == '총인구수':
    with col1:
        st.subheader("🗺️ 지도 시각화")
        map_data = pop_folium['인구수합계']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(geo_data=geo_data, data=map_data, columns=[pop_folium.index, map_data],
                          fill_color='YlGnBu', key_on='feature.id', legend_name="총인구수").add_to(map)
        st_folium(map, width=700)

        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포')
    
    with col2:
        st.subheader("📊 상위 10개 지역 분석")
        top10 = pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10)
        st.table(top10.rename(columns={"ID": "지역명", "인구수합계": "총인구수"}))
        st.markdown("**🔍 요약**: 인구수가 가장 많은 지역은 **서울특별시**입니다.")

elif category == '소멸위기지역':
    with col1:
        st.subheader("🗺️ 지도 시각화")
        map_data = pop_folium['소멸비율']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(geo_data=geo_data, data=map_data, columns=[pop_folium.index, map_data],
                          fill_color='PuRd', key_on='feature.id', legend_name="소멸비율").add_to(map)
        st_folium(map, width=700)
        drawKorea('소멸비율', pop, 'Reds', '지역별 소멸위기 비율')
    
    with col2:
        st.subheader("📊 소멸위기 Top10")
        top10 = pop[['ID', '소멸비율']].sort_values(by='소멸비율', ascending=False).head(10)
        st.table(top10.rename(columns={"ID": "지역명", "소멸비율": "소멸비율"}))
        st.markdown("**🔍 요약**: 소멸비율이 가장 높은 지역은 **농어촌 지역**이 많습니다.")

elif category == '여성비':
    with col1:
        st.subheader("🗺️ 지도 시각화")
        map_data = pop_folium['여성비']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(geo_data=geo_data, data=map_data, columns=[pop_folium.index, map_data],
                          fill_color='RdBu', key_on='feature.id', legend_name="여성비").add_to(map)
        st_folium(map, width=700)
        drawKorea('여성비', pop, 'RdBu', '지역별 여성비 분포')
    
    with col2:
        st.subheader("📊 여성비 분석")
        avg_female_ratio = pop.groupby('소멸위기지역')['여성비'].mean().reset_index()
        st.bar_chart(avg_female_ratio.rename(columns={"여성비": "평균 여성비"}))
        st.markdown("**🔍 요약**: 소멸위기 지역의 여성비가 상대적으로 높습니다.")

elif category == '2030여성비':
    with col1:
        st.subheader("🗺️ 지도 시각화")
        map_data = pop_folium['2030여성비']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(geo_data=geo_data, data=map_data, columns=[pop_folium.index, map_data],
                          fill_color='RdBu', key_on='feature.id', legend_name="2030여성비").add_to(map)
        st_folium(map, width=700)
        drawKorea('2030여성비', pop, 'RdBu', '지역별 2030여성비 분포')

    with col2:
        st.subheader("📊 2030여성비 Top10")
        top10 = pop[['ID', '2030여성비']].sort_values(by='2030여성비', ascending=False).head(10)
        st.table(top10.rename(columns={"ID": "지역명", "2030여성비": "2030 여성비"}))
        st.markdown("**🔍 요약**: 2030여성비가 가장 높은 지역은 **서울 및 수도권**입니다.")
