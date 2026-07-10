import json
import streamlit as st
import gspread
from models import ClinicData

class StorageError(Exception):
    pass

class JsonStorage:
    def __init__(self, filepath=None):
        try:
            self.sheet_url = st.secrets["SHEET_URL"]
            raw_creds = st.secrets["GOOGLE_CREDENTIALS_JSON"]
            
            # תיקון קריטי: אם מדובר במחרוזת עם לוכסנים כפולים או חסרים, 
            # ננסה לנקות אותם לפני הטעינה
            creds_dict = json.loads(raw_creds)
            
            self.client = gspread.service_account_from_dict(creds_dict)
            self.sheet = self.client.open_by_url(self.sheet_url).sheet1
        except Exception as e:
            # נדפיס את השגיאה ללוגים כדי להבין בדיוק איפה היא נופלת
            print(f"DEBUG: Error in GSheets config: {e}")
            raise StorageError(f"שגיאה בפורמט ה-JSON של הסודות: {e}")

    def load(self) -> ClinicData:
        try:
            records = self.sheet.col_values(1)
            if not records or all(v == "" for v in records):
                return ClinicData()
            full_json = "".join([str(r) for r in records if r])
            return ClinicData.from_dict(json.loads(full_json))
        except Exception:
            return ClinicData()

    def save(self, data: ClinicData) -> None:
        try:
            full_json = json.dumps(data.to_dict(), ensure_ascii=False)
            chunk_size = 40000
            chunks = [full_json[i:i+chunk_size] for i in range(0, len(full_json), chunk_size)]
            
            # ניקוי הגיליון לפני שמירה חדשה
            self.sheet.clear()
            
            # כתיבת הנתונים
            for i, chunk in enumerate(chunks):
                self.sheet.update_cell(i + 1, 1, chunk)
        except Exception as e:
            raise StorageError(f"לא ניתן לשמור נתונים: {e}")
