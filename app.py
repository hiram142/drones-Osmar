"""
Drones de fumigación · Osmar y Erick
App Streamlit mobile-first conectada a Google Sheets vía Lumina.
"""
from __future__ import annotations

import html
from datetime import date

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────
# 1. CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
PCT_OSMAR = 0.60
PCT_ERICK = 0.40
TIPOS_GASTO = ["Combustible", "Agroquímicos", "Mantenimiento", "Baterías / refacciones",
               "Viáticos", "Sueldos / ayudantes", "Otro"]
METODOS_PAGO = ["Efectivo", "Transferencia", "Cheque", "Otro"]

st.set_page_config(page_title="Fumigación · Control", page_icon="🚁",
                   layout="centered", initial_sidebar_state="collapsed")

# ─────────────────────────────────────────────────────────────
# 2. CAPA DE DATOS
# ─────────────────────────────────────────────────────────────
try:
    import gsheets as lumina
    LUMINA_OK = True
except ImportError:
    LUMINA_OK = False

# Agregamos Hectareas y Costo_HA para que la tabla las pueda mostrar
COLS_OPS = ["Fecha", "Cliente", "Concepto", "Hectareas", "Costo_HA", "Debe", "Haber"]
COLS_GAS = ["Fecha", "Concepto", "Importe"] 

def _demo_state() -> None:
    if "demo_ops" not in st.session_state:
        st.session_state.demo_ops = pd.DataFrame([
            ["2026-09-02", "Rancho La Esperanza", "Vuelo · Maíz", 40, 250, 10000, 0],
            ["2026-09-10", "Rancho La Esperanza", "Abono · Efectivo", 0, 0, 0, 4000],
        ], columns=COLS_OPS)
        st.session_state.demo_gas = pd.DataFrame(
            [["2026-09-03", "Combustible", 850]], columns=COLS_GAS)

