import streamlit as st
# from utils import chart, db
from main import main


st.set_page_config(layout="wide", page_icon="📊", page_title="Красэко-электро",
        initial_sidebar_state="expanded")


db = main()
adress = [house.name for house in db]

table1 = db[0].entry1
table2 = db[0].entry2
# table1 = clear_data(table1)
# table2 = clear_data(table2)

st.title("💬 Красэко-электро")

st.text('Средние')
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("t1", f'{round(table1[table1.columns[0]].mean(), 2)}°C', "1.2 °C")
col2.metric("t2", f'{round(table1[table1.columns[1]].mean(), 2)}°C', "1.3 °C")
col3.metric("dt", f'{round(table1[table1.columns[2]].mean(), 2)}°C', "-1.3 °C")
col4.metric("P1", f'{round(table1[table1.columns[8]].mean(), 2)}кг/см2', "-1.3 °C")
col5.metric("P2", f'{round(table1[table1.columns[9]].mean(), 2)}кг/см2', "-1.3 °C")

# st.metric

# st.line_chart(table1)

if st.checkbox('Данные ввиде таблицы'):
        st.write(table1)
st.dataframe(table1)

# st.user.email()

st.sidebar.subheader("Filter")

st.sidebar.multiselect('Адрес', options=adress)

st.sidebar.date_input('Дата начала')
st.sidebar.date_input('Дата окончания')

date = list(table1.columns)
account_selections = st.sidebar.multiselect(
        "Select", options=date, default=date)


input_house = [1,2,3]
st.sidebar.select_slider("Выберите номер Ввода:", options=input_house)
st.sidebar.select_slider("Выберите Схему подключения:", options=input_house)

with st.sidebar:
        st.radio('Тык', [1, 2])

# Group multiple widgets:
with st.form(key='my_form'):
        username = st.text_input('Username')
        password = st.text_input('Password')
        st.form_submit_button('Login')

st.image('МЫВМЕСТЕ.jpg')

# st.snow()