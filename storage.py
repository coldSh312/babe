"""
storage.py
==========
Persistence layer using Google Sheets.
"""
import json
import logging
import streamlit as st
import gspread
from models import ClinicData

logger = logging.getLogger(__name__)

class StorageError(Exception):
    pass

class JsonStorage:
    """שומר על שם המחלקה כדי לא לשבור קוד ישן, אבל מתחבר עכשיו לגוגל שיטס במקום לקובץ"""
    
    def __init__(self, filepath=None):
        try:
            self.sheet_url = st.secrets["SHEET_URL"]
            creds_json = st.secrets["GOOGLE_CREDENTIALS_JSON"]
            creds_dict = json.loads(creds_json)
            
            # התחברות אוטומטית לגוגל שיטס בעזרת gspread והסודות
            self.client = gspread.service_account_from_dict(creds_dict)
            self.sheet = self.client.open_by_url(self.sheet_url).sheet1
        except Exception as e:
            raise StorageError(f"שגיאה בהגדרות החיבור לגוגל שיטס. ודא שהסודות הוזנו נכון: {e}")

    def load(self) -> ClinicData:
        try:
            # מושך את כל הנתונים מהעמודה הראשונה
            records = self.sheet.col_values(1)
            if not records:
                return ClinicData()
            
            # מחבר את הבלוקים חזרה לטקסט אחד שלם
            full_json = "".join(records)
            data = json.loads(full_json)
            return ClinicData.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load from GSheets: {e}")
            return ClinicData()

    def save(self, data: ClinicData) -> None:
        try:
            full_json = json.dumps(data.to_dict(), ensure_ascii=False)
            # חלוקה לבלוקים כדי לעקוף את מגבלת 50,000 התווים לתא בגוגל שיטס
            chunk_size = 40000
            chunks = [full_json[i:i+chunk_size] for i in range(0, len(full_json), chunk_size)]
            
            # מכין את טווח העדכון (תמיד מנקה לפחות 10 תאים כדי למנוע שאריות של מידע ישן)
            num_cells = max(len(chunks), 10)
            cell_list = self.sheet.range(f'A1:A{num_cells}')
            
            for i, cell in enumerate(cell_list):
                if i < len(chunks):
                    cell.value = chunks[i]
                else:
                    cell.value = "" 
            
            self.sheet.update_cells(cell_list)
        except Exception as e:
            raise StorageError(f"לא ניתן לשמור נתונים לגוגל שיטס: {e}")
