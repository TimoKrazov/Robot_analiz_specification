import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

current_dir = Path(__file__).parent
load_dotenv(current_dir/"data_connect_db.env")
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}


def checking_components(list_specification_components: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        ending_details: List[Dict] = []
        missing_details: List[Dict] = []
        missing_article: List[Dict] = []
        all_articles_specification = list(list_specification_components.keys())
        placeholders = ','.join(['%s'] * len(all_articles_specification))
        cursor.execute(f"SELECT article, remainder, minimum_threshold, max_capacity FROM remnants_materials WHERE article IN ({placeholders})", all_articles_specification)
        rows = cursor.fetchall()
        
        
        
        database_data = {row["article"]: {"remainder":row["remainder"], "minimum_threshold": row["minimum_threshold"], "max_capacity": row["max_capacity"]} for row in rows}
        
        found_articles = set(database_data.keys())
        for article, data_in_specification in list_specification_components.items():
            quantity_in_specification = data_in_specification['Количество']
            
            if article not in found_articles:
                missing_article.append(article)
                continue
            
            remainder = database_data[article]["remainder"]
            minimum_threshold = database_data[article]["minimum_threshold"]
            max_capacity = database_data[article]["max_capacity"]

            if remainder < quantity_in_specification:
                missing_details.append({'article': article, 'name': data_in_specification["Наименование"], 'missing_number': quantity_in_specification-remainder})
                ending_details.append({'article': article, 'name': data_in_specification["Наименование"], 'missing_number': max_capacity})
            elif remainder <= minimum_threshold or remainder - quantity_in_specification <= minimum_threshold:
                ending_details.append({'article': article, 'name': data_in_specification["Наименование"], 'missing_number': max_capacity-(remainder-quantity_in_specification)})
        cursor.close()
        conn.close()
        if missing_article:
            return {"error": f"Отсутствуют в базе следующие артикули: {', '.join(missing_article)}"}
        if len(missing_details) == 0 and len(ending_details) == 0:
            return {"error": "Пополнение склада не нужно"}
        return {"недостающие": missing_details,"заканчивающиеся": ending_details}
    except Exception as e:
        
        return {"error": f"Ошибка при подключении к базе данных: {str(e)}"}

