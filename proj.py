# Альтернативный источник GeoJSON
@st.cache_data
def load_alternative_geojson():
    try:
        # Альтернативный источник
        url = "https://raw.githubusercontent.com/mapswe/russian-regions-geojson/master/russia.geojson"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    # Если альтернативный не загрузился, используем базовый и добавляем Крым
    base_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson"
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            geojson = response.json()
            
            # Добавляем Крым и Севастополь
            crimea_coords = [
                [32.5, 44.5], [36.5, 44.5], [36.5, 46.2], [32.5, 46.2], [32.5, 44.5]
            ]
            
            sevastopol_coords = [
                [33.4, 44.5], [33.7, 44.5], [33.7, 44.7], [33.4, 44.7], [33.4, 44.5]
            ]
            
            crimea_feature = {
                "type": "Feature",
                "properties": {"name": "Крым"},
                "geometry": {"type": "Polygon", "coordinates": [crimea_coords]}
            }
            
            sevastopol_feature = {
                "type": "Feature", 
                "properties": {"name": "Севастополь"},
                "geometry": {"type": "Polygon", "coordinates": [sevastopol_coords]}
            }
            
            geojson["features"].append(crimea_feature)
            geojson["features"].append(sevastopol_feature)
            
            return geojson
    except:
        pass
    
    return None

# Замените вызов функции загрузки
with st.spinner("Загружаем карту России..."):
    geojson = load_alternative_geojson()
