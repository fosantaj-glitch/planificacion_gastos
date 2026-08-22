import streamlit as st
import pandas as pd
from datetime import date
import requests
import json
import time

# Configuración de la página
st.set_page_config(page_title="Control de Gastos", layout="wide")

# --- SISTEMA DE LOGIN ---
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and \
           st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            st.session_state["usuario_actual"] = st.session_state["username"] 
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 Acceso al Control Financiero")
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Ingresar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 Acceso al Control Financiero")
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Ingresar", on_click=password_entered)
        st.error("😕 Usuario o contraseña incorrectos")
        return False
    return True

# --- FUNCIONES DE BASE DE DATOS (Apps Script) ---
# PEGA AQUÍ TU ENLACE DE APPS SCRIPT
URL_WEB_APP = "https://script.google.com/macros/s/AKfycbx9lOCIm2IZNuDeLl8xmBL8QSR5sekd12Ngx3cELrNvYYefhuVJN6VhgBdezNcfiijo/exec"

def estructurar_datos_para_guardar():
    filas = []
    # 1. Guardar Ingresos
    for periodo, monto in st.session_state.ingresos.items():
        filas.append({'Periodo': periodo, 'Categoria': 'Ingreso', 'ID_Relacionado': '', 'Descripcion': 'Total Recibido', 'Monto': monto, 'Fecha': '', 'Comision': 0, 'IVA': 0})
    
    # 2. Guardar Gastos Fijos
    for periodo, df_prog in st.session_state.gastos_fijos.items():
        for _, row in df_prog.iterrows():
            filas.append({'Periodo': periodo, 'Categoria': 'Gasto Programado', 'ID_Relacionado': row['ID'], 'Descripcion': row['Gasto'], 'Monto': row['Monto_Programado'], 'Fecha': '', 'Comision': 0, 'IVA': 0})
            
    # 3. Guardar Pagos Reales
    for periodo, df_pagos in st.session_state.pagos_reales.items():
        for _, row in df_pagos.iterrows():
            filas.append({'Periodo': periodo, 'Categoria': 'Pago Real', 'ID_Relacionado': row['ID_Gasto'], 'Descripcion': 'Pago registrado', 'Monto': row['Monto_Pagado'], 'Fecha': row['Fecha'], 'Comision': row['Comision'], 'IVA': row['IVA_Comision']})
            
    return pd.DataFrame(filas)

def guardar_datos_en_nube():
    df_consolidado = estructurar_datos_para_guardar()
    try:
        df_clean = df_consolidado.fillna("").astype(str)
        data_list = [df_clean.columns.tolist()]
        for row in df_clean.itertuples(index=False, name=None):
            data_list.append(list(row))
        payload = {"action": "overwrite", "data": data_list}
        res = requests.post(URL_WEB_APP, json=payload, allow_redirects=True)
        if res.status_code not in [200, 201]:
            st.error(f"⚠️ Google respondió con error: {res.status_code}")
            return False
        return True
    except Exception as e:
        st.error(f"⚠️ Error al enviar datos: {e}")
        return False

