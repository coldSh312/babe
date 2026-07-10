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

def __init__(self, filepath=None):
        try:
            if "SHEET_URL" not in st.secrets:
                raise Exception("SHEET_URL חסר ב-Secrets!")
            if "GOOGLE_CREDENTIALS_JSON" not in st.secrets:
                raise Exception("GOOGLE_CREDENTIALS_JSON חסר ב-Secrets!")
                
            self.sheet_url = st.secrets["SHEET_URL"]
            creds_json = st.secrets["GOOGLE_CREDENTIALS_JSON"]
            creds_dict = json.loads(creds_json)
            
            self.client = gspread.service_account_from_dict(creds_dict)
            self.sheet = self.client.open_by_url(self.sheet_url).sheet1
        except Exception as e:
            logger.error(f"Critical connection error: {e}")
            raise StorageError(f"שגיאה בהתחברות לגוגל שיטס: {e}")
