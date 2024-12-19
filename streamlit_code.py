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
font_path = os.path.join("fonts", "NANUMGOTHIC-REGULAR.TTF")  # 정확한 경로 지정
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
st.sidebar.header("📊 2016년 대한민국 인구")  # 제목 변경
category = st.sidebar.selectbox("카테고리 선택", ['총인구수', '소멸위기지역', '여성비', '2030여성비'])

# ----------- 4. 페이지별 제목 설정 ----------- 
if category == '총인구수':
    st.title("👨‍👩‍👧 총인구수 대시보드")
elif category == '소멸위기지역':
    st.title("🚨 소멸위기지역 대시보드")
elif category == '여성비':
    st.title("💁‍♀️👵 여성비 대시보드")
elif category == '2030여성비':
    st.title("💁‍♀️ 2030여성비 대시보드")

# 카토그램 시각화 (matplotlib을 통한 처리)
def drawKorea(targetData, blockedMap, cmapname, title):
    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + min(blockedMap[targetData])
    vmin, vmax = min(blockedMap[targetData]), max(blockedMap[targetData])
    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

    fig, ax = plt.subplots(figsize=(6, 8))
    c = ax.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname, edgecolor='#aaaaaa', linewidth=0.5)

    for idx, row in blockedMap.iterrows():
        dispname = '\n'.join(row['ID'].split())
        fontsize, linespacing = 6, 1.2
        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        ax.annotate(dispname, (row['x'] + 0.5, row['y'] + 0.5),
                    weight='bold', fontsize=fontsize, ha='center', va='center',
                    color=annocolor, linespacing=linespacing, fontproperties=font_prop)

    ax.invert_yaxis()
    ax.axis('off')
    cbar = fig.colorbar(c, ax=ax, shrink=.1, aspect=10)
    cbar.set_label(targetData, fontproperties=font_prop)
    ax.set_title(title, fontsize=12, fontproperties=font_prop)
    st.pyplot(fig)

# ----------- 5. 지도 및 분석 ----------- 
col1, col2 = st.columns([2, 1])  # 지도는 크고 다른 차트들은 작은 크기로 설정

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

