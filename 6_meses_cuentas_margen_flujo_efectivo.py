import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 1. SUPUESTOS DEL MERCADO (CME)
tamano_contrato = 500000 # MXN
margen_inicial = 1500 # USD
margen_mantenimiento = 1200 # USD


#  datos de hace 6 meses
data = yf.download("MXN=X", period="6mo", interval="1d")
df = pd.DataFrame(data['Close'].dropna())
df.columns = ['Precio_Cierre']

# Calcular liquidación diaria para posición CORTA
# Si el precio sube, perdemos si baja, ganamos
df['Liquidacion_Diaria_MXN'] = (df['Precio_Cierre'].shift(1) - df['Precio_Cierre']) * tamano_contrato

# liquidación a USD para la cuenta de margen (aproximación usando el spot del día)
df['Liquidacion_Diaria_USD'] = df['Liquidacion_Diaria_MXN'] / df['Precio_Cierre']
df.fillna(0, inplace=True)

# 3. SIMULACIÓN DE LA CUENTA DE MARGEN
saldo = [margen_inicial]
llamadas_margen = [0]

for i in range(1, len(df)):
    liq_diaria = df['Liquidacion_Diaria_USD'].iloc[i]
    nuevo_saldo = saldo[-1] + liq_diaria
    
    # Revisar si hay Margin Call
    if nuevo_saldo < margen_mantenimiento:
        llamada = margen_inicial - nuevo_saldo
        llamadas_margen.append(llamada)
        saldo.append(margen_inicial) # Se restituye el margen
    else:
        llamadas_margen.append(0)
        saldo.append(nuevo_saldo)

df['Saldo_Cuenta_USD'] = saldo
df['Llamada_a_Margen_USD'] = llamadas_margen

df.to_excel("Cuenta_Margen_Retrospectiva_V2.xlsx")


#GRÁFICOS

# Gráfica 1: Saldo vs Niveles de Margen
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Saldo_Cuenta_USD'], color='#004b8d', linewidth=2, label='Saldo de cuenta de margen')
plt.axhline(y=margen_inicial, color='gray', linestyle='--', label='Margen inicial ($1,500 USD)')
plt.axhline(y=margen_mantenimiento, color='#d9534f', linestyle='-', linewidth=2, label='Margen de mantenimiento ($1,200 USD)')

# Formato Gráfica 1
plt.title('Cuenta margen (Últimos 6 meses)', fontsize=14, fontweight='bold')
plt.ylabel('Saldo en USD', fontsize=12)
plt.xlabel('Fecha', fontsize=12)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

plt.legend(loc='upper left') 

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("Grafica_1_Saldo_Margen.png", dpi=300) 
plt.show()

# Gráfica 2: Llamadas a Margen (Salidas de Efectivo)
plt.figure(figsize=(12, 4))
plt.bar(df.index, df['Llamada_a_Margen_USD'], color='#8b0000', label='Monto de llamada a margen (USD)')

plt.title('Llamadas a margen', fontsize=14, fontweight='bold')
plt.ylabel('Flujo de salida (USD)', fontsize=12)
plt.xlabel('Fecha', fontsize=12)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.legend(loc='upper right')
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig("Grafica_2_Llamadas_Margen.png", dpi=300)
plt.show()

