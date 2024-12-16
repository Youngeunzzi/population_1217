# C011230 전영은
# 배포 링크:

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

# Nanum Gothic 폰트 설정
font_path = os.path.join("fonts", "NANUMGOTHIC-REGULAR.TTF")
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
else:
    raise FileNotFoundError(f"Font file not found at {font_path}")

# 데이터 준비
geo_path = "05. skorea_municipalities_geo_simple.json"
geo_data = json.load(open(geo_path, encoding='utf-8'))
pop = pd.read_excel('pop.xlsx')
pop_folium = pop.set_index('ID')

# Streamlit 설정
st.sidebar.header("📊 2016년 대한민국 인구")
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])
st.title({
    '총인구수': "👨‍👩‍👧 총인구수 대시보드",
    '소멸위기지역': "🚨 소멸위기지역 대시보드",
    '여성비': "💁‍♀️👵 여성비 대시보드",
    '2030여성비': "💁‍♀️ 2030여성비 대시보드"
}[category])

# Choropleth 지도 함수
def create_choropleth(column, legend_name, fill_color):
    map = folium.Map(location=[36.2002, 127.054], zoom_start=7)
    folium.Choropleth(
        geo_data=geo_data,
        data=pop_folium[column],
        columns=[pop_folium.index, pop_folium[column]],
        fill_color=fill_color,
        key_on='feature.id',
        legend_name=legend_name
    ).add_to(map)
    return map

# 카토그램 함수
def drawKorea(targetData, blockedMap, cmapname, title):
    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + min(blockedMap[targetData])
    vmin, vmax = min(blockedMap[targetData]), max(blockedMap[targetData])
    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)

    for idx, row in blockedMap.iterrows():
        dispname = '\n'.join(row['ID'].split())
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        ax.annotate(dispname, (row['x'] + 0.5, row['y'] + 0.5),
                    weight='bold', fontsize=6, ha='center', va='center',
                    color=annocolor, linespacing=1.2, fontproperties=font_prop)

    ax.invert_yaxis()
    ax.axis('off')
    cbar = fig.colorbar(c, ax=ax, shrink=.1, aspect=10)
    cbar.set_label(targetData, fontproperties=font_prop)
    ax.set_title(title, fontsize=12, fontproperties=font_prop)
    st.pyplot(fig)

# UI 구성
col1, col2 = st.columns([2, 1])

if category == '소멸위기지역':
    with col1:
        st_folium(create_choropleth('소멸위기지역', '소멸위기지역', 'PuRd'), width=700)
        drawKorea('소멸위기지역', pop, 'Reds', '지역별 소멸위기 분포 한눈에 보기')
    with col2:
        # 소멸위기지역 비율 도넛 차트
        crisis_counts = pop['소멸위기지역'].value_counts()
        fig = px.pie(values=crisis_counts, names=crisis_counts.index, hole=0.4, title="소멸위기지역 비율")
        st.plotly_chart(fig)

        # 소멸비율 Top10 막대그래프
        top10 = pop[['ID', '소멸비율']].sort_values(by='소멸비율', ascending=False).head(10)
        fig = px.bar(top10, x='ID', y='소멸비율', title="소멸위기지역별 소멸비율 Top10")
        st.plotly_chart(fig)

if category == '여성비':
    pop['여성비'] = (pop['인구수여자'] / pop['인구수합계'] - 0.5) * 100
    with col1:
        st_folium(create_choropleth('여성비', '여성비', 'RdBu'), width=700)
        drawKorea('여성비', pop, 'RdBu', '지역별 여성비 분포 한눈에 보기')
    with col2:
        # 소멸위기지역과 여성비 비교 그래프
        avg_female_ratio = pop.groupby('소멸위기지역')['여성비'].mean().reset_index()
        fig = px.bar(avg_female_ratio, x="소멸위기지역", y="여성비", color="소멸위기지역",
                     title="소멸위기지역 여부에 따른 여성비 비교")
        st.plotly_chart(fig)

        # 수식 텍스트박스
        st.markdown("""
        <div style="border: 2px solid #0073e6; padding: 10px; border-radius: 5px;">
            <h4>📏 여성비 계산 수식</h4>
            <p><strong>여성비 = (여성 인구 / 총 인구 - 0.5) * 100</strong></p>
        </div>
        """, unsafe_allow_html=True)

if category == '2030여성비':
    pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
    with col1:
        st_folium(create_choropleth('2030여성비', '2030여성비', 'RdBu'), width=700)
        drawKorea('2030여성비', pop, 'RdBu', '지역별 2030여성비 분포 한눈에 보기')
    with col2:
        # 지역별 2030 여성비 평균 비교
        avg_2030 = pop[['ID', '2030여성비']].sort_values(by='2030여성비', ascending=False).head(10)
        fig = px.bar(avg_2030, x='ID', y='2030여성비', title="지역별 2030 여성비 평균 Top10")
        st.plotly_chart(fig)

        # 수식 텍스트박스
        st.markdown("""
        <div style="border: 2px solid #0073e6; padding: 10px; border-radius: 5px;">
            <h4>📏 2030 여성비 계산 수식</h4>
            <p><strong>2030여성비 = (20-39세 여성 인구 / 20-39세 총 인구 - 0.5) * 100</strong></p>
        </div>
        """, unsafe_allow_html=True)

