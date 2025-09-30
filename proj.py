import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import re

st.set_page_config(page_title="Рейтинг регионов России", layout="wide")
st.title("🗺️ Рейтинг депрессивности регионов России")

# ---- ДАННЫЕ (как у тебя) ----
data = {
    'Регион': [
        'Белгородская область', 'Брянская область', 'Владимирская область', 
        'Воронежская область', 'Ивановская область', 'Калужская область', 
        'Костромская область', 'Курская область', 'Липецкая область', 
        'Московская область', 'Орловская область', 'Рязанская область', 
        'Смоленская область', 'Тамбовская область', 'Тверская область', 
        'Тульская область', 'Ярославская область', 'Москва', 
        'Республика Карелия', 'Республика Коми', 'Ненецкий автономный округ', 
        'Архангельская область', 'Вологодская область', 'Калининградская область', 
        'Ленинградская область', 'Мурманская область', 'Новгородская область', 
        'Псковская область', 'Санкт-Петербург', 'Республика Адыгея', 
        'Республика Калмыкия', 'Республика Крым', 'Краснодарский край', 
        'Астраханская область', 'Волгоградская область', 'Ростовская область', 
        'Севастополь', 'Республика Дагестан', 'Республика Ингушетия', 
        'Кабардино-Балкарская Республика', 'Карачаево-Черкесская Республика', 
        'Республика Северная Осетия – Алания', 'Чеченская Республика', 
        'Ставропольский край', 'Республика Башкортостан', 'Республика Марий Эл', 
        'Республика Мордовия', 'Республика Татарстан', 'Удмуртская Республика', 
        'Чувашская Республика', 'Пермский край', 'Кировская область', 
        'Нижегородская область', 'Оренбургская область', 'Пензенская область', 
        'Самарская область', 'Саратовская область', 'Ульяновская область', 
        'Курганская область', 'Свердловская область', 'Ханты-Мансийский автономный округ — Югра', 
        'Ямало-Ненецкий автономный округ', 'Тюменская область', 'Челябинская область', 
        'Республика Алтай', 'Республика Тыва', 'Республика Хакасия', 'Алтайский край', 
        'Красноярский край', 'Иркутская область', 'Кемеровская область', 
        'Новосибирская область', 'Омская область', 'Томская область', 
        'Республика Бурятия', 'Республика Саха (Якутия)', 'Забайкальский край', 
        'Камчатский край', 'Приморский край', 'Хабаровский край', 'Амурская область', 
        'Магаданская область', 'Сахалинская область', 'Еврейская автономная область', 
        'Чукотский автономный округ'
    ],
    'Ранг': [33, 26, 44, 27, 10, 60, 16, 46, 25, 74, 14, 24, 19, 23, 17, 39, 12, 85, 
             1, 8, 35, 6, 31, 58, 68, 37, 45, 11, 81, 48, 40, 18, 75, 38, 43, 56, 63, 
             78, 80, 72, 70, 50, 79, 59, 73, 21, 61, 76, 52, 64, 30, 4, 62, 41, 15, 
             71, 47, 34, 2, 42, 82, 84, 66, 53, 28, 51, 55, 9, 32, 13, 3, 29, 20, 36, 
             22, 69, 7, 77, 57, 65, 49, 67, 54, 5, 83]
}
df = pd.DataFrame(data)
df['Уровень проблемности'] = 86 - df['Ранг']

# ---- Загрузка GeoJSON (оставляем ту же ссылку) ----
@st.cache_data
def load_geojson():
    base_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson"
    try:
        resp = requests.get(base_url, timeout=15)
        resp.raise_for_status()
        geo = resp.json()
        # Добавляем Крым и Севастополь (упрощённо) — имена на английском, чтобы совпадать с geojson
        crimea_coords = [[32.5, 44.5], [36.5, 44.5], [36.5, 46.2], [32.5, 46.2], [32.5, 44.5]]
        sev_coords = [[33.4, 44.5], [33.7, 44.5], [33.7, 44.7], [33.4, 44.7], [33.4, 44.5]]
        geo["features"].append({
            "type": "Feature",
            "properties": {"name": "Republic of Crimea"},
            "geometry": {"type": "Polygon", "coordinates": [crimea_coords]}
        })
        geo["features"].append({
            "type": "Feature",
            "properties": {"name": "Sevastopol"},
            "geometry": {"type": "Polygon", "coordinates": [sev_coords]}
        })
        return geo
    except Exception as e:
        st.error(f"Ошибка при загрузке geojson: {e}")
        return None

