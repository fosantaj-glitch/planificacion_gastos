import streamlit as st
import pandas as pd
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Control de Gastos", layout="wide")

st.title("📊 Control de Gastos y Pagos Reales")
st.info('Este es el sistema de control basado en tu archivo "PROGRAMACION".')

# --- INICIALIZACIÓN DE BASE DE DATOS EN MEMORIA ---
if 'ingresos' not in st.session_state:
    # Ingresos configurables por periodo
    st.session_state.ingresos = {
        'Mes Regular': 1000.0,
        'Décimo Tercero': 1000.0,
        'Décimo Cuarto': 450.0
    }

if 'gastos_fijos' not in st.session_state:
    # Estructura: Periodo -> DataFrame de Programación
    estructura_base = pd.DataFrame(columns=['ID', 'Gasto', 'Monto_Programado'])
    st.session_state.gastos_fijos = {
        'Mes Regular': estructura_base.copy(),
        'Décimo Tercero': estructura_base.copy(),
        'Décimo Cuarto': estructura_base.copy()
    }

if 'pagos_reales' not in st.session_state:
    # Estructura: Periodo -> DataFrame de Pagos Reales
    estructura_pagos = pd.DataFrame(columns=['ID_Gasto', 'Fecha', 'Monto_Pagado', 'Comision', 'IVA_Comision'])
    st.session_state.pagos_reales = {
        'Mes Regular': estructura_pagos.copy(),
        'Décimo Tercero': estructura_pagos.copy(),
        'Décimo Cuarto': estructura_pagos.copy()
    }

# --- NAVEGACIÓN ---
periodo_actual = st.radio("Selecciona el periodo a gestionar:", 
                          ['Mes Regular', 'Décimo Tercero', 'Décimo Cuarto'], 
                          horizontal=True)

st.markdown("---")
st.header(f"Gestión de: {periodo_actual}")

# --- 1. CONFIGURACIÓN DE INGRESOS ---
col_ing, _ = st.columns([1, 2])
with col_ing:
    nuevo_ingreso = st.number_input("Total Recibido (Ingreso Inicial):", 
                                    min_value=0.0, 
                                    value=st.session_state.ingresos[periodo_actual], 
                                    step=50.0)
    st.session_state.ingresos[periodo_actual] = nuevo_ingreso

st.markdown("### 📝 Programación de Gastos Fijos vs Pagos Reales")

# --- 2. REGISTRO DE GASTOS FIJOS (PROGRAMACIÓN) ---
with st.expander("➕ Agregar Nuevo Gasto Fijo a la Programación", expanded=False):
    with st.form(f"form_gasto_{periodo_actual}"):
        c1, c2 = st.columns(2)
        with c1:
            nombre_gasto = st.text_input("Nombre del Gasto Fijo")
        with c2:
            monto_prog = st.number_input("Monto Programado ($)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Guardar Gasto Fijo"):
            nuevo_id = f"G-{len(st.session_state.gastos_fijos[periodo_actual]) + 1}"
            nueva_fila = pd.DataFrame([{'ID': nuevo_id, 'Gasto': nombre_gasto, 'Monto_Programado': monto_prog}])
            st.session_state.gastos_fijos[periodo_actual] = pd.concat([st.session_state.gastos_fijos[periodo_actual], nueva_fila], ignore_index=True)
            st.success("Gasto programado añadido.")
            st.rerun()

# --- 3. VISTA PARALELA (PROGRAMACIÓN Y PAGOS REALES) ---
df_prog = st.session_state.gastos_fijos[periodo_actual]
df_pagos = st.session_state.pagos_reales[periodo_actual]

if not df_prog.empty:
    for index, row in df_prog.iterrows():
        st.markdown(f"#### 🔹 {row['Gasto']} (Programado: ${row['Monto_Programado']:.2f})")
        
        col1, col2 = st.columns([1, 1])
        
        # Columna 1: Botón para realizar pago
        with col1:
            with st.form(f"pago_form_{row['ID']}_{periodo_actual}", clear_on_submit=True):
                st.write("**Registrar Pago**")
                c_f, c_m = st.columns(2)
                with c_f:
                    fecha_pago = st.date_input("Fecha", date.today())
                    comision = st.number_input("Comisión ($)", min_value=0.0, step=1.0)
                with c_m:
                    monto_pago = st.number_input("Monto a Pagar ($)", min_value=0.0, value=row['Monto_Programado'], step=10.0)
                    iva_comision = st.number_input("IVA Comisión ($)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("✅ Confirmar Pago"):
                    nuevo_pago = pd.DataFrame([{
                        'ID_Gasto': row['ID'],
                        'Fecha': str(fecha_pago),
                        'Monto_Pagado': monto_pago,
                        'Comision': comision,
                        'IVA_Comision': iva_comision
                    }])
                    st.session_state.pagos_reales[periodo_actual] = pd.concat([st.session_state.pagos_reales[periodo_actual], nuevo_pago], ignore_index=True)
                    st.success("Pago registrado con éxito.")
                    st.rerun()
                    
        # Columna 2: Tabla paralela de pagos realizados para este gasto
        with col2:
            st.write("**Historial de Pagos Reales**")
            pagos_gasto = df_pagos[df_pagos['ID_Gasto'] == row['ID']]
            if not pagos_gasto.empty:
                # Mostrar tabla
                st.dataframe(pagos_gasto[['Fecha', 'Monto_Pagado', 'Comision', 'IVA_Comision']], hide_index=True, use_container_width=True)
                
                # Calcular acumulado de este gasto
                total_acumulado = pagos_gasto['Monto_Pagado'].sum() + pagos_gasto['Comision'].sum() + pagos_gasto['IVA_Comision'].sum()
                st.info(f"**Acumulado Pagado (incl. comisiones e IVA):** ${total_acumulado:.2f}")
            else:
                st.warning("Aún no se han registrado pagos para este rubro.")
                
        st.markdown("---")

    # --- 4. RESUMEN MATEMÁTICO FINAL ---
    st.header("📈 Resumen de Saldos")
    
    # Cálculos
    total_programado = df_prog['Monto_Programado'].sum()
    
    total_pagos_puros = df_pagos['Monto_Pagado'].sum()
    total_comisiones = df_pagos['Comision'].sum() + df_pagos['IVA_Comision'].sum()
    total_salida_real = total_pagos_puros + total_comisiones
    
    saldo_restante = st.session_state.ingresos[periodo_actual] - total_salida_real
    
    # Mostrar métricas
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ingreso Total", f"${st.session_state.ingresos[periodo_actual]:.2f}")
    m2.metric("Total Programado", f"${total_programado:.2f}")
    m3.metric("Total Salida Real (con comisiones)", f"${total_salida_real:.2f}")
    m4.metric("Saldo Restante", f"${saldo_restante:.2f}", delta=float(saldo_restante), delta_color="normal")
else:
    st.info("Comienza agregando tus gastos fijos programados en el formulario de arriba.")
