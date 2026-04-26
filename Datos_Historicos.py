import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Descarga de datos históricos (últimos 2 años)
# El ticker 'MXN=X' representa USD/MXN
ticker = "MXN=X"
data = yf.download(ticker, period="2y", interval="1d")

# 2. Limpieza y Cálculo de Rendimientos Logarítmicos
data['Return'] = np.log(data['Close'] / data['Close'].shift(1))

# 3. Cálculos Estadísticos
volatilidad_diaria = data['Return'].std()
volatilidad_anualizada = volatilidad_diaria * np.sqrt(252)
tendencia_promedio = data['Return'].mean() * 252

print(f"Volatilidad Anualizada: {volatilidad_anualizada:.2%}")
print(f"Tendencia Anualizada (Mean Return): {tendencia_promedio:.2%}")

# 4. Visualización de Tendencia
plt.figure(figsize=(12,6))
plt.plot(data['Close'], color="#8d1300") 
plt.title('Evolución Histórica del Tipo de Cambio MXN/USD (2 años)')
plt.xlabel('Fecha')
plt.ylabel('Precio de Cierre')
plt.grid(True, alpha=0.3)
plt.show()