geojson = load_geojson()
if not geojson:
    st.stop()

# ---- Для удобства: покажем, какие имена есть в geojson (в раскрывающемся блоке) ----
geo_names = [f['properties'].get('name') for f in geojson['features']]
with st.expander("Показать имена регионов из geojson (для отладки)"):
    st.write(f"Всего записей в geojson: {len(geo_names)}")
    st.write(sorted([n for n in geo_names if n]))

# ---- Полный словарь сопоставления (ключи = значения из df['Регион']) ----
# Значения — те имена, которые чаще всего используются в click_that_hood geojson (англ.)
name_mapping = {
    'Белгородская область': 'Belgorod',
    'Брянская область': 'Bryansk',
    'Владимирская область': 'Vladimir',
    'Воронежская область': 'Voronezh',
    'Ивановская область': 'Ivanovo',
    'Калужская область': 'Kaluga',
    'Костромская область': 'Kostroma',
    'Курская область': 'Kursk',
    'Липецкая область': 'Lipetsk',
    'Московская область': 'Moscow Oblast',
    'Орловская область': 'Oryol',
    'Рязанская область': 'Ryazan',
    'Смоленская область': 'Smolensk',
    'Тамбовская область': 'Tambov',
    'Тверская область': 'Tver',
    'Тульская область': 'Tula',
    'Ярославская область': 'Yaroslavl',
    'Москва': 'Moscow',
    'Республика Карелия': 'Republic of Karelia',
    'Республика Коми': 'Komi',
    'Ненецкий автономный округ': 'Nenets Autonomous Okrug',
    'Архангельская область': 'Arkhangelsk',
    'Вологодская область': 'Vologda',
    'Калининградская область': 'Kaliningrad',
    'Ленинградская область': 'Leningrad',
    'Мурманская область': 'Murmansk',
    'Новгородская область': 'Novgorod',
    'Псковская область': 'Pskov',
    'Санкт-Петербург': 'Saint Petersburg',
    'Республика Адыгея': 'Adygea',
    'Республика Калмыкия': 'Kalmykia',
    'Республика Крым': 'Republic of Crimea',
    'Краснодарский край': 'Krasnodar',
    'Астраханская область': 'Astrakhan',
    'Волгоградская область': 'Volgograd',
    'Ростовская область': 'Rostov',
    'Севастополь': 'Sevastopol',
    'Республика Дагестан': 'Dagestan',
    'Республика Ингушетия': 'Ingushetia',
    'Кабардино-Балкарская Республика': 'Kabardino-Balkarian Republic',
    'Карачаево-Черкесская Республика': 'Karachay-Cherkess Republic',
    'Республика Северная Осетия – Алания': 'North Ossetia - Alania',
    'Чеченская Республика': 'Chechnya',
    'Ставропольский край': 'Stavropol',
    'Республика Башкортостан': 'Bashkortostan',
    'Республика Марий Эл': 'Mari El',
    'Республика Мордовия': 'Mordovia',
    'Республика Татарстан': 'Tatarstan',
    'Удмуртская Республика': 'Udmurt Republic',
    'Чувашская Республика': 'Chuvashia',
    'Пермский край': 'Perm',
    'Кировская область': 'Kirov',
    'Нижегородская область': 'Nizhny Novgorod',
    'Оренбургская область': 'Orenburg',
    'Пензенская область': 'Penza',
    'Самарская область': 'Samara',
    'Саратовская область': 'Saratov',
    'Ульяновская область': 'Ulyanovsk',
    'Курганская область': 'Kurgan',
    'Свердловская область': 'Sverdlovsk',
    'Ханты-Мансийский автономный округ — Югра': 'Khanty-Mansi Autonomous Okrug',
    'Ямало-Ненецкий автономный округ': 'Yamalo-Nenets Autonomous Okrug',
    'Тюменская область': 'Tyumen',
    'Челябинская область': 'Chelyabinsk',
    'Республика Алтай': 'Altai Republic',
    'Республика Тыва': 'Tuva',
    'Республика Хакасия': 'Khakassia',
    'Алтайский край': 'Altai Krai',
    'Красноярский край': 'Krasnoyarsk',
    'Иркутская область': 'Irkutsk',
    'Кемеровская область': 'Kemerovo',
    'Новосибирская область': 'Novosibirsk',
    'Омская область': 'Omsk',
    'Томская область': 'Tomsk',
    'Республика Бурятия': 'Buryatia',
    'Республика Саха (Якутия)': 'Sakha Republic',
    'Забайкальский край': 'Zabaykalsky Krai',
    'Камчатский край': 'Kamchatka',
    'Приморский край': 'Primorsky Krai',
    'Хабаровский край': 'Khabarovsk',
    'Амурская область': 'Amur',
    'Магаданская область': 'Magadan',
    'Сахалинская область': 'Sakhalin',
    'Еврейская автономная область': 'Jewish Autonomous Oblast',
    'Чукотский автономный округ': 'Chukotka'
}

