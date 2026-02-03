import streamlit as st
import requests
from datetime import datetime

st.title('RPA-робот для автоматизации процесса заказа крепёжных изделий')
# uploaded_excel_files = st.file_uploader("Загрузите спецификацию (Excel-формат)", type=["xlsx", "xls"])
uploaded_excel_files = st.file_uploader("Загрузите спецификацию (Excel-формат)", type=["xlsx", "xls"], accept_multiple_files=True)
if uploaded_excel_files:
    if st.button("Анализ"):
        # excel_files = {"file": (uploaded_excel_files.name, uploaded_excel_files, uploaded_excel_files.type)}
        excel_files = [("files", (f.name, f, f.type)) for f in uploaded_excel_files]
        response = requests.post("http://localhost:8000/parse-excel/", files=excel_files)
        if response.status_code == 200:
            if response.headers.get('content-type') == 'application/zip':
                st.write("Документы:")
                st.download_button("Скачать все сгенерированные документы", response.content, datetime.now().strftime("Документы на закупку_%Y-%m-%d.zip"), "application/zip")
            else:
                data = response.json()
                
                st.error(f"Уведомление: {data['error']}")
        else:
            st.error(f"Ошибка при обработке файла {response.status_code}")