# --- EJECUCIÓN DE LA APLICACIÓN ---
if check_password():
    st.sidebar.success(f"Sesión iniciada como: {st.session_state['usuario_actual']}")
    
    st.title("📊 Control de Gastos y Pagos Reales")
    st.info('El sistema está conectado a tu método de Apps Script.')

    # Inicialización local 
    if 'ingresos' not in st.session_state:
        st.session_state.ingresos = {'Mes Regular': 0.0, 'Décimo Tercero': 0.0, 'Décimo Cuarto': 0.0}
    if 'gastos_fijos' not in st.session_state:
        estructura_base = pd.DataFrame(columns=['ID', 'Gasto', 'Monto_Programado'])
        st.session_state.gastos_fijos = {'Mes Regular': estructura_base.copy(), 'Décimo Tercero': estructura_base.copy(), 'Décimo Cuarto': estructura_base.copy()}
    if 'pagos_reales' not in st.session_state:
        estructura_pagos = pd.DataFrame(columns=['ID_Gasto', 'Fecha', 'Monto_Pagado', 'Comision', 'IVA_Comision'])
        st.session_state.pagos_reales = {'Mes Regular': estructura_pagos.copy(), 'Décimo Tercero': estructura_pagos.copy(), 'Décimo Cuarto': estructura_pagos.copy()}
    if 'decimo_tercero_meses' not in st.session_state:
        st.session_state.decimo_tercero_meses = {
            'Diciembre': 0.0, 'Enero': 0.0, 'Febrero': 0.0, 'Marzo': 0.0, 
            'Abril': 0.0, 'Mayo': 0.0, 'Junio': 0.0, 'Julio': 0.0, 
            'Agosto': 0.0, 'Septiembre': 0.0, 'Octubre': 0.0, 'Noviembre': 0.0
        }

    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Guardar TODO en Google Drive", type="primary"):
        with st.spinner("Guardando en la nube... ⏳"):
            if guardar_datos_en_nube():
                st.sidebar.success("✅ ¡Guardado con éxito!")
                time.sleep(2)
                st.rerun()

    # --- NAVEGACIÓN ---
    periodo_actual = st.radio("Selecciona el periodo a gestionar:", ['Mes Regular', 'Décimo Tercero', 'Décimo Cuarto'], horizontal=True)
    st.markdown("---")
    st.header(f"Gestión de: {periodo_actual}")

    # --- 1. CONFIGURACIÓN DE INGRESOS ---
    if periodo_actual == 'Décimo Tercero':
        with st.expander("📅 Calculadora Décimo Tercer Sueldo (Ingresa tus salarios)", expanded=True):
            st.write("Ingresa todo lo percibido desde el 1 de dic. hasta el 30 de nov:")
            cols = st.columns(4)
            meses_lista = list(st.session_state.decimo_tercero_meses.keys())
            
            for i, mes in enumerate(meses_lista):
                with cols[i % 4]:
                    val_actual = st.session_state.decimo_tercero_meses[mes]
                    # Ceros automáticos para los meses
                    val_ingresado_raw = st.number_input(f"{mes}", value=val_actual if val_actual > 0 else None, placeholder="0", step=50.0)
                    st.session_state.decimo_tercero_meses[mes] = val_ingresado_raw if val_ingresado_raw is not None else 0.0
            
            # Cálculo
            total_percibido = sum(st.session_state.decimo_tercero_meses.values())
            decimo_calculado = total_percibido / 12 if total_percibido > 0 else 0.0
            
            # Actualizamos el ingreso de este periodo
            st.session_state.ingresos['Décimo Tercero'] = decimo_calculado
            
            st.info(f"**Total Percibido:** ${total_percibido:.2f} | **Décimo Tercero Calculado:** ${decimo_calculado:.2f}")

    else:
        col_ing, _ = st.columns([1, 2])
        with col_ing:
            val_ing = st.session_state.ingresos[periodo_actual]
            # Cero automático para el ingreso inicial
            nuevo_ingreso_raw = st.number_input("Total Recibido (Ingreso Inicial):", min_value=0.0, value=val_ing if val_ing > 0 else None, placeholder="0", step=50.0)
            st.session_state.ingresos[periodo_actual] = nuevo_ingreso_raw if nuevo_ingreso_raw is not None else 0.0

    st.markdown("### 📝 Programación de Gastos Fijos vs Pagos Reales")

    # --- 2. REGISTRO DE GASTOS FIJOS ---
    with st.expander("➕ Agregar Nuevo Gasto Fijo", expanded=False):
        with st.form(f"form_gasto_{periodo_actual}"):
            c1, c2 = st.columns(2)
            with c1:
                nombre_gasto = st.text_input("Nombre del Gasto Fijo")
            with c2:
                # Cero automático para el nuevo gasto programado
                monto_prog_raw = st.number_input("Monto Programado ($)", min_value=0.0, value=None, placeholder="0", step=10.0)
                monto_prog = monto_prog_raw if monto_prog_raw is not None else 0.0
            
            if st.form_submit_button("Guardar Gasto Localmente"):
                if nombre_gasto != "":
                    nuevo_id = f"G-{len(st.session_state.gastos_fijos[periodo_actual]) + 1}"
                    nueva_fila = pd.DataFrame([{'ID': nuevo_id, 'Gasto': nombre_gasto, 'Monto_Programado': monto_prog}])
                    st.session_state.gastos_fijos[periodo_actual] = pd.concat([st.session_state.gastos_fijos[periodo_actual], nueva_fila], ignore_index=True)
                    st.success("Gasto añadido.")
                    st.rerun()

    # --- 3. VISTA PARALELA ---
    df_prog = st.session_state.gastos_fijos[periodo_actual]
    df_pagos = st.session_state.pagos_reales[periodo_actual]

    if not df_prog.empty:
        for index, row in df_prog.iterrows():
            st.markdown(f"#### 🔹 {row['Gasto']} (Programado: ${row['Monto_Programado']:.2f})")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.form(f"pago_form_{row['ID']}_{periodo_actual}", clear_on_submit=True):
                    st.write("**Registrar Pago**")
                    c_f, c_m = st.columns(2)
                    with c_f:
                        fecha_pago = st.date_input("Fecha", date.today())
                        # Cero automático para la comisión
                        comision_raw = st.number_input("Comisión ($)", min_value=0.0, value=None, placeholder="0", step=1.0)
                        comision = comision_raw if comision_raw is not None else 0.0
                    with c_m:
                        # Para el pago, asume por defecto lo programado. Si estaba en cero, muestra el placeholder.
                        val_pago_defecto = row['Monto_Programado'] if row['Monto_Programado'] > 0 else None
                        monto_pago_raw = st.number_input("Monto a Pagar ($)", min_value=0.0, value=val_pago_defecto, placeholder="0", step=10.0)
                        monto_pago = monto_pago_raw if monto_pago_raw is not None else 0.0
                        
                        # Cero automático para el IVA
                        iva_raw = st.number_input("IVA Comisión ($)", min_value=0.0, value=None, placeholder="0", step=0.1)
                        iva_comision = iva_raw if iva_raw is not None else 0.0
                    
                    if st.form_submit_button("✅ Confirmar Pago"):
                        nuevo_pago = pd.DataFrame([{'ID_Gasto': row['ID'], 'Fecha': str(fecha_pago), 'Monto_Pagado': monto_pago, 'Comision': comision, 'IVA_Comision': iva_comision}])
                        st.session_state.pagos_reales[periodo_actual] = pd.concat([st.session_state.pagos_reales[periodo_actual], nuevo_pago], ignore_index=True)
                        st.success("Pago registrado.")
                        st.rerun()
            with col2:
                st.write("**Historial de Pagos Reales**")
                pagos_gasto = df_pagos[df_pagos['ID_Gasto'] == row['ID']]
                if not pagos_gasto.empty:
                    st.dataframe(pagos_gasto[['Fecha', 'Monto_Pagado', 'Comision', 'IVA_Comision']], hide_index=True, use_container_width=True)
                    total_acumulado = pagos_gasto['Monto_Pagado'].sum() + pagos_gasto['Comision'].sum() + pagos_gasto['IVA_Comision'].sum()
                    st.info(f"**Acumulado Pagado:** ${total_acumulado:.2f}")
                else:
                    st.warning("Aún no se han registrado pagos para este rubro.")
            st.markdown("---")

        # --- 4. RESUMEN MATEMÁTICO FINAL ---
        st.header("📈 Resumen de Saldos")
        total_programado = df_prog['Monto_Programado'].sum()
        total_pagos_puros = df_pagos['Monto_Pagado'].sum()
        total_comisiones = df_pagos['Comision'].sum() + df_pagos['IVA_Comision'].sum()
        total_salida_real = total_pagos_puros + total_comisiones
        saldo_restante = st.session_state.ingresos[periodo_actual] - total_salida_real
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Ingreso Total", f"${st.session_state.ingresos[periodo_actual]:.2f}")
        m2.metric("Total Programado", f"${total_programado:.2f}")
        m3.metric("Total Salida Real", f"${total_salida_real:.2f}")
        m4.metric("Saldo Restante", f"${saldo_restante:.2f}", delta=float(saldo_restante), delta_color="normal")