# ---- Вспомогательные функции для "умного" сопоставления ----
def tokenize(name: str):
    # разбиваем на токены, убираем общие слова
    if not isinstance(name, str):
        return set()
    s = re.sub(r'[^A-Za-z0-9а-яА-Я\- ]', ' ', name)  # оставляем буквы/цифры/дефис
    tokens = set(t.lower() for t in s.split() if t)
    stopwords = {'oblast', 'region', 'republic', 'krai', 'autonomous', 'okrug', 'autonomous', 'auton', 'of', '-', 'the'}
    return tokens - stopwords

geo_names_set = set(n for n in geo_names if n)

def smart_match(preferred_name: str):
    """Вернёт имя из geojson, если есть точное совпадение, иначе попробует подобрать по токенам."""
    if preferred_name in geo_names_set:
        return preferred_name
    # пробуем на маленькие варианты: без слова 'Oblast' и т.п.
    pref_tokens = tokenize(preferred_name)
    best = None
    best_score = 0
    for g in geo_names_set:
        g_tokens = tokenize(g)
        score = len(pref_tokens & g_tokens)
        if score > best_score:
            best_score = score
            best = g
    if best_score > 0:
        return best
    # если совсем ничего — вернём preferred_name (px пропустит его)
    return preferred_name

# ---- Применяем маппинг + умный подбор ----
mapped = []
used_manual = {}  # для отладки - какие были сопоставлены вручную
for r in df['Регион']:
    pref = name_mapping.get(r, r)  # сначала явный маппинг
    matched = smart_match(pref)
    if matched != pref:
        used_manual[r] = (pref, matched)
    mapped.append(matched)

df['Регион_норм'] = mapped

# Покажем, какие из первых маппингов были изменены (полезно для отладки)
if used_manual:
    with st.expander("Сопоставления (предпочтительные -> найденные в geojson)"):
        st.write(used_manual)

# Какие всё ещё не найдены в geojson:
not_found = [r for r in df['Регион_норм'].unique() if r not in geo_names_set]
if not_found:
    st.warning("Некоторые имена из df не были найдены в geojson (они будут проигнорированы на карте):")
    st.write(sorted(not_found))

# ---- Строим карту ----
st.subheader("🗺️ Географическая карта регионов России (с Крымом)")

fig = px.choropleth(
    df,
    geojson=geojson,
    locations='Регион_норм',
    featureidkey="properties.name",
    color='Уровень проблемности',
    color_continuous_scale="RdYlBu_r",
    range_color=(0, 85),
    scope="world",
    labels={'Уровень проблемности': 'Уровень проблемности'},
    hover_name='Регион',
    hover_data={'Ранг': True, 'Уровень проблемности': False},
    title='Рейтинг депрессивности регионов России'
)

fig.update_geos(
    visible=False,
    showcountries=True,
    countrycolor="black",
    showsubunits=True,
    subunitcolor="gray",
    subunitwidth=0.5,
    fitbounds="locations",
    center={"lat": 60, "lon": 90},
    projection_scale=1.8
)

fig.update_layout(height=700, margin={"r":0,"t":50,"l":0,"b":0}, geo=dict(bgcolor='lightblue', showland=True, landcolor='white'))

st.plotly_chart(fig, use_container_width=True)

# ---- Топы ----
st.subheader("📊 Топ регионов")
col1, col2 = st.columns(2)
with col1:
    st.write("**🔴 Топ-10 проблемных:**")
    for i, row in df.nsmallest(10, 'Ранг').iterrows():
        st.write(f"{row['Ранг']}. {row['Регион']}")
with col2:
    st.write("**🔵 Топ-10 благополучных:**")
    for i, row in df.nlargest(10, 'Ранг').iterrows():
        st.write(f"{row['Ранг']}. {row['Регион']}")
