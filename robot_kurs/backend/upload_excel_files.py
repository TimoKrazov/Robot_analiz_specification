from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
from io import BytesIO
from .list_fasteners import extract_items_from_excel
from .search_in_database import checking_components
import os 
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile
import zipfile
from starlette.background import BackgroundTask
from collections import defaultdict

def generate_specification_pdf(missing_items, output_path):
    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template('template.html')
    rendered_html = template.render(missing_items=missing_items)
    HTML(string=rendered_html).write_pdf(output_path)

def cleanup_zip(zip_path):
    if os.path.exists(zip_path):
        os.remove(zip_path)

application  = FastAPI()
application.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@application.post("/parse-excel/")
# async def parse_excel(file: UploadFile = File(...)):
async def parse_excel(files: list[UploadFile] = File(...)):
    all_items_raw = []
    for file in files:
        try:
            contents = await file.read()
            uploaded_excel_file = pd.read_excel(BytesIO(contents), header=None)
            

            parsered_data = extract_items_from_excel(uploaded_excel_file)
            if "error" in parsered_data:
                return parsered_data
            for art, data in parsered_data.items():
                all_items_raw.append({"article": art, "name": data["Наименование"], "quantity": data["Количество"]})
        except Exception as e:
            return {"error": str(e)}
    try:
        aggregated = defaultdict(lambda: {"name": "", "total_quantity": 0})
        for item in all_items_raw:
            article = item["article"]    
            aggregated[article]["name"] = item["name"]
            aggregated[article]["total_quantity"] += item["quantity"]

        parsered_data_json = {article: {"Наименование": data["name"], "Количество": data["total_quantity"]} for article, data in aggregated.items()}    
        final_json = checking_components(parsered_data_json)
        if "error" in final_json:
            return final_json
        missing_details = final_json.get("недостающие", [])
        ending_details = final_json.get("заканчивающиеся", [])
        
        zip_file, zip_path = tempfile.mkstemp(suffix=".zip")
        os.close(zip_file)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            if missing_details:
                

                pdf_1_path = tempfile.mktemp(suffix='.pdf')
                generate_specification_pdf(missing_details, pdf_1_path)
                zipf.write(pdf_1_path, datetime.now().strftime("Документ на закупку недостающих деталей_%Y-%m-%d.pdf"))
                os.remove(pdf_1_path)
            if ending_details:
                
                pdf_2_path = tempfile.mktemp(suffix='.pdf')
                generate_specification_pdf(ending_details, pdf_2_path)
                zipf.write(pdf_2_path, datetime.now().strftime("Документ на закупку заканчивающихся деталей_%Y-%m-%d.pdf"))
                os.remove(pdf_2_path)
        return FileResponse(path=zip_path, filename=datetime.now().strftime("Документы на закупку_%Y-%m-%d.zip"), media_type="application/zip", background=BackgroundTask(cleanup_zip, zip_path))
    except Exception as e:
        return {"error": str(e)}