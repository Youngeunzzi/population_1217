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

# 한글 폰트 설정
font_path = os.path.join("fonts", "NANUMGOTHIC-REGULAR.TTF")  # 폰트 경로
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
else:
    raise FileNotFoundError(f"Font file not found at {font_path}")

plt.rcParams['axes.unicode_minus'] = False  # 음수 기호 처리

# 데이터 로드
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

# 카토그램 함수
def drawKorea(targetData, blockedMap, cmapname, title):
    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)

    for idx, row in blockedMap.iterrows():
        dispname = '\n'.join(row['ID'].split())
        annocolor = 'white' if row[targetData] > 0 else 'black'
        ax.annotate(dispname, (row['x'] + 0.5, row['y'] + 0.5), weight='bold',
                    fontsize=6, ha='center', va='center', color=annocolor)

    ax.invert_yaxis()
    ax.axis('off')
    fig.colorbar(c, ax=ax, shrink=0.1, aspect=10).set_label(targetData)
    ax.set_title(title, fontsize=12, fontproperties=font_prop)
    st.pyplot(fig)

# Choropleth 지도 생성
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

# 카테고리별 분석 및 시각화
col1, col2 = st.columns([2, 1])

if category == '총인구수':
    with col1:
        st_folium(create_choropleth('인구수합계', '인구수 합계', 'YlGnBu'), width=700)
        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포')

    with col2:
        st.subheader("상위 10개 지역 총인구수")
        top10 = pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10)
        st.write(top10)

elif category == '소멸위기지역':
    with col1:
        st_folium(create_choropleth('소멸위기지역', '소멸위기지역', 'PuRd'), width=700)
        drawKorea('소멸위기지역', pop, 'Reds', '소멸위기지역 분포')

    with col2:
        st.subheader("소멸위기 비율 Top 10")
        top10_crisis = pop[['ID', '소멸비율']].sort_values(by='소멸비율', ascending=False).head(10)
        st.bar_chart(top10_crisis.set_index('ID'))

elif category == '여성비':
    pop['여성비'] = (pop['인구수여자'] / pop['인구수합계'] - 0.5) * 100
    with col1:
        st_folium(create_choropleth('여성비', '여성비', 'RdBu'), width=700)
        drawKorea('여성비', pop, 'RdBu', '여성비 분포')

    with col2:
        st.subheader("여성비 평균 비교")
        avg_female_ratio = pop.groupby('소멸위기지역')['여성비'].mean()
        st.bar_chart(avg_female_ratio)

elif category == '2030여성비':
    pop['2030여성비'] = (pop['20-39세여자'] / pop['20-39세합계'] - 0.5) * 100
    with col1:
        st_folium(create_choropleth('2030여성비', '2030여성비', 'RdBu'), width=700)
        drawKorea('2030여성비', pop, 'RdBu', '2030여성비 분포')

    with col2:
        st.subheader("2030 여성비 상위 10개 지역")
        top10_2030 = pop[['ID', '2030여성비']].sort_values(by='2030여성비', ascending=False).head(10)
        st.bar_chart(top10_2030.set_index('ID'))
