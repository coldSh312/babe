import streamlit as st
import pandas as pd
import re
import base64
from datetime import datetime

from models import ClinicData
from storage import JsonStorage
from settings import DATA_FILE, APP_NAME

# הגדרות עיצוב
st.set_page_config(page_title=APP_NAME, layout="wide")
st.markdown("<style>body { direction: rtl; text-align: right; }</style>", unsafe_allow_html=True)

# טעינת נתונים
@st.cache_resource
def get_storage():
    return JsonStorage(DATA_FILE)

storage = get_storage()

if "clinic_data" not in st.session_state:
    st.session_state.clinic_data = storage.load()

data: ClinicData = st.session_state.clinic_data

def save_and_refresh():
    storage.save(data)
    st.rerun()

# --- אזור הממשק ---
st.title("נוכחות שיקום יום")

# הטבלה המרכזית - שימוש ב-width='stretch' במקום use_container_width
df_dict = {"שם מטופל": data.patients}
for d in data.dates:
    df_dict[d] = [data.is_present(p, d) for p in data.patients]
df_dict["סה\"כ מטופל"] = [data.get_patient_total(p) for p in data.patients]

df = pd.DataFrame(df_dict)

edited_df = st.data_editor(
    df,
    disabled=["שם מטופל", "סה\"כ מטופל"],
    hide_index=True,
    width=None, # או 'stretch' אם יש בעיה
    key="attendance_editor"
)

# עדכון נתונים
if st.session_state.get("attendance_editor"):
    changes = False
    for i, row in edited_df.iterrows():
        p_name = row["שם מטופל"]
        for d in data.dates:
            if data.attendance[p_name][d] != bool(row[d]):
                data.attendance[p_name][d] = bool(row[d])
                changes = True
    if changes:
        save_and_refresh()

# (שאר הקוד נשאר ללא שינוי, רק ודא שכל ה-use_container_width הוחלפו ב-width="stretch")
