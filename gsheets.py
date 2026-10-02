import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ─────────────────────────────────────────────────────────
# CONFIGURACIÓN DE CONEXIÓN
# ─────────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(show_spinner="Conectando a Google Sheets...")
def init_connection():
    secrets = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(secrets, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
    return client.open_by_key(spreadsheet_id)

# ─────────────────────────────────────────────────────────
# LECTURA DE DATOS
# ─────────────────────────────────────────────────────────
def read_df(worksheet_name):
    try:
        sheet = init_connection().worksheet(worksheet_name)
        data = sheet.get_all_records()
        if not data:
            if worksheet_name == "Operaciones":
                return pd.DataFrame(columns=["ID_Operacion", "Fecha", "Tipo", "Cliente", "Concepto", "Hectareas", "Costo_HA", "Debe", "Haber"])
            elif worksheet_name == "Gastos":
                return pd.DataFrame(columns=["ID_Gasto", "Fecha", "Concepto", "Importe"])
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al leer la hoja {worksheet_name}: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────
# ESCRITURA DE DATOS
# ─────────────────────────────────────────────────────────
def generate_id(worksheet_name):
    df = read_df(worksheet_name)
    if df.empty:
        return 1
    try:
        col_id = "ID_Operacion" if worksheet_name == "Operaciones" else "ID_Gasto"
        return int(df[col_id].max()) + 1
    except:
        return len(df) + 1

def add_operation(tipo, cliente, concepto, fecha, hectareas=0, costo_ha=0, importe=0):
    try:
        sheet = init_connection().worksheet("Operaciones")
        new_id = generate_id("Operaciones")
        
        if tipo == "Vuelo" and importe == 0 and hectareas > 0 and costo_ha > 0:
            importe = float(hectareas) * float(costo_ha)
            
        debe = float(importe) if tipo == "Vuelo" else 0.0
        haber = float(importe) if tipo == "Abono" else 0.0
            
        row = [
            new_id,
            str(fecha),
            tipo,
            cliente,
            concepto,
            float(hectareas) if hectareas else 0,
            float(costo_ha) if costo_ha else 0,
            debe,
            haber
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error al guardar operación: {e}")
        return False

def add_expense(concepto, importe, fecha):
    try:
        sheet = init_connection().worksheet("Gastos")
        new_id = generate_id("Gastos")
        
        row = [
            new_id,
            str(fecha),
            concepto,
            float(importe)
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error al guardar gasto: {e}")
        return False