# 카테고리별로 지도 및 그래프 출력
if category == '총인구수':
    with col1:
        st_folium(create_choropleth('인구수합계', '인구수 합계', 'YlGnBu'), width=700)
        drawKorea('인구수합계', pop, 'Blues', '지역별 총인구수 분포 한눈에 보기')

    with col2:
        st.subheader('지역별 총인구수')
        population_table = pop[['ID', '인구수합계']].sort_values(by='인구수합계', ascending=False).head(10)
        st.write(population_table)

        # 테이블 바로 아래에 요약 박스 추가
        st.markdown(
            """
            <div style="border: 2px solid #0066cc; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #f0f8ff;">
                <h4>🔍 정보</h4>
                <ul>
                    <li><strong>데이터</strong>: 2016년 성인 인구통계</li>
                    <li><strong>출처</strong>: KOSIS 국가통계포털</li>
                    <li><strong>선정 기준</strong>: 20세-100세 이상</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

elif category == '소멸위기지역':
    with col1:
        st_folium(create_choropleth('소멸위기지역', '소멸위기지역', 'PuRd'), width=700)
        drawKorea('소멸위기지역', pop, 'Reds', '지역별 소멸위기 분포 한눈에 보기')

    with col2:
        # 도넛차트
        crisis_area_counts = pop['소멸위기지역'].value_counts()
        fig = px.pie(values=crisis_area_counts, names=crisis_area_counts.index, hole=0.4,
                     title="소멸위기지역 비율", labels={"소멸위기지역": "소멸위기지역"})
        fig.update_traces(textinfo='percent+label', pull=[0.1, 0])  # 첫 번째 값만 튀어나오게
        st.plotly_chart(fig)

        # 소멸위기 비율이 높은 지역 Top 10 분석
        top10_crisis_areas = pop[['ID', '소멸비율', '인구수합계']].sort_values(by='소멸비율', ascending=False).head(10)
        top10_crisis_areas = top10_crisis_areas.rename(columns={'ID': '지역명', '인구수합계': '인구수 합계'})
        fig = px.bar(top10_crisis_areas, x="지역명", y="소멸비율", color="지역명",
                     title="소멸위기지역별 소멸비율 Top10 분석", labels={"소멸비율": "소멸비율"})
        st.plotly_chart(fig)

        # 요약 박스 추가
        st.markdown(
            """
            <div style="border: 2px solid #ff6666; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #ffe6e6;">
                <h4>🔍 요약</h4>
                <ul>
                    <li><strong>소멸위기지역 비율</strong>: 약 67.1%</li>
                    <li><strong>소멸위기지역별 소멸비율 1위</strong>: 경기도 수원시 영통구</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

elif category == '여성비':
    with col1:
        st_folium(create_choropleth('여성비', '여성비', 'RdBu'), width=700)
        drawKorea('여성비', pop, 'RdBu', '지역별 여성비 분포 한눈에 보기')

    with col2:
        # 여성비와 소멸위기지역 비교 그래프
        st.subheader("소멸위기지역과 여성비 비교")
        avg_female_ratio = pop.groupby('소멸위기지역')['여성비'].mean().reset_index()
        fig = px.bar(avg_female_ratio, x="소멸위기지역", y="여성비", color="소멸위기지역",
                     title="소멸위기지역 여부에 따른 여성비 비교", labels={"여성비": "평균 여성비"})
        st.plotly_chart(fig)

        # 요약 박스 추가
        st.markdown(
            """
            <div style="border: 2px solid #ff9933; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #fff5e6;">
                <h4>🔍 요약</h4>
                <ul>
                    <li><strong>소멸위기지역 평균 여성비</strong>: 3.2%</li>
                    <li><strong>비소멸위기지역 평균 여성비</strong>: 1.8%</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

        # 여성비 수식 박스 추가
        st.markdown(
            """
            <div style="border: 2px solid #0073e6; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #f0f8ff;">
                <h4>📏 여성비 계산 수식</h4>
                <p><strong>여성비 = (여성 인구 / 총 인구 - 0.5) * 100</strong></p>
                <p><strong>여성 인구</strong>: 65세 이상 여성의 총 인구</p>
                <p><strong>총 인구</strong>: 65세 이상 인구의 총합</p>
            </div>
            """, unsafe_allow_html=True
        )

elif category == '2030여성비':
    with col1:
        st_folium(create_choropleth('2030여성비', '2030여성비', 'RdBu'), width=700)
        drawKorea('2030여성비', pop, 'RdBu', '지역별 2030여성비 분포 한눈에 보기')

    with col2:
        # 지역별 2030 여성비 평균 비교
        st.subheader("지역별 2030 여성비 평균 비교")
        avg_2030_female_ratio = pop.groupby('ID')['2030여성비'].mean().reset_index()
        avg_2030_female_ratio = avg_2030_female_ratio.sort_values(by='2030여성비', ascending=False).head(10)

        # 막대 그래프 시각화
        fig = px.bar(avg_2030_female_ratio, x="ID", y="2030여성비", color="2030여성비",
                     title="지역별 2030 여성비 평균 상위 10개 지역",
                     labels={"ID": "지역명", "2030여성비": "2030 여성비 평균"})
        st.plotly_chart(fig)

        # 요약 박스 추가
        st.markdown(
            """
            <div style="border: 2px solid #ff9933; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #fff5e6;">
                <h4>🔍 요약</h4>
                <ul>
                    <li><strong>2030 여성비 평균이 가장 높은 지역</strong>: 서울특별시 강남구</li>
                    <li><strong>상위 10개 지역 분석</strong>: 주로 수도권 및 도시 지역에 집중</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

        # 2030 여성비 수식 박스 추가
        st.markdown(
            """
            <div style="border: 2px solid #0073e6; padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #f0f8ff;">
                <h4>📏 2030 여성비 계산 수식</h4>
                <p><strong>2030여성비 = (20-39세 여성 인구 / 20-39세 총 인구 - 0.5) * 100</strong></p>
                <p><strong>20-39세 여성 인구</strong>: 해당 연령대의 여성 인구</p>
                <p><strong>20-39세 총 인구</strong>: 해당 연령대의 전체 인구</p>
            </div>
            """, unsafe_allow_html=True
        )
