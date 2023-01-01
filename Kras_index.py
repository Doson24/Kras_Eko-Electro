import pandas as pd
import streamlit as st
# from utils import chart, db
from main import main_deploy, main, search_xls
import pydeck as pdk
from pathlib import Path


@st.cache
# @st.experimental_singleton
def load_data():
        db, error_read = main_deploy()
        address = {house.address: i for i, house in enumerate(db)}
        return db, error_read, address

def slice_data(data, start, end):
        data = data[(data.index >= pd.to_datetime(start)) & (data.index <= pd.to_datetime(end)) ]
        return data

st.set_page_config(layout="wide", page_icon="📊", page_title="Красэко-электро",
        initial_sidebar_state="expanded")

data, error_read, address = load_data()
# data = pd.read_html(f'Восточная, 19.xls', encoding='cp1251', decimal=',')

st.sidebar.subheader("Filter")

select_address = st.sidebar.selectbox('Адрес:', options=address.keys())
table1 = data[address[select_address]].entry1
table2 = data[address[select_address]].entry2


side_col1, side_col2 = st.sidebar.columns(2)
start_date = side_col1.date_input('Дата начала', value=table1.index.min(),
                                                max_value=table1.index.max(),
                                                min_value=table1.index.min())
end_date = side_col2.date_input('Дата окончания', value=table1.index.max(),
                                                max_value=table1.index.max(),
                                                min_value=table1.index.min())

table1 = slice_data(table1, start_date, end_date)



st.title("💬 Красэко-электро")

st.text('Средние')
col1, col2, col3, col4, col5, col6 = st.columns(5)
col1.metric("t1", f'{round(table1["t1/°C"].mean(), 2)}°C', "1.2 °C")
col2.metric("t2", f'{round(table1["t2/°C"].mean(), 2)}°C', "1.3 °C")
col3.metric("dt", f'{round(table1["dt/°C"].mean(), 2)}°C', "-1.3 °C")
col4.metric("P1", f'{round(table1["P1/кг/см2"].mean(), 2)}кг/см2', "-1.3 °C")
col5.metric("P2", f'{round(table1["P2/кг/см2"].mean(), 2)}кг/см2', "-1.3 °C")
col6.metric("ИТОГО М1", f'{round(table1["М1/т"].sum(), 2)}кг/см2', "-1.3 °C")


columns = list(table1.columns)
account_selections = st.sidebar.multiselect(
        "Select", options=columns, default=columns[:3])


st.line_chart(table1, x=list(table1.index), y=account_selections)


if st.checkbox('Данные в виде таблицы'):
        st.dataframe(table1, use_container_width=True)

st.write(' ')
st.write('')
st.write('')
st.write('')

# Bar_chart
st.markdown('### Диаграмма загруженных файлов')
start_dir = str(Path.cwd())

count_all_houses = len(search_xls(start_dir))
count_bd_houses = len(data)
st.bar_chart(pd.DataFrame({
    'name': ['Загружено домов', 'Ошибка чтения', 'Всего домов'],
    'Количество': [count_bd_houses, error_read, count_all_houses]
}), x='name', y='Количество')







input_house = [1, 2, 3]
st.sidebar.select_slider("Выберите номер Ввода:", options=input_house)
st.sidebar.select_slider("Выберите Схему подключения:", options=input_house)



with st.sidebar:
        st.radio('Тык', [1, 2])

# Group multiple widgets:
# with st.form(key='my_form'):
#         username = st.text_input('Username')
#         password = st.text_input('Password')
#         st.form_submit_button('Login')


# st.image('МЫВМЕСТЕ.jpg')

# st.snow()
def show_map():
    def map(data, lat, lon, zoom):
        DATA_URL = "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/biergartens.json"
        ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/c/c4/Projet_bi%C3%A8re_logo_v2.png"

        icon_data = {
            # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
            # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
            "url": ICON_URL,
            "width": 242,
            "height": 242,
            "anchorY": 242,
        }

        # data = pd.read_json(DATA_URL)
        data["icon_data"] = None
        for i in data.index:
            data["icon_data"][i] = icon_data
        # data['text'] = [52, 53]
        HexagonLayer = pdk.Layer(
                                "HexagonLayer",
                                data=data,
                                get_position=["lon", "lat"],
                                radius=100,
                                elevation_scale=4,
                                elevation_range=[0, 1000],
                                pickable=True,
                                extruded=True,)
        icon_layer = pdk.Layer(
            type="IconLayer",
            data=data,
            get_icon="icon_data",
            get_size=4,
            size_scale=15,
            get_position=["lon", "lat"],
            get_elevation='text',
            pickable=True,)

        st.write(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state={
                    "latitude": lat,
                    "longitude": lon,
                    "zoom": zoom,
                    "pitch": 50,
                },
                layers=[icon_layer],
                tooltip={'text': '{Name} {t1}'}
            )
        )

        st.dataframe(data)


    lat = [house.longitude for house in data]
    lon = [house.latitude for house in data]
    name = [house.address for house in data]

    # t1 = [house.entry1.get("t1/°C")
    #       if house.entry1.get("t1/°C") and house.entry1.get("t1/°C").dtype == float
    #       else 99 for house in data]

    data_map = pd.DataFrame()
    data_map['lon'] = lon
    data_map['lat'] = lat
    data_map['Name'] = name
    # data_map['t1'] = t1

    # round(table1["t1/°C"].mean(), 2)

    map(data_map, 56.16933215, 93.45940342605422, 11)

if __name__ == '__main__':
    pass
    # show_map()
