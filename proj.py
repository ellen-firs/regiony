import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Загружаем geojson
url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson"
geojson = requests.get(url).json()

# Загружаем свои данные (пример: CSV с колонками "Регион" и "Значение")
# Подставь свой файл
df = pd.DataFrame({
    "Регион": ["Москва", "Санкт-Петербург", "Ростовская область", "Волгоградская область"],
    "Значение": [10, 20, 30, 40]
})

st.write("### Данные для отображения")
st.write(df)

# Отладка: список всех регионов в geojson
regions_in_map = [feature['properties']['name'] for feature in geojson['features']]
st.write("### Регионы, доступные в geojson:")
st.write(sorted(regions_in_map))

# Строим карту
fig = px.choropleth(
    df,
    geojson=geojson,
    locations='Регион',
    featureidkey="properties.name",   # важный момент — оставляем как было
    color='Значение',
    color_continuous_scale="Viridis",
    scope="europe",
    labels={'Значение':'Показатель'},
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)
