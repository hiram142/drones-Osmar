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
    # Cargar credenciales desde st.secrets
    secrets = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(secrets, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # Abrir el documento usando el ID
    spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
    return client.open_by_key(spreadsheet_id)

# ─────────────────────────────────────────────────────────
# LECTURA DE DATOS
# ─────────────────────────────────────────────────────────
def read_df(worksheet_name):
    """Lee una hoja y la devuelve como DataFrame."""
    try:
        sheet = init_connection().worksheet(worksheet_name)
        data = sheet.get_all_records()
        if not data:
            # Si está vacío, devolvemos un DataFrame vacío pero con las columnas correctas
            if worksheet_name == "Operaciones":
                return pd.DataFrame(columns=["ID", "Tipo", "Cliente", "Concepto", "Fecha", "Hectareas", "Costo_ha", "Importe"])
            elif worksheet_name == "Gastos":
                return pd.DataFrame(columns=["ID", "Concepto", "Importe", "Fecha"])
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error al leer la hoja {worksheet_name}: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────────────────
# ESCRITURA DE DATOS
# ─────────────────────────────────────────────────────────
def generate_id(worksheet_name):
    """Genera un ID simple basado en el número de filas."""
    df = read_df(worksheet_name)
    if df.empty:
        return 1
    # Asume que la columna ID existe y es numérica
    try:
        return int(df["ID"].max()) + 1
    except:
        return len(df) + 1

def add_operation(tipo, cliente, concepto, fecha, hectareas=0, costo_ha=0, importe=0):
    """Añade un registro a la hoja 'Operaciones'."""
    try:
        sheet = init_connection().worksheet("Operaciones")
        new_id = generate_id("Operaciones")
        
        # Si es un vuelo y no tiene importe, lo calculamos
        if tipo == "Vuelo" and importe == 0 and hectareas > 0 and costo_ha > 0:
            importe = float(hectareas) * float(costo_ha)
            
        row = [
            new_id,
            tipo,
            cliente,
            concepto,
            str(fecha),
            float(hectareas) if hectareas else 0,
            float(costo_ha) if costo_ha else 0,
            float(importe)
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error al guardar operación: {e}")
        return False

def add_expense(concepto, importe, fecha):
    """Añade un registro a la hoja 'Gastos'."""
    try:
        sheet = init_connection().worksheet("Gastos")
        new_id = generate_id("Gastos")
        
        row = [
            new_id,
            concepto,
            float(importe),
            str(fecha)
        ]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error al guardar gasto: {e}")
        return False