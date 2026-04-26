import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(page_title="Estrategia Marriott", layout="wide")

# Estilo CSS personalizado para la tabla tipo corporativa
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Título y encabezado
st.title(" Marriott International: Cobertura de riesgo cambiario")
st.markdown("### Simulador de estrategias y evaluación de escenarios (MXN/USD)")
st.divider()

# 3. Barra lateral - Parámetros de entrada
st.sidebar.header("⚙️ Parámetros de la estrategia")
exposicion_mxn = 384_000_000

# Inputs de precios
f0 = st.sidebar.number_input("Precio pactado en futuros (F0)", value=17.60)
k = st.sidebar.number_input("Strike de opción PUT (K)", value=17.35)
prima_total_usd = st.sidebar.number_input("Costo total de la prima (USD)", value=318443)

st.sidebar.divider()
st.sidebar.header("📈 Escenarios de estrés")
tc_bajista = st.sidebar.slider("Escenario bajista (peso fuerte)", 15.0, 17.5, 16.50)
tc_normal = st.sidebar.slider("Escenario normal (proyectado)", 17.0, 18.0, 17.60)
tc_alcista = st.sidebar.slider("Escenario alcista (dólar caro)", 18.0, 21.0, 18.50)

# 4. Cálculos financieros
def calcular_resultados(tc):
    mercado_usd = exposicion_mxn / tc
    # Estrategia opciones (PUT)
    if tc > k: # El seguro se activa (peso débil)
        neto_usd = (exposicion_mxn / k) - prima_total_usd
        payoff_derivado = (exposicion_mxn / k) - mercado_usd
    else: # El seguro NO se activa (peso fuerte)
        neto_usd = (exposicion_mxn / tc) - prima_total_usd
        payoff_derivado = 0
    return round(mercado_usd, 2), round(payoff_derivado, 2), round(neto_usd, 2)

# Datos para la tabla
escenarios = ["Bajista", "Normal", "Alcista"]
tcs = [tc_bajista, tc_normal, tc_alcista]
data_tabla = []

for esc, tc in zip(escenarios, tcs):
    merc, pay, neto = calcular_resultados(tc)
    data_tabla.append({
        "Escenario": esc,
        "TC": tc,
        "Mercado (sin cobertura)": merc,
        "Derivados (payoff)": pay,
        "Primas": -prima_total_usd,
        "Neto (USD)": neto
    })

df_resumen = pd.DataFrame(data_tabla)

# 5. Visualización: Tabla de resumen de resultados
st.subheader("5. Resumen de resultados (consolidado en USD)")
# Formatear la tabla para que se vea como dinero
df_display = df_resumen.copy()
for col in ["Mercado (sin cobertura)", "Derivados (payoff)", "Primas", "Neto (USD)"]:
    df_display[col] = df_display[col].apply(lambda x: f"${x:,.2f}")

st.table(df_display.set_index("Escenario"))

# 6. Gráfica interactiva de efectividad (payoff)
st.divider()
st.subheader("📊 Gráfica de efectividad de la cobertura")

# Generar rango de TCs para la curva
tc_range = np.linspace(15.5, 20.0, 100)
y_spot = exposicion_mxn / tc_range
y_put = np.where(tc_range > k, (exposicion_mxn / k) - prima_total_usd, (exposicion_mxn / tc_range) - prima_total_usd)
y_fut = np.full_like(tc_range, (exposicion_mxn / f0))

fig = go.Figure()
fig.add_trace(go.Scatter(x=tc_range, y=y_spot, name="Sin cobertura (spot)", line=dict(color="#94a3b8", dash="dash")))
fig.add_trace(go.Scatter(x=tc_range, y=y_fut, name="Estrategia 1: Futuros", line=dict(color="#ef4444", width=2)))
fig.add_trace(go.Scatter(x=tc_range, y=y_put, name="Estrategia 2: Opciones PUT", line=dict(color="#004b8d", width=4)))

fig.update_layout(
    xaxis_title="Tipo de cambio (MXN/USD)",
    yaxis_title="Ingreso neto final (USD)",
    hovermode="x unified",
    template="plotly_white",
    height=500
)
st.plotly_chart(fig, width="stretch")

# 7. Fórmulas financieras
with st.expander("📝 Ver fórmulas financieras aplicadas"):
    st.latex(r"Ingreso_{Spot} = \frac{Nominal}{S_T}")
    st.latex(r"Ingreso_{Opciones} = \left( \frac{Nominal}{\min(S_T, K)} \right) - Prima")
    st.markdown("""
    * Donde **S_T** es el tipo de cambio al vencimiento.
    * Si **S_T > K**, ejercemos el derecho de vender al strike (seguro).
    * Si **S_T < K**, aprovechamos el mercado y solo perdemos la prima.
    """)