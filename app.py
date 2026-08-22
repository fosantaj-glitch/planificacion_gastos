import streamlit as st
import pandas as pd
from datetime import date
import requests
import json
import time

# Configuración de la página
st.set_page_config(page_title="Control Financiero", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🎨 CSS AVANZADO: DISEÑO CORPORATIVO Y ELEGANTE
# ==========================================
st.markdown("""
    <style>
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}

    /* Fondo general: Perla / Pizarra ultra limpio y sofisticado */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }

    /* Tipografía General */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* TÍTULO PRINCIPAL */
    .titulo-principal {
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: 1.5px !important;
        line-height: 1.1 !important;
        margin-bottom: 0 !important;
        text-transform: uppercase;
    }

    .subtitulo-marca {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #D97706 !important; /* Acento cálido / dorado */
        letter-spacing: 3px !important;
        text-transform: uppercase;
        margin-top: 5px !important;
        margin-bottom: 25px !important;
    }

    /* TARJETAS DE MÉTRICAS / KPIS */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.05);
    }
    .kpi-titulo {
        font-size: 11px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-valor {
        font-size: 22px;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }

    /* FORMULARIOS Y CONTENEDORES FLOTANTES */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0px 10px 20px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid #E2E8F0;
    }

    /* BORDES Y CAJAS DE ENTRADA COMPACTAS */
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {
        border-radius: 6px !important;
        border: 1px solid #CBD5E1 !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
        border-color: #D97706 !important;
        box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.15) !important;
    }

    /* BOTONES ESTILIZADOS */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button[type="primary"] {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(15, 23, 42, 0.20) !important;
    }
    div.stButton > button[type="primary"]:hover {
        background: linear-gradient(135deg, #334155 0%, #1E293B 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 14px rgba(15, 23, 42, 0.30) !important;
    }

    /* ETIQUETAS DE ESTADO (PASTILLAS) */
    .estado-pendiente { color: #DC2626; font-weight: 700; background-color: #FEE2E2; padding: 4px 12px; border-radius: 20px; font-size: 12px; display: inline-block;}
    .estado-pagado { color: #16A34A; font-weight: 700; background-color: #DCFCE7; padding: 4px 12px; border-radius: 20px; font-size: 12px; display: inline-block;}
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES BASE DE DATOS (NUBE) BLINDADAS ---
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbx9lOCIm2IZNuDeLl8xmBL8QSR5sekd12Ngx3cELrNvYYefhuVJN6VhgBdezNcfiijo/exec"

def cargar_datos_desde_nube():
    try:
        res = requests.get(URL_WEB_APP, allow_redirects=True)
        if res.status_code in [200, 201]:
            data = res.json()
            if len(data) > 1:
                return pd.DataFrame(data[1:], columns=data[0])
            elif len(data) == 1:
                return pd.DataFrame(columns=data[0])
        else:
            st.error(f"⚠️ Error al descargar desde Google: {res.status_code}")
    except Exception as e:
        st.error(f"⚠️ Error de conexión con Google Sheets: {e}")
    return pd.DataFrame()

def estructurar_datos_para_guardar():
    filas = []
    for periodo, monto in st.session_state.ingresos.items():
        filas.append({'Periodo': periodo, 'Categoria': 'Ingreso', 'ID_Relacionado': '', 'Descripcion': 'Total Recibido', 'Monto': monto, 'Fecha': '', 'Comision': 0, 'IVA': 0, 'Estado': ''})
    for mes, valor in st.session_state.decimo_tercero_meses.items():
        filas.append({'Periodo': 'Décimo Tercero', 'Categoria': 'Mes Decimo', 'ID_Relacionado': mes, 'Descripcion': 'Salario Mensual', 'Monto': valor, 'Fecha': '', 'Comision': 0, 'IVA': 0, 'Estado': ''})
    for periodo, df_prog in st.session_state.gastos_fijos.items():
        for _, row in df_prog.iterrows():
            filas.append({'Periodo': periodo, 'Categoria': 'Programacion', 'ID_Relacionado': row['ID'], 'Descripcion': row['Gasto'], 'Monto': row['Monto_Programado'], 'Fecha': '', 'Comision': row['Comision_Prog'], 'IVA': row['IVA_Prog'], 'Estado': row['Estado']})
    for periodo, df_pagos in st.session_state.pagos_reales.items():
        for _, row in df_pagos.iterrows():
            filas.append({'Periodo': periodo, 'Categoria': 'Pago Real', 'ID_Relacionado': row['ID_Gasto'], 'Descripcion': 'Pago ejecutado', 'Monto': row['Monto_Pagado'], 'Fecha': row['Fecha'], 'Comision': row['Comision'], 'IVA': row['IVA_Comision'], 'Estado': 'Pagado'})
    return pd.DataFrame(filas)

def guardar_datos_en_nube():
    try:
        df_consolidado = estructurar_datos_para_guardar()
        df_clean = df_consolidado.fillna("").astype(str)
        data_list = [df_clean.columns.tolist()]
        for row in df_clean.itertuples(index=False, name=None):
            data_list.append(list(row))
        payload = {"action": "overwrite", "data": data_list}
        res = requests.post(URL_WEB_APP, json=payload, allow_redirects=True)
        
        if res.status_code not in [200, 201]:
            st.error(f"⚠️ Google rechazó los datos. Error: {res.status_code}")
            return False
        return True
    except Exception as e:
        st.error(f"⚠️ Ocurrió un error al intentar enviar los datos: {e}")
        return False

# --- SISTEMA DE LOGIN DE ALTO IMPACTO ---
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            st.session_state["usuario_actual"] = st.session_state["username"] 
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown('<p class="titulo-principal" style="text-align:center;">CONTROL FINANCIERO</p>', unsafe_allow_html=True)
            st.markdown('<p class="subtitulo-marca" style="text-align:center;">PROGRAMACIÓN Y PAGOS INTELIGENTES</p>', unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 20px;'>🔒 Iniciar Sesión</h4>", unsafe_allow_html=True)
                st.text_input("Usuario", key="username")
                st.text_input("Contraseña", type="password", key="password")
                st.write("<br>", unsafe_allow_html=True)
                st.form_submit_button("ACCEDER AL PANEL", on_click=password_entered, use_container_width=True, type="primary")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Credenciales incorrectas. Verifica tus datos.")
        return False
    return True

# --- EJECUCIÓN APP ---
if check_password():
    
    # CABECERA EMPRESARIAL
    st.markdown('<p class="titulo-principal">📊 PANEL FINANCIERO</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-marca">Gestión Estratégica de Presupuesto y Gastos</p>', unsafe_allow_html=True)
    
    # PROTECCIÓN CONTRA ERRORES DE CACHÉ
    if 'mes_operativo' not in st.session_state:
        st.session_state.mes_operativo = "Agosto"
    if 'anio_operativo' not in st.session_state:
        st.session_state.anio_operativo = 2026

    if 'datos_cargados' not in st.session_state:
        st.session_state.ingresos = {'Mes Regular': 0.0, 'Décimo Tercero': 0.0, 'Décimo Cuarto': 0.0}
        st.session_state.decimo_tercero_meses = {
            'Diciembre': 0.0, 'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 
            'Abril': 0.0, 'Mayo': 0.0, 'Junio': 0.0, 'Julio': 0.0, 
            'Agosto': 0.0, 'Septiembre': 0.0, 'Octubre': 0.0, 'Noviembre': 0.0
        }
        
        estructura_base = pd.DataFrame(columns=['ID', 'Gasto', 'Monto_Programado', 'Comision_Prog', 'IVA_Prog', 'Estado'])
        st.session_state.gastos_fijos = {'Mes Regular': estructura_base.copy(), 'Décimo Tercero': estructura_base.copy(), 'Décimo Cuarto': estructura_base.copy()}
        
        estructura_pagos = pd.DataFrame(columns=['ID_Gasto', 'Fecha', 'Monto_Pagado', 'Comision', 'IVA_Comision'])
        st.session_state.pagos_reales = {'Mes Regular': estructura_pagos.copy(), 'Décimo Tercero': estructura_pagos.copy(), 'Décimo Cuarto': estructura_pagos.copy()}

        with st.spinner("Descargando base de datos segura... ⏳"):
            df_cloud = cargar_datos_desde_nube()
            if not df_cloud.empty:
                ing_df = df_cloud[df_cloud['Categoria'] == 'Ingreso']
                for _, row in ing_df.iterrows():
                    if row['Periodo'] in st.session_state.ingresos:
                        try: st.session_state.ingresos[row['Periodo']] = float(row['Monto'])
                        except: pass
                
                meses_df = df_cloud[df_cloud['Categoria'] == 'Mes Decimo']
                for _, row in meses_df.iterrows():
                    if row['ID_Relacionado'] in st.session_state.decimo_tercero_meses:
                        try: st.session_state.decimo_tercero_meses[row['ID_Relacionado']] = float(row['Monto'])
                        except: pass
                
                prog_df = df_cloud[df_cloud['Categoria'] == 'Programacion']
                for periodo in ['Mes Regular', 'Décimo Tercero', 'Décimo Cuarto']:
                    p_df = prog_df[prog_df['Periodo'] == periodo]
                    if not p_df.empty:
                        df_to_save = pd.DataFrame({
                            'ID': p_df['ID_Relacionado'].values,
                            'Gasto': p_df['Descripcion'].values,
                            'Monto_Programado': pd.to_numeric(p_df['Monto'], errors='coerce').fillna(0.0),
                            'Comision_Prog': pd.to_numeric(p_df['Comision'], errors='coerce').fillna(0.0),
                            'IVA_Prog': pd.to_numeric(p_df['IVA'], errors='coerce').fillna(0.0),
                            'Estado': p_df['Estado'].values
                        })
                        st.session_state.gastos_fijos[periodo] = df_to_save

                pagos_df = df_cloud[df_cloud['Categoria'] == 'Pago Real']
                for periodo in ['Mes Regular', 'Décimo Tercero', 'Décimo Cuarto']:
                    p_df = pagos_df[pagos_df['Periodo'] == periodo]
                    if not p_df.empty:
                        df_to_save = pd.DataFrame({
                            'ID_Gasto': p_df['ID_Relacionado'].values,
                            'Fecha': p_df['Fecha'].values,
                            'Monto_Pagado': pd.to_numeric(p_df['Monto'], errors='coerce').fillna(0.0),
                            'Comision': pd.to_numeric(p_df['Comision'], errors='coerce').fillna(0.0),
                            'IVA_Comision': pd.to_numeric(p_df['IVA'], errors='coerce').fillna(0.0)
                        })
                        st.session_state.pagos_reales[periodo] = df_to_save

        st.session_state.datos_cargados = True

    # NAVEGACIÓN COMPACTA
    periodo_actual = st.radio("SELECCIONA EL PERIODO DE GESTIÓN:", ['Mes Regular', 'Décimo Tercero', 'Décimo Cuarto'], horizontal=True)

    # ====================================================
    # PARÁMETROS SUPERIORES COMPACTOS (UNIFICADOS EN UNA SOLA FILA)
    # ====================================================
    st.write("<br>", unsafe_allow_html=True)
    
    if periodo_actual == 'Mes Regular':
        with st.form("form_parametros_mes"):
            st.markdown("<h5 style='color:#0F172A; font-weight:700;'>⚙️ Parámetros del Mes</h5>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 1.5])
            with c1:
                meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                nuevo_mes = st.selectbox("Mes", meses, index=meses.index(st.session_state.mes_operativo))
            with c2:
                anios = [2026, 2027, 2028, 2029, 2030]
                nuevo_anio = st.selectbox("Año", anios, index=anios.index(st.session_state.anio_operativo))
            with c3:
                val_ing = st.session_state.ingresos[periodo_actual]
                nuevo_ingreso_raw = st.number_input("Presupuesto Inicial ($)", min_value=0.0, value=val_ing if val_ing > 0 else None, placeholder="0.00", step=50.0, format="%.2f")
            with c4:
                st.write("<br>", unsafe_allow_html=True)
                if st.form_submit_button("💾 Actualizar", type="primary", use_container_width=True):
                    st.session_state.mes_operativo = nuevo_mes
                    st.session_state.anio_operativo = nuevo_anio
                    st.session_state.ingresos[periodo_actual] = nuevo_ingreso_raw if nuevo_ingreso_raw is not None else 0.0
                    with st.spinner("Guardando en la nube... ⏳"):
                        guardar_datos_en_nube()
                    st.rerun()

    elif periodo_actual == 'Décimo Tercero':
        with st.form("form_calculadora_decimo"):
            st.markdown("<h5 style='color:#0F172A; font-weight:700;'>📅 Calculadora de Remuneraciones (Dic - Nov)</h5>", unsafe_allow_html=True)
            cols = st.columns(6) # Más compacto: 6 meses por fila
            meses_lista = list(st.session_state.decimo_tercero_meses.keys())
            
            for i, mes in enumerate(meses_lista):
                with cols[i % 6]:
                    val_actual = st.session_state.decimo_tercero_meses[mes]
                    val_ingresado_raw = st.number_input(f"{mes[:3]}.", value=val_actual if val_actual > 0 else None, placeholder="0", step=50.0)
                    st.session_state.decimo_tercero_meses[mes] = val_ingresado_raw if val_ingresado_raw is not None else 0.0
            
            total_percibido = sum(st.session_state.decimo_tercero_meses.values())
            decimo_calculado = total_percibido / 12 if total_percibido > 0 else 0.0
            
            c_res1, c_res2, c_btn = st.columns([2, 2, 2])
            with c_res1: st.info(f"**Total Percibido:** ${total_percibido:.2f}")
            with c_res2: st.success(f"**Décimo Calculado:** ${decimo_calculado:.2f}")
            with c_btn:
                if st.form_submit_button("💾 Guardar Décimo", type="primary", use_container_width=True):
                    st.session_state.ingresos['Décimo Tercero'] = decimo_calculado
                    with st.spinner("Sincronizando... ⏳"):
                        guardar_datos_en_nube()
                    st.rerun()
                    
    elif periodo_actual == 'Décimo Cuarto':
        with st.form(f"form_ingreso_{periodo_actual}"):
            st.markdown("<h5 style='color:#0F172A; font-weight:700;'>⚙️ Parámetros del Décimo Cuarto</h5>", unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                val_ing = st.session_state.ingresos[periodo_actual]
                nuevo_ingreso_raw = st.number_input("Valor del Décimo Cuarto Recibido ($)", min_value=0.0, value=val_ing if val_ing > 0 else None, placeholder="0.00", step=10.0, format="%.2f")
            with c2:
                st.write("<br>", unsafe_allow_html=True)
                if st.form_submit_button("💾 Actualizar", type="primary", use_container_width=True):
                    st.session_state.ingresos[periodo_actual] = nuevo_ingreso_raw if nuevo_ingreso_raw is not None else 0.0
                    with st.spinner("Sincronizando... ⏳"):
                        guardar_datos_en_nube()
                    st.rerun()

    st.write("<hr style='border: none; height: 1px; background: #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📝 LISTADO DE GASTOS Y PAGOS</h4>", unsafe_allow_html=True)

    # ====================================================
    # FORMULARIO COMPACTO DE NUEVO GASTO
    # ====================================================
    with st.expander("➕ Ingresar Nueva Programación Fija", expanded=False):
        with st.form(f"form_nuevo_gasto_{periodo_actual}", clear_on_submit=True):
            c1, c2, c3, c4, c_btn = st.columns([2.5, 1.5, 1.5, 1.5, 1.5])
            with c1: nombre_gasto = st.text_input("Descripción")
            with c2: monto_prog_raw = st.number_input("Monto ($)", min_value=0.0, value=None, placeholder="0", step=10.0)
            with c3: comision_prog_raw = st.number_input("Comisión ($)", min_value=0.0, value=None, placeholder="0", step=1.0)
            with c4: iva_prog_raw = st.number_input("IVA ($)", min_value=0.0, value=None, placeholder="0", step=0.1)
            with c_btn: 
                st.write("<br>", unsafe_allow_html=True)
                if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
                    if nombre_gasto != "":
                        nuevo_id = f"G-{len(st.session_state.gastos_fijos[periodo_actual]) + 1}_{int(time.time())}"
                        monto_p = monto_prog_raw if monto_prog_raw is not None else 0.0
                        comis_p = comision_prog_raw if comision_prog_raw is not None else 0.0
                        iva_p = iva_prog_raw if iva_prog_raw is not None else 0.0
                        
                        nueva_fila = pd.DataFrame([{'ID': nuevo_id, 'Gasto': nombre_gasto, 'Monto_Programado': monto_p, 'Comision_Prog': comis_p, 'IVA_Prog': iva_p, 'Estado': 'Pendiente'}])
                        st.session_state.gastos_fijos[periodo_actual] = pd.concat([st.session_state.gastos_fijos[periodo_actual], nueva_fila], ignore_index=True)
                        with st.spinner("Sincronizando... ⏳"):
                            guardar_datos_en_nube()
                        st.rerun()

    df_prog = st.session_state.gastos_fijos[periodo_actual]
    df_pagos = st.session_state.pagos_reales[periodo_actual]

    if not df_prog.empty:
        # ==========================================
        # DISEÑO DE LISTA EN UNA SOLA FILA
        # ==========================================
        for index, row in df_prog.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4.5, 2, 1.5, 1.5])
                
                with c1:
                    st.markdown(f"**🔹 {row['Gasto']}**<br><span style='color:#64748B; font-size:12px;'>Prog: **${float(row['Monto_Programado']):.2f}** | Com: **${float(row['Comision_Prog']):.2f}** | IVA: **${float(row['IVA_Prog']):.2f}**</span>", unsafe_allow_html=True)
                
                with c2:
                    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
                    if row['Estado'] == 'Pagado':
                        st.markdown('<span class="estado-pagado">✅ PAGADO</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="estado-pendiente">🔴 PENDIENTE</span>', unsafe_allow_html=True)
                        
                with c3:
                    st.markdown("<div style='margin-top: 3px;'></div>", unsafe_allow_html=True)
                    if row['Estado'] == 'Pendiente':
                        with st.popover("💳 Pagar", use_container_width=True):
                            with st.form(f"pago_{row['ID']}_{periodo_actual}", clear_on_submit=True):
                                st.info("Modifica los valores si variaron.")
                                fecha_pago = st.date_input("Fecha", date.today())
                                val_pago_defecto = float(row['Monto_Programado']) if float(row['Monto_Programado']) > 0 else None
                                monto_pago = st.number_input("Monto Real ($)", min_value=0.0, value=val_pago_defecto, placeholder="0", step=10.0)
                                val_comis = float(row['Comision_Prog']) if float(row['Comision_Prog']) > 0 else None
                                comision_pago = st.number_input("Comisión Real ($)", min_value=0.0, value=val_comis, placeholder="0", step=1.0)
                                val_iva = float(row['IVA_Prog']) if float(row['IVA_Prog']) > 0 else None
                                iva_pago = st.number_input("IVA Real ($)", min_value=0.0, value=val_iva, placeholder="0", step=0.1)
                                    
                                if st.form_submit_button("✅ Confirmar Pago", type="primary"):
                                    monto_f = monto_pago if monto_pago is not None else 0.0
                                    comis_f = comision_pago if comision_pago is not None else 0.0
                                    iva_f = iva_pago if iva_pago is not None else 0.0
                                    nuevo_pago = pd.DataFrame([{'ID_Gasto': row['ID'], 'Fecha': str(fecha_pago), 'Monto_Pagado': monto_f, 'Comision': comis_f, 'IVA_Comision': iva_f}])
                                    st.session_state.pagos_reales[periodo_actual] = pd.concat([st.session_state.pagos_reales[periodo_actual], nuevo_pago], ignore_index=True)
                                    st.session_state.gastos_fijos[periodo_actual].at[index, 'Estado'] = 'Pagado'
                                    with st.spinner("Registrando... ⏳"):
                                        if guardar_datos_en_nube(): st.rerun()
                
                with c4:
                    st.markdown("<div style='margin-top: 3px;'></div>", unsafe_allow_html=True)
                    with st.popover("⚙️ Editar", use_container_width=True):
                        with st.form(f"edit_{row['ID']}_{periodo_actual}"):
                            e_nom = st.text_input("Gasto", value=row['Gasto'])
                            e_monto = st.number_input("Monto ($)", min_value=0.0, value=float(row['Monto_Programado']), step=10.0)
                            e_com = st.number_input("Comisión ($)", min_value=0.0, value=float(row['Comision_Prog']), step=1.0)
                            e_iva = st.number_input("IVA ($)", min_value=0.0, value=float(row['IVA_Prog']), step=0.1)
                            
                            if st.form_submit_button("💾 Actualizar Valores"):
                                st.session_state.gastos_fijos[periodo_actual].at[index, 'Gasto'] = e_nom
                                st.session_state.gastos_fijos[periodo_actual].at[index, 'Monto_Programado'] = e_monto
                                st.session_state.gastos_fijos[periodo_actual].at[index, 'Comision_Prog'] = e_com
                                st.session_state.gastos_fijos[periodo_actual].at[index, 'IVA_Prog'] = e_iva
                                with st.spinner("Actualizando... ⏳"):
                                    guardar_datos_en_nube()
                                st.rerun()
                        if st.button("🗑️ Borrar", key=f"del_{row['ID']}_{periodo_actual}"):
                            st.session_state.gastos_fijos[periodo_actual] = st.session_state.gastos_fijos[periodo_actual][st.session_state.gastos_fijos[periodo_actual]['ID'] != row['ID']].reset_index(drop=True)
                            with st.spinner("Borrando... ⏳"):
                                guardar_datos_en_nube()
                            st.rerun()
    else:
        st.info("Sin registros. Empieza a programar tus gastos arriba.")

    # ====================================================
    # DASHBOARD INFERIOR: RESUMEN DE SALDOS
    # ====================================================
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>📈 KPIS DE SALDOS Y FLUJO</h4>", unsafe_allow_html=True)
    
    total_programado = df_prog['Monto_Programado'].astype(float).sum() + df_prog['Comision_Prog'].astype(float).sum() + df_prog['IVA_Prog'].astype(float).sum()
    total_pagos_puros = df_pagos['Monto_Pagado'].astype(float).sum()
    total_comisiones = df_pagos['Comision'].astype(float).sum() + df_pagos['IVA_Comision'].astype(float).sum()
    total_salida_real = total_pagos_puros + total_comisiones
    saldo_restante = float(st.session_state.ingresos[periodo_actual]) - total_salida_real
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">PRESUPUESTO BASE</div><div class="kpi-valor" style="color:#16A34A;">${float(st.session_state.ingresos[periodo_actual]):,.2f}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">TOTAL PROGRAMADO</div><div class="kpi-valor">${total_programado:,.2f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">GASTO REAL EJECUTADO</div><div class="kpi-valor" style="color:#DC2626;">${total_salida_real:,.2f}</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">SALDO RESTANTE</div><div class="kpi-valor" style="color:{"#0F172A" if saldo_restante >= 0 else "#DC2626"};">${saldo_restante:,.2f}</div></div>', unsafe_allow_html=True)
