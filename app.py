import streamlit as st
import pandas as pd
from datetime import date
import requests
import json
import time

st.set_page_config(page_title="Control Financiero", layout="wide")

# ==========================================
# 🎨 CSS AVANZADO: DISEÑO ELEGANTE Y PROFESIONAL
# ==========================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stAppViewContainer"] { background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%); }
    .titulo-principal { font-size: 32px !important; font-weight: 800 !important; color: #0F172A !important; text-transform: uppercase; margin-bottom: 0px !important;}
    .subtitulo-marca { font-size: 14px !important; font-weight: 700 !important; color: #D97706 !important; text-transform: uppercase; margin-top: 5px !important;}
    div[data-testid="stForm"] { background-color: #FFFFFF; border-radius: 12px; padding: 25px; box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.04); border: 1px solid #EBE6DF; }
    .kpi-card { background: #FFFFFF; border-radius: 14px; padding: 18px 22px; border: 1px solid #E2E8F0; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03); }
    .kpi-titulo { font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-valor { font-size: 24px; font-weight: 800; color: #0F172A; margin-top: 4px; }
    .estado-pendiente { color: #DC2626; font-weight: bold; background-color: #FEE2E2; padding: 5px 10px; border-radius: 5px; font-size: 14px;}
    .estado-pagado { color: #16A34A; font-weight: bold; background-color: #DCFCE7; padding: 5px 10px; border-radius: 5px; font-size: 14px;}
    .item-gasto { background: #FFFFFF; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 10px; box-shadow: 0px 2px 5px rgba(0,0,0,0.02);}
    </style>
""", unsafe_allow_html=True)

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

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.write("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<p class="titulo-principal" style="text-align:center;">CONTROL FINANCIERO</p>', unsafe_allow_html=True)
            st.markdown('<p class="subtitulo-marca" style="text-align:center;">PROGRAMACIÓN Y PAGOS</p>', unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("#### 🔒 Ingreso Seguro")
                st.text_input("Usuario", key="username")
                st.text_input("Contraseña", type="password", key="password")
                st.form_submit_button("Acceder", on_click=password_entered, use_container_width=True)
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Credenciales incorrectas.")
        return False
    return True

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

# --- EJECUCIÓN APP ---
if check_password():
    
    st.markdown('<p class="titulo-principal">📊 PANEL FINANCIERO</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitulo-marca">Gestión de Presupuesto y Gastos Reales</p>', unsafe_allow_html=True)
    st.write("---")

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

        with st.spinner("Descargando datos desde Google Drive..."):
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

    periodo_actual = st.radio("SELECCIONA EL PERIODO:", ['Mes Regular', 'Décimo Tercero', 'Décimo Cuarto'], horizontal=True)
    st.write("<br>", unsafe_allow_html=True)

    if periodo_actual == 'Décimo Tercero':
        with st.form("form_calculadora_decimo"):
            st.markdown("**📅 Calculadora Décimo Tercer Sueldo (Ingresa tus salarios)**")
            cols = st.columns(4)
            meses_lista = list(st.session_state.decimo_tercero_meses.keys())
            
            for i, mes in enumerate(meses_lista):
                with cols[i % 4]:
                    val_actual = st.session_state.decimo_tercero_meses[mes]
                    val_ingresado_raw = st.number_input(f"{mes}", value=val_actual if val_actual > 0 else None, placeholder="0", step=50.0)
                    st.session_state.decimo_tercero_meses[mes] = val_ingresado_raw if val_ingresado_raw is not None else 0.0
            
            total_percibido = sum(st.session_state.decimo_tercero_meses.values())
            decimo_calculado = total_percibido / 12 if total_percibido > 0 else 0.0
            st.info(f"**Total Percibido:** ${total_percibido:.2f} | **Décimo Tercero Calculado:** ${decimo_calculado:.2f}")

            if st.form_submit_button("💾 Actualizar y Guardar Meses"):
                st.session_state.ingresos['Décimo Tercero'] = decimo_calculado
                with st.spinner("Sincronizando con la nube... ⏳"):
                    if guardar_datos_en_nube():
                        st.success("✅ Guardado automático exitoso.")
                        time.sleep(1.5)
                        st.rerun()
    else:
        with st.form(f"form_ingreso_{periodo_actual}"):
            st.markdown(f"**Ingreso para: {periodo_actual}**")
            val_ing = st.session_state.ingresos[periodo_actual]
            nuevo_ingreso_raw = st.number_input("Total Recibido (Ingreso Inicial):", min_value=0.0, value=val_ing if val_ing > 0 else None, placeholder="0.00", step=50.0, format="%.2f")
            
            if st.form_submit_button("💾 Actualizar Ingreso"):
                st.session_state.ingresos[periodo_actual] = nuevo_ingreso_raw if nuevo_ingreso_raw is not None else 0.0
                with st.spinner("Sincronizando con la nube... ⏳"):
                    if guardar_datos_en_nube():
                        st.success("Ingreso guardado.")
                        time.sleep(1.5)
                        st.rerun()

    st.write("---")
    st.markdown("### 📝 LISTA DE GASTOS PROGRAMADOS")

    with st.expander("➕ Programar Nuevo Gasto Fijo", expanded=False):
        # Mantenemos clear_on_submit=True para que quede en blanco tras guardar
        with st.form(f"form_nuevo_gasto_{periodo_actual}", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1: nombre_gasto = st.text_input("Descripción del Gasto")
            with c2: monto_prog_raw = st.number_input("Monto Principal ($)", min_value=0.0, value=None, placeholder="0", step=10.0)
            with c3: comision_prog_raw = st.number_input("Comisión Estimada ($)", min_value=0.0, value=None, placeholder="0", step=1.0)
            with c4: iva_prog_raw = st.number_input("IVA Estimado ($)", min_value=0.0, value=None, placeholder="0", step=0.1)
            
            if st.form_submit_button("💾 Guardar en Programación"):
                if nombre_gasto != "":
                    nuevo_id = f"G-{len(st.session_state.gastos_fijos[periodo_actual]) + 1}_{int(time.time())}"
                    monto_p = monto_prog_raw if monto_prog_raw is not None else 0.0
                    comis_p = comision_prog_raw if comision_prog_raw is not None else 0.0
                    iva_p = iva_prog_raw if iva_prog_raw is not None else 0.0
                    
                    nueva_fila = pd.DataFrame([{'ID': nuevo_id, 'Gasto': nombre_gasto, 'Monto_Programado': monto_p, 'Comision_Prog': comis_p, 'IVA_Prog': iva_p, 'Estado': 'Pendiente'}])
                    st.session_state.gastos_fijos[periodo_actual] = pd.concat([st.session_state.gastos_fijos[periodo_actual], nueva_fila], ignore_index=True)
                    with st.spinner("Sincronizando con la nube... ⏳"):
                        if guardar_datos_en_nube():
                            st.success("Gasto programado exitosamente.")
                            time.sleep(1.5)
                            st.rerun()

    df_prog = st.session_state.gastos_fijos[periodo_actual]
    df_pagos = st.session_state.pagos_reales[periodo_actual]

    if not df_prog.empty:
        for index, row in df_prog.iterrows():
            st.markdown(f"""
                <div class="item-gasto">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 18px; font-weight: 600; color: #1E293B;">🔹 {row['Gasto']}</span>
                        <span class="{'estado-pagado' if row['Estado'] == 'Pagado' else 'estado-pendiente'}">
                            {'✅ PAGADO' if row['Estado'] == 'Pagado' else '🔴 PENDIENTE'}
                        </span>
                    </div>
                    <div style="color: #64748B; font-size: 14px; margin-top: 5px;">
                        Programado: <b>${float(row['Monto_Programado']):.2f}</b> | Comisión: <b>${float(row['Comision_Prog']):.2f}</b> | IVA: <b>${float(row['IVA_Prog']):.2f}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c_p1, c_p2 = st.columns(2)
            
            with c_p1:
                if row['Estado'] == 'Pendiente':
                    with st.expander(f"💳 Realizar Pago", expanded=False):
                        with st.form(f"pago_{row['ID']}_{periodo_actual}", clear_on_submit=True):
                            st.info("Modifica los valores si el cobro real varió.")
                            fecha_pago = st.date_input("Fecha de Pago", date.today())
                            
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
                                
                                with st.spinner("Registrando en la nube... ⏳"):
                                    if guardar_datos_en_nube():
                                        st.rerun()
            
            with c_p2:
                with st.expander(f"⚙️ Editar / Borrar", expanded=False):
                    with st.form(f"edit_{row['ID']}_{periodo_actual}"):
                        st.write("**Modificar Programación**")
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

                    # El botón de borrar va fuera del form para no chocar con el guardado
                    st.write("")
                    if st.button("🗑️ Eliminar Gasto", key=f"del_{row['ID']}_{periodo_actual}", type="secondary"):
                        # Se filtra la tabla para excluir el ID borrado
                        st.session_state.gastos_fijos[periodo_actual] = st.session_state.gastos_fijos[periodo_actual][st.session_state.gastos_fijos[periodo_actual]['ID'] != row['ID']].reset_index(drop=True)
                        with st.spinner("Borrando registro de la nube... ⏳"):
                            guardar_datos_en_nube()
                        st.rerun()
                        
    else:
        st.info("No hay gastos programados. Empieza agregando uno arriba.")

    st.write("<br><br>", unsafe_allow_html=True)
    
    st.markdown("### 📈 RESUMEN DE SALDOS")
    total_programado = df_prog['Monto_Programado'].astype(float).sum() + df_prog['Comision_Prog'].astype(float).sum() + df_prog['IVA_Prog'].astype(float).sum()
    total_pagos_puros = df_pagos['Monto_Pagado'].astype(float).sum()
    total_comisiones = df_pagos['Comision'].astype(float).sum() + df_pagos['IVA_Comision'].astype(float).sum()
    total_salida_real = total_pagos_puros + total_comisiones
    saldo_restante = float(st.session_state.ingresos[periodo_actual]) - total_salida_real
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">INGRESO INICIAL</div><div class="kpi-valor" style="color:#16A34A;">${float(st.session_state.ingresos[periodo_actual]):.2f}</div></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">TOTAL PROGRAMADO</div><div class="kpi-valor">${total_programado:.2f}</div></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">TOTAL GASTO REAL</div><div class="kpi-valor" style="color:#DC2626;">${total_salida_real:.2f}</div></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="kpi-card"><div class="kpi-titulo">SALDO RESTANTE</div><div class="kpi-valor">${saldo_restante:.2f}</div></div>', unsafe_allow_html=True)
