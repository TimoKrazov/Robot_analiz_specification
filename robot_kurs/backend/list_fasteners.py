import pandas as pd
from typing import Dict, Any

def extract_items_from_excel(excel_file: pd.DataFrame) -> Dict[str, Any]:
    try:
        if len(excel_file) < 3:
            return {"error": "Некорректный файл. Заголовки отсутствуют в 3 строке"}
        third_row = excel_file.iloc[2]
        tags = ["артикул", "наименование", "количество"]
        found_cols = {}
        for col_idx, cell in third_row.items():
            if pd.isna(cell):
                continue
            clean = str(cell).strip().lower()
            if clean in tags:
                found_cols[clean] = col_idx
        missing = set(tags) - set(found_cols.keys())

        if missing:
            return {"error": f"Отсутствие необходимых колонок в 3 строке: {','.join(missing)}"}
        

        articul_col_number = found_cols["артикул"]
        name_col_number = found_cols["наименование"]
        quantity_col_number = found_cols["количество"]
        parse_art_name_quantity = excel_file.iloc[3:, [articul_col_number, name_col_number, quantity_col_number]].copy()
        
        parse_art_name_quantity.columns = ["Артикул", "Наименование", "Количество"]
        parse_art_name_quantity = parse_art_name_quantity.dropna(how='all').reset_index(drop=True)
        # parse_art_name_quantity = parse_art_name_quantity.dropna(subset="Артикул").reset_index(drop=True)
        check = parse_art_name_quantity["Артикул"].isna()
        if check.any():
            return {"error": f"Присутствует пустой артикул в строке {[idx + 4 for idx in parse_art_name_quantity[check].index]}"}
        parse_art_name_quantity["Количество"] = pd.to_numeric(parse_art_name_quantity["Количество"], errors='coerce').fillna(0)
        
        if len(parse_art_name_quantity) == 0:
            return {"error": "Колонки нужные есть. Данные отсутствуют"}
        

        grouped_to_articul = parse_art_name_quantity.groupby("Артикул", as_index=False).agg({"Наименование":"first", "Количество":"sum"})
        
        result_json_one_excel = (grouped_to_articul.set_index("Артикул").to_dict(orient='index'))
        return result_json_one_excel

    except Exception as e:
        return {"error": f"Ошибка при обработке данных: {str(e)}"}