@st.cache_data(ttl=30, show_spinner=False)
def leer_operaciones(_v: int) -> pd.DataFrame:
    df = (lumina.read_df("Operaciones") if LUMINA_OK else
          (_demo_state(), st.session_state.demo_ops)[1])
    df = pd.DataFrame(df).reindex(columns=COLS_OPS)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    for c in ("Debe", "Haber", "Hectareas", "Costo_HA"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    return df

@st.cache_data(ttl=30, show_spinner=False)
def leer_gastos(_v: int) -> pd.DataFrame:
    df = (lumina.read_df("Gastos") if LUMINA_OK else
          (_demo_state(), st.session_state.demo_gas)[1])
    df = pd.DataFrame(df).reindex(columns=COLS_GAS)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce").fillna(0.0)
    return df

def guardar_vuelo(fecha, cliente, cultivo, hectareas, precio_ha, notas) -> None:
    concepto = f"Vuelo · {cultivo}" + (f" · {notas}" if notas else "")
    if LUMINA_OK:
        lumina.add_operation(tipo="Vuelo", cliente=cliente, concepto=concepto, 
                             fecha=str(fecha), hectareas=hectareas, costo_ha=precio_ha)
    else:
        _demo_state()
        total = round(hectareas * precio_ha, 2)
        st.session_state.demo_ops.loc[len(st.session_state.demo_ops)] = [str(fecha), cliente, concepto, hectareas, precio_ha, total, 0]

def guardar_abono(fecha, cliente, monto, metodo, notas) -> None:
    concepto = f"Abono · {metodo}" + (f" · {notas}" if notas else "")
    if LUMINA_OK:
        lumina.add_operation(tipo="Abono", cliente=cliente, concepto=concepto, 
                             fecha=str(fecha), importe=monto)
    else:
        _demo_state()
        st.session_state.demo_ops.loc[len(st.session_state.demo_ops)] = [str(fecha), cliente, concepto, 0, 0, 0, monto]

def guardar_gasto(fecha, tipo, monto, notas) -> None:
    concepto = tipo + (f" · {notas}" if notas else "")
    if LUMINA_OK:
        lumina.add_expense(concepto=concepto, importe=monto, fecha=str(fecha))
    else:
        _demo_state()
        st.session_state.demo_gas.loc[len(st.session_state.demo_gas)] = [str(fecha), concepto, monto]

# ─────────────────────────────────────────────────────────────
# 3. ESTILO MOBILE-FIRST 
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root{--ink:#14201a;--field:#1b5e36;--field-dark:#123f25;--sun:#f2b705;--paper:#fffdf7;--line:#d9d4c3;--debt:#b3261e;}
.stApp{background:var(--paper);color:var(--ink);}
.block-container{padding:1rem 1rem 4rem;max-width:640px;}
html,body,[class*="css"]{font-size:18px;}
h1{font-size:1.7rem!important;margin-bottom:.2rem;}
h2,h3{font-size:1.3rem!important;}
.stTextInput input,.stNumberInput input,.stDateInput input,.stTextArea textarea,
.stSelectbox div[data-baseweb="select"]>div{min-height:3.4rem;font-size:1.15rem!important;border:2px solid var(--ink)!important;border-radius:12px!important;background:#fff;}
.stButton>button,.stDownloadButton>button{width:100%;min-height:3.6rem;font-size:1.2rem;font-weight:700;border-radius:14px;border:2px solid var(--field-dark);}
.stButton>button[kind="primary"]{background:var(--field);color:#fff;}
.stTabs [data-baseweb="tab-list"]{gap:0;border-bottom:3px solid var(--ink);}
.stTabs [data-baseweb="tab"]{flex:1;height:3.4rem;font-size:1rem;font-weight:700;padding:0 .2rem;}
.stTabs [aria-selected="true"]{background:var(--sun);color:var(--ink);}
.big{background:#fff;border:2px solid var(--ink);border-radius:16px;padding:1rem 1.1rem;margin:.6rem 0;}
.big .lbl{font-size:1rem;color:#4a5a50;}
.big .num{font-size:2.1rem;font-weight:800;line-height:1.15;}
.big.saldo{border-color:var(--debt);} .big.saldo .num{color:var(--debt);}
.big.ok .num{color:var(--field);}
.big.total{background:var(--field);color:#fff;border-color:var(--field-dark);} .big.total .lbl{color:#d6e8dc;}
</style>
""", unsafe_allow_html=True)

def money(x: float) -> str:
    return f"${x:,.2f}" if x >= 0 else f"-${abs(x):,.2f}"

def card(label: str, value: str, cls: str = "") -> None:
    st.markdown(f'<div class="big {cls}"><div class="lbl">{html.escape(label)}</div>'
                f'<div class="num">{html.escape(value)}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# 4. ESTADO DE SESIÓN
# ─────────────────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("v", 0)       
ss.setdefault("form_v", 0)  

ops = leer_operaciones(ss.v)
gastos = leer_gastos(ss.v)
clientes = sorted(c for c in ops["Cliente"].dropna().astype(str).str.strip().unique() if c)

def terminar_guardado(msg: str) -> None:
    ss.v += 1
    ss.form_v += 1
    st.toast(msg, icon="✅")
    st.rerun()

# ─────────────────────────────────────────────────────────────
# 5. INTERFAZ EN PESTAÑAS
# ─────────────────────────────────────────────────────────────
st.title("🚁 Control de fumigación")
if not LUMINA_OK:
    st.warning("Modo demo: no se encontró el módulo `gsheets.py` o faltan credenciales.")

tab_reg, tab_cta, tab_fin = st.tabs(["📝 Registro", "👤 Cuenta", "📊 Finanzas"])

# ── 📝 REGISTRO ──────────────────────────────────────────────
with tab_reg:
    tipo = st.selectbox("¿Qué vas a registrar?", ["🚁 Vuelo", "💵 Abono", "⛽ Gasto"], key="tipo_registro")
    k = ss.form_v  

    def elegir_cliente() -> str:
        opciones = clientes + ["➕ Cliente nuevo"]
        sel = st.selectbox("Cliente", opciones, key=f"cli_{k}")
        if sel == "➕ Cliente nuevo":
            return st.text_input("Nombre del cliente nuevo", key=f"cli_nuevo_{k}").strip()
        return sel

    if tipo.endswith("Vuelo"):
        cliente = elegir_cliente()
        fecha = st.date_input("Fecha", value=date.today(), key=f"f_{k}")
        cultivo = st.text_input("Cultivo", placeholder="Maíz, chile, caña…", key=f"cul_{k}").strip()
        hectareas = st.number_input("Hectáreas fumigadas", min_value=0.0, step=1.0, format="%.2f", key=f"ha_{k}")
        precio = st.number_input("Precio por hectárea ($)", min_value=0.0, step=10.0, format="%.2f", key=f"pr_{k}")
        notas = st.text_input("Notas (opcional)", key=f"n_{k}").strip()
        total = round(hectareas * precio, 2)
        card("Total del vuelo (se suma a lo que debe el cliente)", money(total), "total")

        errores = []
        if not cliente: errores.append("Elige o escribe el cliente.")
        if not cultivo: errores.append("Escribe el cultivo.")
        if hectareas <= 0: errores.append("Las hectáreas deben ser mayores a 0.")
        if precio <= 0: errores.append("El precio por hectárea debe ser mayor a 0.")
        for e in errores: st.caption(f"⚠️ {e}")
        if st.button("Guardar vuelo", type="primary", disabled=bool(errores), key=f"b_v_{k}"):
            try:
                guardar_vuelo(fecha, cliente, cultivo, hectareas, precio, notas)
            except Exception as exc:
                st.error(f"No se pudo guardar. ({exc})")
            else:
                terminar_guardado(f"Vuelo guardado: {cliente} · {money(total)}")

    elif tipo.endswith("Abono"):
        cliente = elegir_cliente()
        if cliente in clientes:
            saldo_actual = ops.loc[ops["Cliente"] == cliente, "Debe"].sum() - ops.loc[ops["Cliente"] == cliente, "Haber"].sum()
            st.caption(f"Saldo pendiente actual de {cliente}: **{money(saldo_actual)}**")
        fecha = st.date_input("Fecha", value=date.today(), key=f"f_{k}")
        monto = st.number_input("Monto recibido ($)", min_value=0.0, step=100.0, format="%.2f", key=f"m_{k}")
        metodo = st.selectbox("Forma de pago", METODOS_PAGO, key=f"mp_{k}")
        notas = st.text_input("Notas (opcional)", key=f"n_{k}").strip()
        errores = []
        if not cliente: errores.append("Elige o escribe el cliente.")
        if monto <= 0: errores.append("El monto debe ser mayor a 0.")
        for e in errores: st.caption(f"⚠️ {e}")
        if st.button("Guardar abono", type="primary", disabled=bool(errores), key=f"b_a_{k}"):
            try:
                guardar_abono(fecha, cliente, monto, metodo, notas)
            except Exception as exc:
                st.error(f"No se pudo guardar. ({exc})")
            else:
                terminar_guardado(f"Abono guardado: {cliente} · {money(monto)}")

    else:  # Gasto
        fecha = st.date_input("Fecha", value=date.today(), key=f"f_{k}")
        tipo_gasto = st.selectbox("Tipo de gasto", TIPOS_GASTO, key=f"tg_{k}")
        monto = st.number_input("Monto ($)", min_value=0.0, step=50.0, format="%.2f", key=f"m_{k}")
        notas = st.text_input("Notas (opcional)", key=f"n_{k}").strip()
        errores = [] if monto > 0 else ["El monto debe ser mayor a 0."]
        for e in errores: st.caption(f"⚠️ {e}")
        if st.button("Guardar gasto", type="primary", disabled=bool(errores), key=f"b_g_{k}"):
            try:
                guardar_gasto(fecha, tipo_gasto, monto, notas)
            except Exception as exc:
                st.error(f"No se pudo guardar. ({exc})")
            else:
                terminar_guardado(f"Gasto guardado: {tipo_gasto} · {money(monto)}")

# ── 👤 ESTADO DE CUENTA (Control Interno por Cliente) ────────
with tab_cta:
    st.header("👥 Control Interno por Cliente")
    if not clientes:
        st.info("Aún no hay clientes registrados.")
    else:
        cli = st.selectbox("Selecciona un cliente para ver su historial:", clientes, key="cli_cuenta")
        historial = ops[ops["Cliente"].astype(str).str.strip() == cli].copy()
        
        if not historial.empty:
            # Organizar la tabla al estilo Excel
            historial = historial.sort_values("Fecha", ascending=False)
            historial['DEBE (Cargos)'] = historial['Debe']
            historial['HABER (Abonos)'] = historial['Haber']
            
            # Mostrar tabla
            tabla_mostrar = historial[['Fecha', 'Concepto', 'Hectareas', 'Costo_HA', 'DEBE (Cargos)', 'HABER (Abonos)']]
            st.dataframe(tabla_mostrar, hide_index=True, use_container_width=True)
            
            # Cálculo de saldo
            debe = historial["DEBE (Cargos)"].sum()
            haber = historial["HABER (Abonos)"].sum()
            saldo = debe - haber

            if saldo > 0.005:
                card("Saldo pendiente por cobrar", money(saldo), "saldo")
            else:
                card("Estado del cliente", "Al corriente ✔" if abs(saldo) <= 0.005 else f"A favor {money(-saldo)}", "ok")
        else:
            st.info("Este cliente no tiene movimientos.")

# ── 📊 FINANZAS (Resumen financiero y utilidades) ────────────
with tab_fin:
    st.header("📊 Resumen Financiero")
    ingresos = ops["Haber"].sum()          
    total_gastos = gastos["Importe"].sum() 
    utilidad = ingresos - total_gastos
    por_cobrar = ops["Debe"].sum() - ops["Haber"].sum()

    card("Ingresos Reales (Abonos)", money(ingresos), "ok")
    card("Gastos Totales", money(total_gastos))
    card("Utilidad Neta", money(utilidad), "total")
    
    if utilidad < 0:
        st.warning("Los gastos superan lo cobrado. La pérdida se reparte con el mismo porcentaje.")

    st.subheader("Reparto de utilidad")
    r1, r2 = st.columns(2)
    with r1: card(f"Osmar · {PCT_OSMAR:.0%}", money(utilidad * PCT_OSMAR))
    with r2: card(f"Erick · {PCT_ERICK:.0%}", money(utilidad * PCT_ERICK))
    st.caption(f"Por cobrar a clientes (no incluido en la utilidad): {money(por_cobrar)}")

    st.divider()
    st.subheader("Descargar datos")
    stamp = date.today().isoformat()
    st.download_button("⬇️ Operaciones (CSV)", ops.to_csv(index=False).encode("utf-8-sig"),
                       f"operaciones_{stamp}.csv", "text/csv", key="dl_ops")
    st.download_button("⬇ Gastos (CSV)", gastos.to_csv(index=False).encode("utf-8-sig"),
                       f"gastos_{stamp}.csv", "text/csv", key="dl_gas")