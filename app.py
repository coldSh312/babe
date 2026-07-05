import streamlit as st
import pandas as pd
import re
import base64
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
    /* עיצוב כפתור מחיקה כדי שייראה בולט ומזהיר */
    button[kind="primary"] { background-color: #E5484D; color: white; border: none; }
    button[kind="primary"]:hover { background-color: #C93A3E; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- טעינת נתונים ---
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

def generate_printable_report(clinic_data: ClinicData) -> str:
    """מחולל קוד HTML מעוצב שמיועד להדפסה או לשמירה כ-PDF מהדפדפן"""
    
    # המרת מספר החודש לשם בעברית
    months_he = ["", "ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני", "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר"]
    month_name = months_he[clinic_data.default_month]
    
    html = f"""<!DOCTYPE html>
    <html dir="rtl" lang="he">
    <head>
        <meta charset="utf-8">
        <title>נוכחות שיקום יום - {month_name} {clinic_data.default_year}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; color: #333; }}
            h1 {{ text-align: center; color: #2F6FED; margin-bottom: 5px; }}
            h2 {{ text-align: center; color: #555; margin-top: 0; font-weight: normal; font-size: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 15px; page-break-inside: auto; }}
            tr {{ page-break-inside: avoid; page-break-after: auto; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
            th {{ background-color: #EEF2FB; color: #1F2430; }}
            .totals-row th {{ background-color: #E5F6EE; font-weight: bold; }}
            .summary-box {{ margin-top: 30px; padding: 15px; background-color: #F5F7FA; border-radius: 8px; border: 1px solid #E1E5EB; display: inline-block; }}
            .summary-box p {{ margin: 5px 0; font-size: 16px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>נוכחות שיקום יום</h1>
        <h2>{month_name} {clinic_data.default_year}</h2>
        <table>
            <thead>
                <tr>
                    <th>שם מטופל</th>
    """
    for d in clinic_data.dates:
        html += f"<th>{d}</th>"
    
    html += """
                </tr>
            </thead>
            <tbody>
    """
    for p in clinic_data.patients:
        html += f"<tr><td><strong>{p}</strong></td>"
        for d in clinic_data.dates:
            mark = "✔️" if clinic_data.is_present(p, d) else ""
            html += f"<td>{mark}</td>"
        html += "</tr>"
    
    html += """
            </tbody>
            <tfoot>
                <tr class="totals-row">
                    <th>סה"כ ליום</th>
    """
    for d in clinic_data.dates:
        html += f"<th>{clinic_data.get_date_total(d)}</th>"
        
    html += f"""
                </tr>
            </tfoot>
        </table>
        
        <div class="summary-box">
            <p>סה"כ טיפולים כולל: {clinic_data.get_grand_total()}</p>
            <p>מחיר לטיפול: {clinic_data.price_per_session:,.0f} ₪</p>
            <p style="color: #2FB380; font-size: 18px;">סה"כ הכנסה: {clinic_data.get_total_income():,.0f} ₪</p>
        </div>
        
        <script>
            // מקפיץ אוטומטית את חלון ההדפסה / חלון ה-PDF
            window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """
    return html

# --- סרגל צד ---
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
    new_names_input = st.text_area("מטופלים חדשים (מופרדים בשורה/פסיק):")
    selected_existing = st.multiselect("מטופלים קיימים:", data.patients)
    
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
    with st.expander("ניהול מחיקות נקודתיות", expanded=False):
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
            
    st.divider()
    with st.expander("⚠️ איפוס מערכת מלא", expanded=False):
        st.error("פעולה זו תמחק את כל המטופלים, התאריכים וסימוני הנוכחות. לא ניתן לשחזר לאחר מכן!")
        if st.button("כן, מחק את כל הנתונים", type="primary"):
            st.session_state.clinic_data = ClinicData(default_month=data.default_month, default_year=data.default_year)
            save_data()
            st.rerun()

# --- אזור ראשי: טבלה וסיכומים ---
st.title("נוכחות שיקום יום")

# בניית מסד הנתונים לטבלה המרכזית
df_dict = {"שם מטופל": data.patients}
for d in data.dates:
    df_dict[d] = [data.is_present(p, d) for p in data.patients]
df_dict["סה\"כ מטופל"] = [data.get_patient_total(p) for p in data.patients]

df = pd.DataFrame(df_dict)

st.subheader("טבלת נוכחות (ניתן לסמן/לבטל V ישירות מהטבלה)")

# הצגת הטבלה כאינטראקטיבית
disabled_cols = ["שם מטופל", "סה\"כ מטופל"]
edited_df = st.data_editor(
    df,
    disabled=disabled_cols,
    hide_index=True,
    use_container_width=True,
    key="attendance_editor"
)

# בדיקה אם המשתמש סימן/ביטל V בטבלה
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

# --- טבלת סה"כ ליום תחתית מסונכרנת ---
if data.dates:
    st.write("**סה\"כ טיפולים ליום:**")
    summary_data = {"שם מטופל": ["סה\"כ"]}
    for d in data.dates:
        summary_data[d] = [data.get_date_total(d)]
    summary_data["סה\"כ מטופל"] = [""] # עמודת דמי כדי לשמור על יישור מושלם מול הטבלה הראשית
    
    st.dataframe(
        pd.DataFrame(summary_data),
        hide_index=True,
        use_container_width=True
    )

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

st.write("---")
st.subheader("הפקת דוחות")

# כפתור ייצוא לדוח מותאם ל-PDF
report_html = generate_printable_report(data)
b64_report = base64.b64encode(report_html.encode('utf-8')).decode()

st.markdown(
    f"""
    <a href="data:text/html;base64,{b64_report}" download="attendance_report.html" style="text-decoration: none;">
        <div style="background-color: #2F6FED; color: white; padding: 10px 20px; border-radius: 5px; text-align: center; font-weight: bold; width: 100%; cursor: pointer; display: inline-block;">
            🖨️ לחץ כאן לייצוא הדוח / שמירה כ-PDF
        </div>
    </a>
    <p style="font-size: 12px; color: gray; text-align: center;">הדוח יירד למכשירך ויפתח אוטומטית חלון הדפסה. משם תוכל לבחור "שמור כ-PDF".</p>
    """,
    unsafe_allow_html=True
)