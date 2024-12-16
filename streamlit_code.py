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

# 폰트 설정 (Streamlit 배포 환경에 맞는 기본 폰트 사용)
plt.rcParams['font.family'] = 'sans-serif'  # 기본 폰트
plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 깨짐 방지

# 상대 경로로 데이터 파일 지정
geo_path = "./05. skorea_municipalities_geo_simple.json"
data_path = "./pop.xlsx"

# 데이터 로드
geo_data = json.load(open(geo_path, encoding='utf-8'))  # GeoJSON 파일
pop = pd.read_excel(data_path)  # Excel 파일

# 'ID'를 인덱스로 설정
pop_folium = pop.set_index('ID')

# Streamlit 대시보드 설정
st.sidebar.header("📊 2016년 대한민국 인구")  # 제목 변경

# 카테고리 선택
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])

# 각 카테고리별 동적 제목 설정
st.title({
    '총인구수': "👨‍👩‍👧 총인구수 대시보드",
    '소멸위기지역': "🚨 소멸위기지역 대시보드",
    '여성비': "💁‍♀️👵 여성비 대시보드",
    '2030여성비': "💁‍♀️ 2030여성비 대시보드"
}[category])

# 카토그램 시각화
def drawKorea(targetData, blockedMap, cmapname, title):
    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + min(blockedMap[targetData])
    vmin, vmax = min(blockedMap[targetData]), max(blockedMap[targetData])
    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)
    
    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)
    
    for idx, row in blockedMap.iterrows():
        dispname = '\n'.join(row['ID'].split())  # 긴 이름 나누기
        fontsize = 6
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        ax.annotate(dispname, (row['x']+0.5, row['y']+0.5), weight='bold', fontsize=fontsize, ha='center', va='center', color=annocolor)
    
    ax.invert_yaxis()
    ax.axis('off')
    fig.colorbar(c, ax=ax, shrink=.1, aspect=10).set_label(targetData)
    ax.set_title(title, fontsize=12)
    st.pyplot(fig)

# Streamlit의 Columns를 사용하여 가로 배치
col1, col2 = st.columns([2, 1])

if category == '총인구수':
    with col1:
        map_data = pop_folium['인구수합계']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(geo_data=geo_data, data=map_data, columns=[pop_folium.index, map_data],
                          fill_color='YlGnBu', key_on='feature.id', legend_name='인구수 합계').add_to(map)
        st_folium(map, width=700)
        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포 한눈에 보기')

    with col2:
        population_table = pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10)
        st.subheader('지역별 총인구수')
        st.write(population_table.rename(columns={'ID': '지역명', '인구수합계': '인구수 합계'}))

elif category == '소멸위기지역':
    with col1:
        map_data = pop_folium['소멸위기지역']
        map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
        folium.Choropleth(geo_data=geo_data, data=map_data, columns=[pop_folium.index, map_data],
                          fill_color='PuRd', key_on='feature.id', legend_name='소멸위기지역').add_to(map)
        st_folium(map, width=700)

    with col2:
        crisis_area_counts = pop['소멸위기지역'].value_counts()
        fig = px.pie(values=crisis_area_counts, names=crisis_area_counts.index, hole=0.4,
                     title="소멸위기지역 비율")
        st.plotly_chart(fig)

elif category == '여성비':
    with col1:
        pop['여성비'] = (pop['인구수여자']/pop['인구수합계'] - 0.5) * 100
        drawKorea('여성비', pop, 'RdBu', '지역별 여성비 분포 한눈에 보기')

    with col2:
        avg_female_ratio = pop.groupby('소멸위기지역')['여성비'].mean().reset_index()
        fig = px.bar(avg_female_ratio, x="소멸위기지역", y="여성비", title="소멸위기지역 여부에 따른 여성비 비교")
        st.plotly_chart(fig)

elif category == '2030여성비':
    with col1:
        pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
        drawKorea('2030여성비', pop, 'RdBu', '지역별 2030여성비 분포 한눈에 보기')

    with col2:
        avg_2030_female_ratio = pop.groupby('ID')['2030여성비'].mean().reset_index()
        fig = px.bar(avg_2030_female_ratio.sort_values(by='2030여성비', ascending=False).head(10),
                     x="ID", y="2030여성비", title="지역별 2030 여성비 평균 상위 10개 지역")
        st.plotly_chart(fig)
