import pandas as pd
import streamlit as st
# from utils import chart, db
from main import main, search_xls

@st.cache
# @st.experimental_singleton
def load_data():
        db, error_read = main()
        address = {house.name[:-4]: i for i, house in enumerate(db)}
        return db, error_read, address

def slice_data(data, start, end):
        data = data[(data.index >= pd.to_datetime(start)) & (data.index <= pd.to_datetime(end)) ]
        return data

st.set_page_config(layout="wide", page_icon="📊", page_title="Красэко-электро",
        initial_sidebar_state="expanded")

data, error_read, address = load_data()


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
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("t1", f'{round(table1["t1/°C"].mean(), 2)}°C', "1.2 °C")
col2.metric("t2", f'{round(table1["t2/°C"].mean(), 2)}°C', "1.3 °C")
col3.metric("dt", f'{round(table1["dt/°C"].mean(), 2)}°C', "-1.3 °C")
col4.metric("P1", f'{round(table1["P1/кг/см2"].mean(), 2)}кг/см2', "-1.3 °C")
col5.metric("P2", f'{round(table1["P2/кг/см2"].mean(), 2)}кг/см2', "-1.3 °C")


columns = list(table1.columns)
account_selections = st.sidebar.multiselect(
        "Select", options=columns, default=columns[:3])

st.text(select_address)

st.line_chart(table1, x=list(table1.index), y=account_selections)


if st.checkbox('Данные в виде таблицы'):
        st.dataframe(table1, use_container_width=True)

st.write(' ')
st.write('')
st.write('')
st.write('')

# Bar_chart
st.markdown('### Диаграмма загруженных файлов')
count_all_houses = len(search_xls('data/Октябрь'))
count_bd_houses = len(data)
st.bar_chart(pd.DataFrame({
    'name': ['Загружено', 'Ошибка чтения', 'Всего'],
    'Количество файлов': [count_bd_houses, error_read, count_all_houses]
}), x='name', y='Количество файлов')







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

locate = pd.DataFrame({'lat': [56.16933215, 56.245044449999995],
                       'lon': [93.45940342605422, 93.538263485505211]},
                      columns=['lat', 'lon'])
st.dataframe(locate)
st.map(locate)

st.image('МЫВМЕСТЕ.jpg')

# st.snow()