import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Загружаем geojson (как у тебя)
url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson"
geojson = requests.get(url).json()

# Пример данных (подставь свои)
df = pd.DataFrame({
    "Регион": ["Москва", "Санкт-Петербург", "Ростовская область", "Волгоградская область", "Астраханская область", "Республика Калмыкия"],
    "Значение": [10, 20, 30, 40, 50, 60]
})

# Словарь сопоставления (ключ = название в df, значение = название в geojson)
name_mapping = {
    'Москва': 'Moscow',
    'Санкт-Петербург': 'Saint Petersburg',
    'Ростовская область': 'Rostov',
    'Волгоградская область': 'Volgograd',
    'Астраханская область': 'Astrakhan',
    'Республика Калмыкия': 'Kalmykia',
}

# Применяем сопоставление
df['region_match'] = df['Регион'].apply(lambda x: name_mapping.get(x, x))

# Строим карту
fig = px.choropleth(
    df,
    geojson=geojson,
    locations='region_match',
    featureidkey="properties.name",
    color='Значение',
    color_continuous_scale="Viridis",
    scope="europe",
    labels={'Значение': 'Показатель'}
)

fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)
