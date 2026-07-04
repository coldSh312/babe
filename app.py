import streamlit as st
import pandas as pd
import re
from datetime import datetime

from models import ClinicData
from storage import JsonStorage
from settings import DATA_FILE, APP_NAME

# --- הגדרות בסיסיות ותמיכה בעברית (RTL) ---
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown("""
    <style>
    body, .stApp, .st-emotion-cache-16txtl3 {
        direction: rtl;
        text-align: right;
        font-family: "Segoe UI", sans-serif;
    }
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        direction: rtl;
    }
    .st-emotion-cache-1kyxreq { justify-content: flex-end; }
    </style>
""", unsafe_allow_html=True)

# --- טעינת נתונים (נטען פעם אחת ונשמר ב-Session) ---
@st.cache_resource
def get_storage():
    return JsonStorage(DATA_FILE)

storage = get_storage()

if "clinic_data" not in st.session_state:
    try:
        st.session_state.clinic_data = storage.load()
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {e}")
        st.session_state.clinic_data = ClinicData()

data: ClinicData = st.session_state.clinic_data

def save_data():
    storage.save(data)

def smart_parse_date(date_str: str, d_month: int, d_year: int) -> str:
    val = date_str.strip().replace('.', '/')
    parts = val.split('/')
    try:
        if len(parts) == 1:
            dt = datetime(d_year, d_month, int(parts[0]))
        elif len(parts) == 2:
            dt = datetime(d_year, int(parts[1]), int(parts[0]))
        else:
            formats = ["%d/%m/%Y", "%d/%m/%y"]
            for fmt in formats:
                try:
                    return datetime.strptime(val, fmt).strftime("%d/%m/%Y")
                except ValueError:
                    pass
            raise ValueError
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        raise ValueError("פורמט תאריך לא חוקי. אנא הזן יום תקין.")

# --- סרגל צד: הזנה מהירה והגדרות ---
with st.sidebar:
    st.header("⚙️ הגדרות והזנה")
    
    with st.expander("הגדרות חודש ושנה", expanded=False):
        new_month = st.number_input("חודש ברירת מחדל", 1, 12, data.default_month)
        new_year = st.number_input("שנת ברירת מחדל", 2000, 2100, data.default_year)
        if new_month != data.default_month or new_year != data.default_year:
            data.default_month = new_month
            data.default_year = new_year
            save_data()
    
    st.divider()
    st.subheader("הזנת נוכחות מרוכזת")
    
    date_input = st.text_input("יום או תאריך מלא (למשל: 5):")
    selected_existing = st.multiselect("מטופלים קיימים:", data.patients)
    new_names_input = st.text_area("מטופלים חדשים (מופרדים בשורה/פסיק):")
    
    if st.button("סמן נוכחות לתאריך זה", use_container_width=True):
        if not date_input:
            st.warning("נא להזין תאריך")
        else:
            try:
                norm_date = smart_parse_date(date_input, data.default_month, data.default_year)
                data.add_date(norm_date)
                
                all_names = set(selected_existing)
                for name in re.split(r'[,\n]+', new_names_input):
                    cname = name.strip()
                    if cname: all_names.add(cname)
                    
                for cname in all_names:
                    if cname not in data.patients:
                        data.add_patient(cname)
                    data.attendance[cname][norm_date] = True
                    
                save_data()
                st.success(f"עודכן בהצלחה לתאריך {norm_date}!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.divider()
    with st.expander("ניהול מחיקות", expanded=False):
        st.write("בממשק הווב לא ניתן ללחוץ מקש ימני. מחק מכאן:")
        del_patient = st.selectbox("בחר מטופל למחיקה:", [""] + data.patients)
        if st.button("מחק מטופל") and del_patient:
            data.remove_patient(del_patient)
            save_data()
            st.rerun()
            
        del_date = st.selectbox("בחר תאריך למחיקה:", [""] + data.dates)
        if st.button("מחק תאריך") and del_date:
            data.remove_date(del_date)
            save_data()
            st.rerun()

# --- אזור ראשי: טבלה וסיכומים ---
st.title(APP_NAME)

# בניית מסד הנתונים לטבלה
df_dict = {"שם מטופל": data.patients}
for d in data.dates:
    df_dict[d] = [data.is_present(p, d) for p in data.patients]
df_dict["סה\"כ מפגשים"] = [data.get_patient_total(p) for p in data.patients]

df = pd.DataFrame(df_dict)

st.subheader("טבלת נוכחות (ניתן לסמן/לבטל V ישירות מהטבלה)")

# הצגת הטבלה כאינטראקטיבית (data_editor)
disabled_cols = ["שם מטופל", "סה\"כ מפגשים"]
edited_df = st.data_editor(
    df,
    disabled=disabled_cols,
    hide_index=True,
    use_container_width=True,
    key="attendance_editor"
)

# בדיקה אם המשתמש סימן/ביטל V בטבלה ועדכון הלוגיקה בהתאם
changes_made = False
for i, row in edited_df.iterrows():
    p_name = row["שם מטופל"]
    for d in data.dates:
        is_checked = bool(row[d])
        if data.attendance[p_name][d] != is_checked:
            data.attendance[p_name][d] = is_checked
            changes_made = True
            
if changes_made:
    save_data()
    st.rerun()

# --- שורת סיכום יומית ---
cols = st.columns(len(data.dates) + 2)
cols[0].write("**סה\"כ ליום:**")
for idx, d in enumerate(data.dates):
    cols[idx+1].write(f"**{data.get_date_total(d)}**")
    
st.divider()

# --- הכנסות וייצוא ---
col1, col2 = st.columns(2)
with col1:
    new_price = st.number_input("מחיר לטיפול (₪)", min_value=0.0, step=10.0, value=data.price_per_session)
    if new_price != data.price_per_session:
        data.price_per_session = new_price
        save_data()
        st.rerun()
        
with col2:
    st.metric("סה\"כ הכנסה", f"₪ {data.get_total_income():,.0f}")
    st.metric("סה\"כ כל המפגשים", data.get_grand_total())

# כפתור הורדה לאקסל (עם קידוד מיוחד שתומך בעברית)
csv_data = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 ייצא נתונים לאקסל (CSV)",
    data=csv_data,
    file_name="attendance_export.csv",
    mime="text/csv"
)